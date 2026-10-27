"""Stethoscope origin reel - renders a silent 720x1280 30fps MP4 in the style of the reference reel."""
import sys, math, subprocess, time
import numpy as np, cv2
from PIL import Image, ImageDraw
import assets as A
from assets import W, H, ease_out, ease_in, ease_io, ease_back, bounce, lerp, clamp01, blur

FPS = 30

# ------------------------------------------------------------------ compositing helpers
def cam(img, zoom=1.0, dx=0.0, dy=0.0, rot=0.0):
    ih, iw = img.shape[:2]
    s = max(W / iw, H / ih) * zoom
    cx, cy = iw / 2 + dx, ih / 2 + dy
    M = cv2.getRotationMatrix2D((cx, cy), rot, s)
    M[0, 2] += W / 2 - cx; M[1, 2] += H / 2 - cy
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def mblur(img, dx, dy):
    L = int(math.hypot(dx, dy))
    if L < 2: return img
    k = np.zeros((L * 2 + 1, L * 2 + 1), np.float32)
    cv2.line(k, (L - int(dx / 2), L - int(dy / 2)), (L + int(dx / 2), L + int(dy / 2)), 1, 1)
    k /= k.sum()
    return cv2.filter2D(img, -1, k, borderType=cv2.BORDER_REFLECT)

def zoom_blur(img, amt, n=6):
    if amt < .02: return img
    acc = np.zeros_like(img)
    for i in range(n):
        acc += cam(img, 1 + .14 * amt * i / (n - 1))
    return acc / n

def blit(dst, spr, cx, cy, scale=1.0, rot=0.0, alpha=1.0, mb=None, shadow=None, glow=None, sblur=0.0):
    if alpha <= .003: return dst
    if sblur > .3:
        p = int(sblur * 3) + 2
        spr = blur(np.pad(spr, ((p, p), (p, p), (0, 0))), sblur)
    sh, sw = spr.shape[:2]
    pm = spr.copy(); pm[..., :3] *= pm[..., 3:4]
    M = cv2.getRotationMatrix2D((sw / 2, sh / 2), rot, scale)
    M[0, 2] += cx - sw / 2; M[1, 2] += cy - sh / 2
    lay = cv2.warpAffine(pm, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    if mb is not None: lay = mblur(lay, *mb)
    a = lay[..., 3:4] * alpha
    if shadow is not None:
        ox, oy, sb, st = shadow
        sa = blur(lay[..., 3], sb)
        sa = np.roll(np.roll(sa, int(oy), 0), int(ox), 1)
        dst = dst * (1 - (sa * st * alpha)[..., None])
    if glow is not None:
        col, gs, gk = glow
        g = blur(lay[..., 3], gs)
        dst = dst + g[..., None] * np.array(col, np.float32) * gk * alpha
    return dst * (1 - a) + lay[..., :3] * alpha

_tcache = {}
def text(s, fnt, size, color, wght=None, pad=36, shear=0.0, depth=0, depth_col=(110, 8, 8), stroke=0, stroke_col=(0, 0, 0)):
    key = (s, fnt, size, color, wght, shear, depth, stroke)
    if key in _tcache: return _tcache[key]
    f = A.font(fnt, size, wght)
    l, t, r, b = f.getbbox(s, stroke_width=stroke)
    w, h = r - l + pad * 2 + depth, b - t + pad * 2 + depth
    im = Image.new('RGBA', (max(w, 1), max(h, 1)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c255 = tuple(int(c * 255) if isinstance(c, float) else c for c in color)
    for i in range(depth, 0, -1):
        d.text((pad - l + i * .6, pad - t + i), s, font=f, fill=depth_col + (255,), stroke_width=2, stroke_fill=(40, 0, 0, 255))
    d.text((pad - l, pad - t), s, font=f, fill=c255 + (255,), stroke_width=stroke, stroke_fill=stroke_col + (255,))
    arr = np.asarray(im).astype(np.float32) / 255
    if depth:  # top highlight on face
        g = np.linspace(1.25, .85, arr.shape[0], dtype=np.float32)[:, None, None]
        arr[..., :3] = np.clip(arr[..., :3] * g, 0, 1)
    if shear:
        hh, ww = arr.shape[:2]; ex = int(abs(shear) * hh)
        M = np.float32([[1, -shear, ex if shear > 0 else 0], [0, 1, 0]])
        arr = cv2.warpAffine(arr, M, (ww + ex, hh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    _tcache[key] = arr
    return arr

def text_width(s, fnt, size):
    l, t, r, b = A.font(fnt, size).getbbox(s); return r - l

# ------------------------------------------------------------------ assets
t0 = time.time()
LAB_E, LAB_B = A.lab(False), A.lab(True)
STONE = A.stone_wall()
STETH = A.wooden_stethoscope()
P_YOUNG, P_OLD = A.portrait(False), A.portrait(True)
WARD, LISTEN = A.ward(False), A.ward(True)
TABLE = A.wood_table()
ORANGE = A.orange_paper()
WSHADOW = blur(A.window_shadow(), 12)
CHALK = A.chalkboard()
NAVY = A.navy()
BLUE = A.grid_paper((.80, .84, .88), (.63, .69, .76), 40, .12, 5)
WHITE = A.white_paper()
MODERN = A.clinic_fisheye()
EVO = [A.paper_tube(), A.wooden_stethoscope(), A.binaural(), A.binaural(modern=True)]
RED_T = A.torn_sheet((.55, .07, .09), H, W, ((-20, 600), (600, -20)), False, 3)
BLUE_T = A.torn_sheet((.07, .11, .30), H, W, ((-20, 930), (760, 1330)), True, 9)
GRAIN = [(np.random.default_rng(i).normal(0, 1, (H, W, 1)).astype(np.float32) * .028) for i in range(8)]
VIG = A.vignette(H, W, .35, 2.5)
print('assets', round(time.time() - t0, 1), 's', flush=True)

def polaroid(photo, label):
    pw, ph = 330, 400
    card = np.ones((ph, pw, 4), np.float32); card[..., :3] = np.array([.96, .95, .92])
    card[..., :3] *= (1 - .05 * A.fbm(ph, pw, (80, 20), 2))[..., None]
    ph_img = cv2.resize(photo, (290, 290), interpolation=cv2.INTER_AREA)
    card[20:310, 20:310, :3] = ph_img
    card[20:310, 20:310, :3] *= .97
    lab = text(label, 'oswald', 32, (15, 15, 15), wght=700, pad=4)
    lh, lw = lab.shape[:2]
    y0, x0 = 352 - lh // 2, pw // 2 - lw // 2
    a = lab[..., 3:4]
    card[y0:y0 + lh, x0:x0 + lw, :3] = card[y0:y0 + lh, x0:x0 + lw, :3] * (1 - a) + lab[..., :3] * a
    return card

def bw(img): g = img.mean(2, keepdims=True); return np.repeat(g, 3, 2)

POL_YOUNG = polaroid(P_YOUNG, 'René Laennec')
POL_WARD = polaroid(bw(cv2.resize(WARD[480:1240, 40:800], (420, 420))), 'René Laennec')
POL_OLD = polaroid(P_OLD, 'René Laennec')

def paper_roll_sprite(p):
    """Sheet of paper rolling up from the bottom into a tube (p 0..1)."""
    pw, fh = 380, 470
    r = 10 + 26 * p
    flat = (1 - p) * fh
    h = int(fh + 2 * 36 + 20); w = pw + 20
    out = np.zeros((h, w, 4), np.float32)
    y0 = 20; y1 = int(y0 + flat)
    if y1 > y0:
        out[y0:y1, 10:10 + pw, :3] = np.array([.93, .88, .76]) * (1 - .06 * PAPER_TEX[:y1 - y0, :pw])[..., None]
        out[y0:y1, 10:10 + pw, 3] = 1
    yy = np.arange(h)[:, None].astype(np.float32)
    u = (yy - y1) / r
    inside = np.abs(u) <= 1
    shade = np.sqrt(np.clip(1 - u ** 2, 0, 1))
    light = .55 + .45 * shade + .25 * np.exp(-((u + .45) / .2) ** 2)
    band = np.zeros((h, w, 4), np.float32)
    band[..., :3] = (np.array([.93, .88, .76])[None, None] * light[..., None])
    band[..., 3] = np.clip((r - np.abs(yy - y1)) * .8, 0, 1)[:, 0][:, None] * np.ones((1, w))
    band[:, :10] = 0; band[:, 10 + pw:] = 0
    m = band[..., 3:4]
    out = out * (1 - m) + band * m
    out[..., 3] = np.maximum(out[..., 3], band[..., 3])
    return out
PAPER_TEX = A.fbm(480, 380, (60, 15, 4), 77)

def chalk_frame():
    fw, fh = 480, 790
    im = Image.new('RGBA', (fw * 2, fh * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 20, fw * 2 - 20, fh * 2 - 20], radius=110, fill=(255, 255, 255, 10))
    # dashed outline
    pts = []
    R = 110; x0, y0, x1, y1 = 20, 20, fw * 2 - 20, fh * 2 - 20
    path = []
    for i in range(400):
        tt = i / 400 * 2 * (x1 - x0 + y1 - y0)
    # sample rounded-rect perimeter
    def rr_points(n=900):
        segs = []
        for a in np.linspace(180, 270, 20): segs.append((x0 + R + R * math.cos(math.radians(a)), y0 + R + R * math.sin(math.radians(a))))
        for a in np.linspace(270, 360, 20): segs.append((x1 - R + R * math.cos(math.radians(a)), y0 + R + R * math.sin(math.radians(a))))
        for a in np.linspace(0, 90, 20): segs.append((x1 - R + R * math.cos(math.radians(a)), y1 - R + R * math.sin(math.radians(a))))
        for a in np.linspace(90, 180, 20): segs.append((x0 + R + R * math.cos(math.radians(a)), y1 - R + R * math.sin(math.radians(a))))
        segs.append(segs[0])
        # resample evenly
        P = np.array(segs); dd = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
        s = np.linspace(0, dd[-1], n)
        return np.c_[np.interp(s, dd, P[:, 0]), np.interp(s, dd, P[:, 1])]
    P = rr_points(700)
    for i in range(0, len(P) - 1, 2):
        d.line([tuple(P[i]), tuple(P[i + 1])], fill=(235, 235, 235, 230), width=4)
    d2 = Image.new('RGBA', im.size, (0, 0, 0, 0)); dd2 = ImageDraw.Draw(d2)
    dd2.rounded_rectangle([34, 34, fw * 2 - 34, fh * 2 - 34], radius=100, outline=(200, 200, 200, 90), width=3)
    im = Image.alpha_composite(im, d2)
    return A.pil_to_rgba(im)
CFRAME = chalk_frame()

def banner():
    s = '  he turned it into a wooden tube and called it the stethoscope  '
    f = A.font('pf', 30, 500)
    tw = int(f.getlength(s))
    bw_, bh = tw + 1500, 64
    im = Image.new('RGBA', (bw_, bh + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 10, bw_, 10 + bh], fill=(222, 50, 62, 255))
    d.text((760, 10 + bh / 2), s, font=f, fill=(40, 10, 10, 255), anchor='lm')
    arr = np.asarray(im).astype(np.float32) / 255
    tex = A.fbm(arr.shape[0], arr.shape[1], (40, 10), 13)
    arr[..., :3] *= (.9 + .2 * tex)[..., None]
    return arr
BANNER = banner()

# ------------------------------------------------------------------ scenes (u = local time)
GOLD, CREAM = (255, 205, 60), (250, 240, 215)

def sc_lab(u, D):
    z = 1.04 + .06 * u / D; dx = -35 + 40 * u / D
    fe, fb = cam(LAB_E, z, dx), cam(LAB_B, z, dx)
    m = ease_io((u - 1.05) / .35)
    f = fe * (1 - m) + fb * m
    words = [('Most medical', 36, CREAM, (330, 232), 1.30), ('Inventions', 88, GOLD, (395, 292), 1.48),
             ('come from', 36, CREAM, (530, 362), 1.70), ('Labs.', 92, GOLD, (290, 382), 1.90)]
    for s, sz, col, (x, y), st in words:
        e = ease_out((u - st) / .28)
        if e <= 0: continue
        big = sz > 50
        f = blit(f, text(s, 'pfi', sz, col, wght=700 if big else 500), x, y, scale=1.3 - .3 * e, alpha=e, sblur=(1 - e) * 7,
                 glow=((1, .8, .2), 14, .9) if big else ((1, .9, .6), 8, .35), shadow=(3, 4, 7, .85))
    return f

def sc_wall(u, D):
    shake = 0
    land = .98
    if u > land: shake = 10 * math.exp(-(u - land) * 14) * math.sin((u - land) * 70)
    f = cam(STONE, 1.06 + .05 * u / D, 0, -shake)
    # dust in light
    r = np.random.default_rng(5)
    for i in range(70):
        x = (r.uniform(200, 650) + u * r.uniform(-20, 20)); y = (r.uniform(300, 1200) + u * r.uniform(10, 40))
        cv2.circle(f, (int(x), int(y)), int(r.integers(1, 3)), (.9, .9, .9), -1, cv2.LINE_AA)
    full = text('THIS', 'anton', 104, (226, 32, 36), depth=10)
    left = 232 - full.shape[1] / 2
    word = 'THIS'
    n = int(clamp01((u - .05) / .3) * 4 + .999)
    if n > 0:
        sp = text(word[:n], 'anton', 104, (226, 32, 36), depth=10)
        f = blit(f, sp, left + sp.shape[1] / 2, 600 - shake, shadow=(6, 10, 10, .5))
    full2 = text('ONE', 'anton', 104, (226, 32, 36), depth=10)
    left2 = 505 - full2.shape[1] / 2
    n2 = int(clamp01((u - .38) / .22) * 3 + .999)
    if n2 > 0:
        sp = text('ONE'[:n2], 'anton', 104, (226, 32, 36), depth=10)
        f = blit(f, sp, left2 + sp.shape[1] / 2, 600 - shake, shadow=(6, 10, 10, .5))
    p = clamp01((u - .5) / (land - .5))
    if p > 0:
        y = lerp(-320, 585, bounce(p))
        vy = 0 if p >= 1 else 40
        f = blit(f, STETH, 368, y - shake, scale=.85, rot=lerp(-12, 0, ease_out(p)), mb=(0, vy) if p < .45 else None,
                 shadow=(10, 14, 8, .55))
    return f

def sc_orange(u, D):
    f = cam(ORANGE, 1.04 + .05 * u / D, 0, 10 * u)
    # moving window light
    M = cv2.getRotationMatrix2D((600, 800), -28, 1.35)
    M[0, 2] += -240 + 18 * u; M[1, 2] += -520 + 10 * u
    wl = cv2.warpAffine(WSHADOW, M, (W, H), borderMode=cv2.BORDER_CONSTANT)
    f = f * (.80 + .32 * wl[..., None])
    # 1816
    e = ease_out((u - .05) / .45)
    if e > 0 and u < 1.75:
        yy = lerp(780, 650, e); sc = lerp(.7, 1.0, e) + .06 * clamp01((u - .5) / 1.0)
        mbv = None
        if u > 1.4:
            q = ease_in((u - 1.4) / .35); yy = lerp(650, -260, q); mbv = (0, 70 * q)
        f = blit(f, text('1816', 'anton', 150, (252, 248, 240), shear=.22), 360, yy, scale=sc, alpha=e, sblur=(1 - e) * 6,
                 shadow=(8, 12, 12, .45), mb=mbv)
    # polaroid
    if u > 1.45:
        q = ease_out((u - 1.45) / .55)
        y = lerp(1600, 640, q); rot = lerp(-18, 5, q); x = 360
        photo = POL_YOUNG
        mbv = (0, 60 * (1 - q)) if q < .8 else None
        if u > 1.95: rot = lerp(5, 3, clamp01((u - 1.95) / .9)); y = 640 - 10 * clamp01((u - 1.95) / .9)
        if u > 2.85:
            w = ease_io((u - 2.85) / .25)
            rot = lerp(3, -7, w); x = 360 + 30 * math.sin(w * math.pi)
            mbv = (int(70 * math.sin(w * math.pi)), 0)
            if u > 2.97: photo = POL_WARD
        if u > 3.65:
            w = ease_in((u - 3.65) / .4)
            y = lerp(630, -480, w); rot = lerp(-7, -14, w); mbv = (0, int(90 * w))
        f = blit(f, photo, x, y, scale=1.05, rot=rot, mb=mbv, shadow=(14, 20, 16, .55))
    return f

def sc_ward(u, D):
    f = cam(WARD, 1.06 + .08 * u / D, 25 - 50 * u / D, 0)
    return f

def sc_table(u, D):
    f = cam(TABLE, 1.05 + .05 * u / D, 0, 0, rot=1.2 * u / D)
    p = ease_io((u - .5) / 2.8)
    spr = paper_roll_sprite(p)
    cy = lerp(560, 520, p) + spr.shape[0] / 2 * 0
    f = blit(f, spr, 360, lerp(600, 460 + 260, p) - 0, scale=1.0, rot=lerp(4, -6, p), shadow=(12, 18, 14, .6))
    words = 'rolled a sheet of paper into a tube.'.split()
    st, step = .35, .5
    i = int((u - st) // step)
    if 0 <= i < len(words):
        a = clamp01((u - st - i * step) / .06)
        f = blit(f, text(words[i], 'pfi', 30, (250, 250, 250), wght=500), 360, 905, alpha=a, shadow=(2, 3, 5, .7))
    return f

def sc_listen(u, D):
    f = cam(LISTEN, 1.10 + .14 * ease_io(u / D), 60 * u / D, 40 * u / D)
    words = ['louder', 'than', 'ever.']
    st, step = .2, .55
    i = int((u - st) // step)
    if 0 <= i < len(words):
        a = clamp01((u - st - i * step) / .06)
        f = blit(f, text(words[i], 'pfi', 42, (255, 255, 255), wght=600), 360, 1000, alpha=a, shadow=(2, 3, 9, .95))
    return f

SLOTS = [(118, -4), (272, 3), (440, -3), (612, 5)]
def sc_evo(u, D):
    f = cam(BLUE, 1.04 + .04 * u / D)
    for k, spr in enumerate(EVO):
        st = .15 + k * .42
        q = clamp01((u - st) / .45)
        if q <= 0: continue
        e = ease_out(q)
        sx, rot = SLOTS[k]
        x = lerp(W + 220, sx, e)
        vel = (1 - e) * 120
        sc = 400 / spr.shape[0]
        f = blit(f, spr, x, 800 + 8 * math.sin(u * 2 + k), scale=sc, rot=rot + (1 - e) * 15, mb=(int(vel), 0) if vel > 6 else None,
                 shadow=(10, 16, 10, .45))
    # scrolling red tape banner
    off = int(u * 300)
    sl = BANNER[:, off:off + 900]
    f = blit(f, sl, 360, 420, rot=4, shadow=(6, 12, 10, .45))
    return f

LINES = [('HIS SIMPLE IDEA', (245, 245, 245)), ('NOW HANGS', (40, 215, 255)), ('AROUND THE NECK', (255, 45, 60)),
         ('OF EVERY', (255, 215, 30)), ('DOCTOR', (70, 245, 70)), ('ON EARTH.', (245, 245, 245))]
LSIZES = []
for s, c in LINES:
    tw = text_width(s, 'luckiest', 100)
    LSIZES.append(int(min(100 * 380 / tw, 84 if s != 'HIS SIMPLE IDEA' and s != 'ON EARTH.' else 32)))
LH = [sz * 1.0 for sz in LSIZES]
def sc_chalk(u, D):
    f = cam(CHALK, 1.03 + .03 * u / D)
    gin = ease_out(u / .3)
    gs = lerp(1.18, 1.0, gin)
    end = ease_in((u - 3.45) / .75)
    grot = -10 * end; gs *= lerp(1, .74, end); gdx = -20 * end
    c = np.array([360.0, 640.0])
    th = math.radians(grot)
    R = np.array([[math.cos(th), math.sin(th)], [-math.sin(th), math.cos(th)]])
    def G(x, y):
        v = c + gs * R @ (np.array([x, y]) - c); return v[0] + gdx, v[1]
    x, y = G(360, 640)
    f = blit(f, CFRAME, x, y, scale=gs, rot=grot, alpha=gin)
    total = sum(len(s) for s, _ in LINES)
    nchar = int(clamp01((u - .25) / 2.7) * total)
    ytot = sum(LH) + 8 * (len(LH) - 1)
    yy = 640 - ytot / 2
    for (s, col), sz, lh in zip(LINES, LSIZES, LH):
        k = min(len(s), nchar); nchar -= k
        if k > 0:
            full = text(s, 'luckiest', sz, col)
            part = text(s[:k], 'luckiest', sz, col)
            left = 360 - full.shape[1] / 2
            px, py = left + part.shape[1] / 2, yy + lh / 2
            gx, gy = G(px, py)
            f = blit(f, part, gx, gy, scale=gs, rot=grot, glow=(tuple(v / 255 for v in col), 10, .9), shadow=(3, 5, 4, .6))
        yy += lh + 8
    return f

ZIG = [('And', 175, 520, .08), ('the', 520, 590, .32), ('strangest', 245, 680, .58), ('part', 505, 770, .86)]
def sc_navy(u, D):
    sh = 5 * math.sin(u * 37) * math.exp(-u * 1.5)
    f = cam(NAVY, 1.05 + .04 * u / D, sh, sh * .6)
    drift = -18 * u
    for s, x, y, st in ZIG:
        e = ease_out((u - st) / .3)
        if e <= 0: continue
        f = blit(f, text(s, 'pfi', 50, (255, 255, 255), wght=600), x + drift + (1 - e) * 60, y + drift * .5, scale=1.35 - .35 * e,
                 alpha=e, sblur=(1 - e) * 9, glow=((1, 1, 1), 12, .6), mb=(int(40 * (1 - e)), 0) if e < .9 else None)
    return f

def sc_modern(u, D):
    return cam(MODERN, 1.0 + .07 * u / D, 0, 6 * math.sin(u * 6), rot=1.5 * math.sin(u * 3))

STAIR = ['his', 'own', 'invention', 'diagnosed', 'the', 'disease', 'that', 'killed', 'him:', 'tuberculosis.']
def sc_paper(u, D):
    f = cam(WHITE, 1.03 + .04 * u / D)
    e1 = ease_out((u - .0) / .35)
    for spr, ox, oy in ((RED_T, -420, -420), (BLUE_T, -380, 420)):
        if e1 <= 0: continue
        Mt = np.float32([[1, 0, ox * (1 - e1)], [0, 1, oy * (1 - e1)]])
        lay = cv2.warpAffine(spr, Mt, (W, H), borderMode=cv2.BORDER_CONSTANT)
        sa = np.roll(blur(lay[..., 3], 10), 10, 0)
        f = f * (1 - .45 * sa[..., None])
        f = f * (1 - lay[..., 3:4]) + lay[..., :3] * lay[..., 3:4]
    # polaroid
    q = ease_out((u - .3) / .5)
    if q > 0:
        x = lerp(-260, 380, q); rot = lerp(18, -4, q); y = 640
        sc = 1.05 + .05 * clamp01((u - .8) / 1.4)
        mbv = (int(60 * (1 - q)), 0) if q < .85 else None
        if u > 2.2:
            w = ease_io((u - 2.2) / .45)
            x = lerp(380, -40, w); y = lerp(640, 760, w); rot = lerp(-4, 4, w); sc = lerp(1.1, 1.0, w)
            mbv = (int(60 * math.sin(w * math.pi)), 0) if w < .95 else None
        f = blit(f, POL_OLD, x, y, scale=sc, rot=rot, mb=mbv, shadow=(14, 20, 16, .5))
    st, step = 2.6, .27
    n = len(STAIR)
    for i, wd in enumerate(STAIR):
        e = ease_out((u - st - i * step) / .2)
        if e <= 0: continue
        x = lerp(215, 520, i / (n - 1)); y = lerp(300, 1000, i / (n - 1))
        last = i == n - 1
        sp = text(wd, 'pfi', 50 if last else 40, (175, 25, 30) if last else (20, 20, 22), wght=700 if last else 500)
        f = blit(f, sp, x, y - 12 * (1 - e), alpha=e)
    return f

# ------------------------------------------------------------------ timeline
SCENES = [(sc_lab, 0.0, 2.8), (sc_wall, 2.8, 4.3), (sc_orange, 4.3, 8.4), (sc_ward, 8.4, 11.0), (sc_table, 11.0, 15.4),
          (sc_listen, 15.4, 17.6), (sc_evo, 17.6, 21.2), (sc_chalk, 21.2, 25.4), (sc_navy, 25.4, 26.8),
          (sc_modern, 26.8, 28.5), (sc_paper, 28.5, 34.8)]
TRANS = {2.8: ('zoomwhip', .16), 4.3: ('slide', .2), 15.4: ('blurfade', .25), 17.6: ('flash', .14), 21.2: ('smear', .28),
         28.5: ('flash', .08)}
END = SCENES[-1][2]

def scene_frame(t, idx=None):
    if idx is None:
        idx = max(i for i, s in enumerate(SCENES) if s[1] <= t) if t >= 0 else 0
    fn, a, b = SCENES[idx]
    return fn(min(max(t - a, 0), b - a - 1e-3), b - a)

def idx_of(T):
    for i, s in enumerate(SCENES):
        if abs(s[1] - T) < 1e-6: return i

def frame(t):
    for T, (typ, d) in TRANS.items():
        if T - d <= t < T + d:
            ib = idx_of(T); ia = ib - 1
            if typ == 'zoomwhip':
                if t < T:
                    p = (t - (T - d)) / d; f = scene_frame(t, ia)
                    return zoom_blur(cam(f, 1 + .5 * ease_in(p)), p * 1.5)
                p = (t - T) / d; f = scene_frame(t, ib)
                return zoom_blur(cam(f, 1.35 - .35 * ease_out(p)), (1 - p) * 1.5)
            if typ == 'slide':
                p = (t - (T - d)) / (2 * d); off = int(ease_io(p) * W)
                fa, fb = scene_frame(min(t, T - 1e-3), ia), scene_frame(max(t, T), ib)
                f = np.concatenate([fa[:, off:], fb[:, :off]], 1) if off > 0 else fa
                return mblur(f, int(90 * math.sin(math.pi * p)), 0)
            if typ == 'blurfade':
                p = (t - (T - d)) / (2 * d); s = 14 * math.sin(math.pi * p); m = ease_io(p)
                fa, fb = scene_frame(min(t, T - 1e-3), ia), scene_frame(max(t, T), ib)
                return blur(fa, s) * (1 - m) + blur(fb, s) * m
            if typ == 'flash':
                f = scene_frame(t)
                w = 1 - abs(t - T) / d
                return f + (1 - f) * w * .95
            if typ == 'smear':
                p = (t - (T - d)) / (2 * d)
                fa, fb = scene_frame(min(t, T - 1e-3), ia), scene_frame(max(t, T), ib)
                e = lerp(W + 250, -250, ease_io(p))
                y, x = np.mgrid[0:H, 0:W].astype(np.float32)
                edge = e + (y - H / 2) * .3
                m = 1 / (1 + np.exp(-(x - edge) / 25))
                f = fa * (1 - m[..., None]) + fb * m[..., None]
                dark = np.exp(-((x - edge) / 110) ** 2) * .9
                f = f * (1 - dark[..., None])
                return mblur(f, int(70 * math.sin(math.pi * p)), 0)
    return scene_frame(t)

def post(f, i):
    f = f * VIG + GRAIN[i % len(GRAIN)]
    return np.clip(f, 0, 1)

if __name__ == '__main__':
    out = sys.argv[1]
    sample = len(sys.argv) > 2  # write stills instead
    if sample:
        times = [float(x) for x in sys.argv[2].split(',')]
        tiles = []
        for t in times:
            tiles.append(cv2.resize(post(frame(t), int(t * FPS)), (240, 427)))
        while len(tiles) % 6: tiles.append(np.zeros_like(tiles[0]))
        img = np.vstack([np.hstack(tiles[i:i + 6]) for i in range(0, len(tiles), 6)])
        cv2.imwrite(out, (img[..., ::-1] * 255).astype(np.uint8))
        sys.exit()
    n = int(END * FPS)
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', out],
                         stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(n):
        f = post(frame(i / FPS), i)
        p.stdin.write((f * 255 + .5).astype(np.uint8).tobytes())
        if i % 60 == 0: print(f'{i}/{n} {time.time() - t0:.0f}s', flush=True)
    p.stdin.close(); p.wait()
    print('done', out)
