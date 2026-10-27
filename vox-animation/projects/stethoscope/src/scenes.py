"""Six 10-second paper-diorama scenes for the Hinglish stethoscope explainer."""
import math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
from dlib import *

SCENE_LEN = 10.0

# ------------------------------------------------------------ captions
CAPTIONS = [
    ["Yeh cheez aaj", "har doctor ke", "gale mein latakti hai.", "Aur isne", "apne hi inventor ki", "*maut* pakdi thi."],
    ["Paris,", "*eighteen sixteen.*", "Us zamaane mein", "heartbeat sunne ke liye", "doctor seedha patient ki", "chest pe kaan lagate the."],
    ["Necker Hospital mein", "René Laennec ke saamne", "thi ek young lady,", "heart problem ke saath.", "Kaan lagana?", "Bilkul *nahi.*"],
    ["Toh unhone", "ek *kaagaz* ko roll karke", "tube banaya,", "ek end uski chest pe rakha,", "aur dhyaan se suna."],
    ["Heartbeat pehle se", "kahin zyada *loud* thi.", "Teen saal mein", "woh tube lakdi ki bani,", "naam mila:", "*stethoscope.*"],
    ["Aur sabse ajeeb baat?", "Kehte hain,", "*eighteen twenty-six* mein", "isi stethoscope ne pakdi", "woh bimaari", "jisne unki jaan li:", "*tuberculosis.*"],
]

def chunk_times(chunks, t0=.3, t1=9.5):
    n = [len(c.replace('*', '').split()) + .6 for c in chunks]
    tot = sum(n); out = []; t = t0
    for c, k in zip(chunks, n):
        d = (t1 - t0) * k / tot; out.append((t, t + d, c)); t += d
    return out
CTIMES = [chunk_times(c) for c in CAPTIONS[:5]] + [chunk_times(CAPTIONS[5], .3, 8.9)]
def ctime(scene, needle):
    for a, b, c in CTIMES[scene]:
        if needle in c.lower(): return a
    return 0

@functools.lru_cache(maxsize=64)
def caption_sprite(chunk):
    f = font('inter', 56, 800)
    words = chunk.split(' ')
    parts = []
    for wd in words:
        hl = wd.startswith('*') or wd.endswith('*') or wd.endswith('*.') or wd.endswith('*,') or '*' in wd
        parts.append((wd.replace('*', ''), hl))
    # highlight spans between stars
    on = False; fixed = []
    for wd in words:
        s = wd
        start = s.startswith('*'); s = s.replace('*', '')
        if start: on = True
        fixed.append((s, on))
        if wd.rstrip('.,:?').endswith('*'): on = False
    sp = f.getlength(' ')
    tw = sum(f.getlength(w) for w, _ in fixed) + sp * (len(fixed) - 1)
    pad = 24; asc = f.getbbox('Hg')
    h = asc[3] - asc[1] + pad * 2; w = int(tw + pad * 2)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = pad
    for wd, hl in fixed:
        col = (238, 110, 35, 255) if hl else (255, 250, 240, 255)
        d.text((x, pad - asc[1]), wd, font=f, fill=col, stroke_width=6, stroke_fill=(15, 12, 10, 255))
        x += f.getlength(wd) + sp
    return np.asarray(im).astype(np.float32) / 255

def draw_captions(f, scene, u):
    for a, b, c in CTIMES[scene]:
        if a <= u < b:
            e = ease_out((u - a) / .12)
            spr = caption_sprite(c)
            sc = min(1.0, 660 / spr.shape[1]) * lerp(.9, 1.0, e)
            f = blit(f, spr, W / 2, 1035, sc, 0, e, shadow=(0, 6, 8, .55))
    return f

# ------------------------------------------------------------ assets (lazy)
@functools.lru_cache(maxsize=None)
def A(name):
    if name == 'wall_dark': return newsprint(1600, 900, 101, .62)
    if name == 'row_backdrop':
        img = newsprint(1600, 900, 102, .95)
        fl = int(1600 * .62)
        img[fl:] = floor_planks(1600 - fl, 900, 103, .62)
        return img
    if name == 'doc_white': return white_coat_doctor(820, 5)
    if name == 'frock': return frock_doctor(820, 1.0, seed=3)
    if name == 'frock_hat': return frock_doctor(820, 1.0, hat=True, seed=4, hair=30)
    if name == 'laennec': return frock_doctor(820, .85, seed=6, hair=40)
    if name == 'woman': return seated_woman(640, 7)
    if name == 'sickbed': return sickbed(760, 9)
    if name == 'young': return frock_doctor(760, .9, seed=11, hair=30)
    if name == 'hand_l': return hand_sprite(False, 13)
    if name == 'hand_r': return hand_sprite(True, 14)
    if name == 'tomb': return tombstone(360, 15)
    if name == 'sky':
        img = newsprint(1600, 900, 104, 1.05, density=.5)
        y = np.linspace(0, 1, 1600, dtype=np.float32)[:, None, None]
        img = img * (1.08 - .25 * y) * np.array([1.0, .95, .86], np.float32)
        return np.clip(img, 0, 1)
    if name == 'night_sky':
        img = newsprint(1600, 900, 105, .5, density=.4)
        return np.clip(img * np.array([.8, .82, .9], np.float32), 0, 1)
    if name == 'ward':
        img, glow = wall_with_windows(1600, 900, 106, 2, .92)
        fl = int(1600 * .64); img[fl:] = floor_planks(1600 - fl, 900, 107, .66)
        return img
    if name == 'ward_small':
        img, glow = wall_with_windows(1600, 900, 108, 1, .8)
        fl = int(1600 * .64); img[fl:] = floor_planks(1600 - fl, 900, 109, .58)
        return img
    if name == 'bedroom':
        img, glow = wall_with_windows(1600, 900, 110, 1, .55, lit=False)
        fl = int(1600 * .66); img[fl:] = floor_planks(1600 - fl, 900, 111, .45)
        return img
    if name == 'desk': return newsprint(1700, 1000, 112, .5)
    if name == 'bench_wall':
        img = newsprint(1600, 900, 113, .85)
        fl = int(1600 * .6)
        bench = newsprint(1600 - fl, 900, 114, .5, density=.5) * np.array([.9, .75, .6], np.float32)
        img[fl:] = bench; img[fl:fl + 14] *= .45
        return img
    if name == 'pillar':
        w, h = 260, 1000; m = np.zeros((h, w), np.float32)
        cv2.rectangle(m, (0, 0), (w, h), 1, -1)
        a, rim = torn_alpha(m, 120, 4)
        col = newsprint(h, w, 121, .7) * np.linspace(1.1, .7, w, dtype=np.float32)[None, :, None]
        return rgba(col * (1 - rim[..., None]) + WHITE_P * rim[..., None], a)
    if name == 'bed':
        w, h = 640, 260; f = Fig(w, h)
        f.rect((w * .02, h * .1, w * .06, h), 40); f.rect((w * .94, h * .3, w * .98, h), 40)
        f.rect((w * .03, h * .45, w * .97, h * .7), 228); f.rect((w * .03, h * .66, w * .97, h * .76), 70)
        return f.build(seed=122)
    if name == 'tube': return tube_sprite(420, 34, 21)
    if name == 'wood': return tube_sprite(420, 30, 22, wood=True)
    if name == 'listen': return stamp_text('LISTEN', 90, WHITE_P * .85, 33, distress=.3)
    if name == 'st1826': return stamp_text('1826', 170, ORANGE, 34)
    if name == 'st1816': return torn_strip(330, 120, 35, label='1816', label_size=86)
    if name == 'stNO': return stamp_text('NO', 260, ORANGE, 36, distress=.28)
    if name == 'stSTETH': return torn_strip(620, 120, 37)
    if name == 'stSTETH_t': return stamp_text('STETHOSCOPE', 96, INK * 1.3, 38, distress=.3)
    if name == 'stTB_strip': return torn_strip(640, 130, 39)
    if name == 'stTB_t': return stamp_text('TUBERCULOSIS', 92, INK * 1.3, 40, distress=.3)
    if name == 'pole':
        m = np.zeros((300, 30), np.float32); cv2.rectangle(m, (10, 0), (20, 300), 1, -1)
        return rgba(np.broadcast_to(INK * 2, (300, 30, 3)).copy(), m)
    if name.startswith('row'):
        k = int(name[3:])
        cfg = {0: (2400, .78, 360, 640, True), 1: (2200, .92, 320, 560, False), 2: (2000, 1.02, 260, 480, False), 3: (1800, 1.1, 230, 420, False)}[k]
        return house_row(cfg[0], 200 + k * 7, cfg[1], cfg[2], cfg[3], dome=cfg[4])
    if name.startswith('cloud'): return cloud(500, 300 + int(name[5:]))
    if name.startswith('stone'): k = int(name[5:]); return mini_stone(120, 400 + k, cross=k % 3 == 0)
    if name.startswith('sheet'):
        k = int(name[5:]); w, h = 120, 150
        return rgba(newsprint(h, w, 500 + k, 1.0), np.ones((h, w), np.float32))
    if name == 'tunnel_tex':
        t = orange_paper(512, 512, 600)
        n = fbm(512, 512, (64, 16, 4), 601)
        return np.clip(t * (.75 + .4 * n)[..., None], 0, 1)
    raise KeyError(name)

def lean_sprite(spr, bend, hip=.6):
    """Bend a figure forward at the hips (bend degrees, + = toward +x). Returns (sprite, feet_ax, feet_ay)."""
    h, w = spr.shape[:2]
    hy = int(h * hip)
    S = int(h * 2.4)
    canvas = np.zeros((S, S, 4), np.float32)
    fx, fy = S // 2, int(S * .75)          # feet position in canvas
    ox, oy = fx - w // 2, fy - h
    canvas[oy + hy:oy + h, ox:ox + w] = spr[hy:]
    up = np.zeros_like(canvas); up[oy:oy + hy + 6, ox:ox + w] = spr[:hy + 6]
    M = cv2.getRotationMatrix2D((fx, oy + hy), -bend, 1.0)
    up = cv2.warpAffine(up, M, (S, S), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    a = up[..., 3:4]
    canvas[..., :3] = canvas[..., :3] * (1 - a) + up[..., :3] * a
    canvas[..., 3:4] = np.maximum(canvas[..., 3:4], a)
    ys, xs = np.where(canvas[..., 3] > .02)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    c = canvas[y0:y1, x0:x1]
    return c, (fx - x0) / c.shape[1], (fy - y0) / c.shape[0]

@functools.lru_cache(maxsize=256)
def leaned(name, angle_q):
    return lean_sprite(A(name), angle_q / 2.0)

def lay(spr, x, y, z, size, **kw):
    d = dict(spr=spr, x=x, y=y, z=z, size=size); d.update(kw); return d

def draw_anchored(dst, cam, items):
    """Like draw_layers but supports anchor (ax, ay) = sprite fraction placed at (x,y)."""
    out = []
    for L in items:
        if 'ax' in L:
            zr = L['z'] - cam.z
            if zr <= .05: continue
            spr = L['spr']; hpx, wpx = spr.shape[:2]
            wpu = L['size'] / hpx  # world units per sprite px
            L = dict(L); L['x'] = L['x'] + (.5 - L['ax']) * wpx * wpu; L['y'] = L['y'] + (.5 - L['ay']) * hpx * wpu
        out.append(L)
    return draw_layers(dst, cam, out)

def figure_layer(name, x, z, size, ground=1.0, lean=0.0, **kw):
    if abs(lean) > .25:
        spr, ax, ay = leaned(name, int(round(lean * 2)))
        hpx = A(name).shape[0]
        return lay(spr, x, ground, z, size * spr.shape[0] / hpx, ax=ax, ay=ay, **kw)  # lean = hip bend degrees
    return lay(A(name), x, ground - size / 2, z, size, **kw)

def backdrop(name, cam_x=0, cam_y=0, zoom=1.0, par=.05, rot=0):
    return cover(A(name), zoom, cam_x * par * 400, cam_y * par * 400, rot)

def tunnel(u, speed=2.0, pulse=True, fade_center=True):
    h, w = H, W
    if not hasattr(tunnel, 'g'):
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        dx, dy = x - w / 2, y - h / 2
        rr = np.sqrt(dx * dx + dy * dy) + 1
        th = np.arctan2(dy, dx)
        tunnel.g = (rr, th)
    rr, th = tunnel.g
    d = 260.0 / rr  # depth
    tex = A('tunnel_tex')
    mx = ((th / (2 * math.pi) + .5) * 512 * 2 + d * 30) % 512
    my = (d * 60 - u * speed * 60) % 512
    col = cv2.remap(tex, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    ring = .86 + .14 * np.sin((d - u * speed) * 2 * math.pi * 1.3)
    fog = np.exp(-d * .22)
    img = col * (ring * (.12 + .95 * fog))[..., None]
    if pulse:
        for k in range(3):
            pos = 6 - ((u * 1.4 + k * .9) % 2.7) * 2.4
            band = np.exp(-((d - pos) / .35) ** 2) * clamp01(1 - pos / 6)
            img = img + band[..., None] * np.array([1, .8, .55], np.float32) * .55
    return np.clip(img, 0, 1)

def glow_spot(f, x, y, r, col=(1, .7, .35), k=.6):
    m = np.zeros((H, W), np.float32); cv2.circle(m, (int(x), int(y)), int(r), 1, -1)
    return f + blur(m, r * .9)[..., None] * np.array(col, np.float32) * k

def finish(f, u, enter=None, exit_=None):
    """Motion-blur entry (first .3s) and exit (last .45s) so cuts read as one shot."""
    if enter and u < .3:
        p = 1 - u / .3
        f = mblur(f, enter[0] * p, enter[1] * p) if enter != 'zoom' else zoom_blur(f, p * 1.6)
    if exit_ and u > SCENE_LEN - .45:
        p = ease_in((u - (SCENE_LEN - .45)) / .45)
        f = mblur(f, exit_[0] * p, exit_[1] * p) if exit_ != 'zoom' else zoom_blur(f, p * 1.8)
    return f

# ------------------------------------------------------------ scene 1: the row of doctors -> tunnel -> grave
ROW = [(-.95 if i % 2 else .95, 3.2 + i * 1.7) for i in range(12)]
def scene1(u):
    if u < 6.4:
        if u < 2.3:  # macro pull back with speed ramp
            q = u / 2.3
            e = q ** 4 * .85 + ease_io(q) * .15
            cz = lerp(1.6, -1.6, e); cy = lerp(-.22, -.1, e); cx = 0
        else:
            q = (u - 2.3) / 4.1
            cz = lerp(-1.6, 21.0, ease_io5(q) * .9 + q * .1); cx = .35 * math.sin(q * 9); cy = -.1 + .05 * math.sin(q * 13)
        cam = Cam(cx, cy, cz, F=900, roll=3 * math.sin(u * 1.3), focus=2.2 if u < 2.3 else 3.0, dof=1.0)
        f = backdrop('row_backdrop', cx, cy, 1.05 + .02 * u)
        items = [figure_layer('doc_white', 0, 2.0, 1.9)]
        for x, z in ROW: items.append(figure_layer('doc_white', x, z, 1.9))
        items.append(figure_layer('doc_white', 0, 23.5, 1.9))
        f = draw_anchored(f, cam, items)
        if u > 5.6:  # dive into the stethoscope
            p = ease_in((u - 5.6) / .8)
            f = zoom_blur(cover(f, 1 + 3.5 * p, 0, -120 * p), p * 1.5)
            f = f * (1 - .85 * p) + tunnel(u) * .85 * p
    elif u < 7.5:
        f = tunnel(u, 3.0)
        if u < 6.7: f = zoom_blur(f, (6.7 - u) * 4)
        if u > 7.15:
            p = (u - 7.15) / .35; f = zoom_blur(f, p * 2); f = f + (1 - f) * p * .9
    else:
        q = u - 7.5
        sx, sy = impact_shake(u, 8.32, 16)
        cam = Cam(sx * .002, -.35 + sy * .002, lerp(-1.0, .2, ease_out(q / 2.4)), F=900, focus=2.6, dof=1.0)
        f = backdrop('night_sky', 0, 0, 1.08 + .03 * q)
        f[int(H * .7):] *= .55
        items = [lay(A('tomb'), 0, .15, 2.6, 1.55)]
        for k in range(9):
            x = (k - 4) * .9 + (.3 if k % 2 else 0); z = 4.5 + (k % 3) * 1.6
            items.append(lay(A('stone%d' % k), x, .55 - (z - 4) * .02, z, .62))
        f = draw_anchored(f, cam, items)
        f = glow_spot(f, W * .5, H * .25, 220, (.9, .85, .7), .25)
        f = stamp(f, A('st1826'), W / 2 + 4, H * .515, u - 8.32, 300, rot=-6, seed=3)
        if q < .25: f = f + (1 - f) * (1 - q / .25) * .9
        if u > 9.5:
            p = ease_in((u - 9.5) / .5); f = mblur(cover(f, 1.0, 0, 200 * p), 0, 160 * p)
    f = draw_captions(f, 0, u)
    return finish(f, u, enter='zoom')

# ------------------------------------------------------------ scene 2: Paris rooftops -> ward of ear-on-chest doctors
def scene2(u):
    if u < 4.6:
        q = u / 4.6
        cz = lerp(0, 6.5, ease_io(q) * .7 + q * .3); cx = lerp(-.8, .6, ease_io(q)); cy = lerp(-.6, -.2, q)
        cam = Cam(cx, cy, cz, F=900, roll=lerp(-4, 3, q), focus=5.0, dof=.9)
        f = backdrop('sky', cx, cy, 1.05)
        items = [lay(A('cloud%d' % k), (k - 2) * 3.5, -5 + (k % 2) * 1.4, 30 + k * 2, 2.6, shadow=None) for k in range(5)]
        rows = [(0, 24, 11.0, 4.0), (1, 15, 7.2, 3.2), (2, 10, 4.8, 2.4), (3, 8, 3.2, 1.8)]
        for k, z, size, ground in rows:
            spr = A('row%d' % k)
            items.append(lay(spr, (k - 1.5) * .6, ground - size / 2, z, size))
        # orange 1816 flag on the nearest roof
        fq = ease_back((u - 1.3) / .35)
        items.append(lay(A('pole'), .3, 1.6 - 1.2, 8.4, 1.2, shadow=None))
        f = draw_anchored(f, cam, items)
        if u > 1.3:
            p = cam.project(.3, -.05, 8.4)
            if p:
                sx, sy, zr = p; sc = 900 * .75 / zr / A('st1816').shape[0]
                spr = A('st1816')
                wav = math.sin(u * 9) * 3
                f = blit(f, spr, sx + spr.shape[1] * sc * .5 * max(fq, .05), sy, sc * max(fq, .05), wav, 1.0, shadow=(6, 9, 6, .4))
        if u > 3.7:  # dive toward the hospital window
            p = ease_in((u - 3.7) / .9)
            f = zoom_blur(cover(f, 1 + 2.2 * p, 0, 60 * p), p * 1.8)
            f = f + (1 - f) * p * .5
    else:
        q = (u - 4.6) / 5.4
        cx = .55 * math.sin(q * 3.2 + .5); cz = lerp(.3, 1.6, ease_io(q)); cy = -.12
        if u > 9.1:
            p = ease_in((u - 9.1) / .9); cz += 5 * p
        cam = Cam(cx, cy, cz, F=900, roll=-2 * math.sin(q * 3), focus=3.6, dof=1.1)
        f = backdrop('ward', cx, cy, 1.02, par=.08)
        items = [lay(A('bed'), .55, .78, 4.0, .7)]
        items.append(figure_layer('woman', .62, 4.0, 1.35, ground=1.0))
        lean = 78 * ease_io((u - 5.0) / .7)
        items.append(figure_layer('frock', -.5, 3.95, 1.9, lean=lean))
        for k, (bx, bz, t0) in enumerate(((-2.0, 6.5, 6.9), (2.2, 7.5, 7.6))):
            e = ease_back((u - t0) / .3)
            if e > 0:
                items.append(lay(A('bed'), bx + .55, .78, bz, .7 * e))
                items.append(figure_layer('woman', bx + .62, bz, 1.35 * e))
                items.append(figure_layer('frock_hat' if k else 'frock', bx - .5 * e, bz - .05, 1.9 * e, lean=78 * ease_io((u - t0 - .2) / .4)))
        f = draw_anchored(f, cam, items)
        f = glow_spot(f, W * .25, H * .3, 200, (1, .9, .7), .18); f = glow_spot(f, W * .75, H * .3, 200, (1, .9, .7), .18)
        if u < 4.9: f = zoom_blur(f, (4.9 - u) / .3 * 1.5)
        if u > 9.1: f = zoom_blur(f, ease_in((u - 9.1) / .9) * 1.6)
    f = draw_captions(f, 1, u)
    return finish(f, u, enter='zoom')

# ------------------------------------------------------------ scene 3: corridor -> hesitation -> NO
def scene3(u):
    t_no = ctime(2, 'bilkul') + .15
    if u < 3.0:
        q = u / 3.0
        cam = Cam(.1 * math.sin(u * 2), -.1, lerp(0, 8.5, ease_io(q) * .6 + q * .4), F=900, focus=4.0, dof=1.0)
        f = backdrop('wall_dark', 0, 0, 1.05 + .1 * q) * .8
        items = []
        for k in range(7):
            z = 3 + k * 2.2
            for side in (-1, 1):
                items.append(lay(A('pillar'), side * 1.25, -.2, z, 3.2, glow=None))
        f = draw_anchored(f, cam, items)
        for k in range(7):
            p = cam.project(-1.0, -.4, 3 + k * 2.2)
            if p: f = glow_spot(f, p[0], p[1], max(10, 120 / p[2]), (1, .65, .3), .9)
            p = cam.project(1.0, -.4, 4.1 + k * 2.2)
            if p: f = glow_spot(f, p[0], p[1], max(10, 120 / p[2]), (1, .65, .3), .9)
        if u > 2.6: p = ease_in((u - 2.6) / .4); f = zoom_blur(f, p * 1.6)
    else:
        q = u - 3.0
        sx, sy = impact_shake(u, t_no, 22, 8)
        cx, cy, cz, F = lerp(-.3, 0, ease_io(q / 2)), -.2, lerp(.6, 1.2, ease_io(q / 3)), 900
        # snap close-ups on the hesitation
        c1, c2 = 5.25, 5.95
        if c1 <= u < c2: cx, cy, cz = -.1, -.62, 2.5 - .1 * (u - c1)
        elif c2 <= u < c2 + .6: cx, cy, cz = .62, -.2, 2.6 - .1 * (u - c2)
        if u > 9.3: cz -= 3.5 * ease_in((u - 9.3) / .7)
        cam = Cam(cx + sx * .002, cy + sy * .002, cz, F=F, roll=sx * .15, focus=4.0 - cz, dof=1.0)
        f = backdrop('ward_small', cx, cy, 1.04, par=.08)
        step = ease_io((u - 3.4) / .9)
        lean = 34 * ease_io((u - 4.4) / .7) * (1 - ease_io((u - 6.8) / .7))
        x_doc = lerp(-1.7, -.6, step) - .25 * ease_io((u - 6.8) / .7)
        flap = math.sin((u - t_no) * 40) * 8 * math.exp(-(u - t_no) * 4) if u > t_no else 0
        items = [lay(A('bed'), .55, .78, 4.0, .7, rot=flap * .2), figure_layer('woman', .62, 4.0, 1.35, rot=flap * .15),
                 figure_layer('laennec', x_doc, 3.9, 1.95, lean=lean)]
        f = draw_anchored(f, cam, items)
        f = glow_spot(f, W * .5, H * .3, 260, (1, .8, .55), .2)
        for cut in (c1, c2, c2 + .6):
            if cut <= u < cut + .12: f = zoom_blur(f, (cut + .12 - u) / .12 * 1.2)
        if u < 3.3: f = zoom_blur(f, (3.3 - u) / .3 * 1.6)
        if u > t_no:
            d = u - t_no
            if d < .7:  # shockwave ring
                m = np.zeros((H, W), np.float32); cv2.circle(m, (W // 2, int(H * .5)), int(60 + d * 1100), 1, int(30 * (1 - d / .7)) + 2)
                f = f + blur(m, 10)[..., None] * np.array([1, .8, .6], np.float32) * .5 * (1 - d / .7)
            f = stamp(f, A('stNO'), W / 2 + sx, H * .48 + sy, d, 470, rot=-8, seed=5)
        if u > 9.3: f = zoom_blur(f, ease_in((u - 9.3) / .7) * 1.6)
    f = draw_captions(f, 2, u)
    return finish(f, u, enter='zoom')

# ------------------------------------------------------------ scene 4: roll the paper -> on her chest -> into the tube
def roll_sprite(p, seed=700):
    pw, fh = 380, 470
    r = 10 + 24 * p; flat = (1 - p) * fh
    h, w = fh + 90, pw + 20
    out = np.zeros((h, w, 4), np.float32)
    if not hasattr(roll_sprite, 'tex'): roll_sprite.tex = orange_paper(fh + 90, pw, seed)
    y0 = 20; y1 = int(y0 + flat)
    if y1 > y0:
        out[y0:y1, 10:10 + pw, :3] = roll_sprite.tex[:y1 - y0]; out[y0:y1, 10:10 + pw, 3] = 1
    yy = np.arange(h, dtype=np.float32)[:, None]
    u = (yy - y1) / r
    sh = np.sqrt(np.clip(1 - u ** 2, 0, 1))
    light = .5 + .5 * sh + .3 * np.exp(-((u + .45) / .2) ** 2)
    band_a = np.clip((r - np.abs(yy - y1)) * .8, 0, 1) * np.ones((1, w), np.float32)
    band_a[:, :10] = 0; band_a[:, 10 + pw:] = 0
    band_c = ORANGE[None, None] * light[..., None] * np.ones((1, w, 1), np.float32)
    out[..., :3] = out[..., :3] * (1 - band_a[..., None]) + band_c * band_a[..., None]
    out[..., 3] = np.maximum(out[..., 3], band_a)
    return out

def scene4(u):
    if u < 4.2:
        p = ease_io((u - .7) / 2.7)
        f = cover(A('desk'), 1.06 + .04 * u / 4.2, 0, 0, rot=lerp(-3, 2, u / 4.2))
        f = stamp(f, A('listen'), W * .74, H * .2, u - .55, 210, rot=8, seed=7, dust=False)
        spr = roll_sprite(p)
        cy = lerp(620, 470 + 200, p) - 40
        f = blit(f, spr, W / 2, cy, 1.0, lerp(3, -4, p), 1.0, shadow=(12, 18, 12, .55))
        hy = cy + (1 - p) * 235 + 150 + 12 * math.sin(u * 5)
        f = blit(f, A('hand_l'), W / 2 - 175, hy, .6, -14, 1.0, shadow=(10, 16, 10, .5))
        f = blit(f, A('hand_r'), W / 2 + 175, hy, .6, 14, 1.0, shadow=(10, 16, 10, .5))
        if u > 3.8: q = ease_in((u - 3.8) / .4); f = mblur(cover(f, 1, -260 * q, 0), 120 * q, 0)
    elif u < 6.4:
        q = u - 4.2
        sx, sy = impact_shake(u, 5.0, 14)
        cz4 = lerp(1.3, 1.9, ease_io(q / 2.2))
        cam = Cam(.25 + sx * .002, -.1 + sy * .002, cz4, F=900, focus=4.0 - cz4, dof=1.0)
        f = backdrop('ward', .15, -.4, 1.1, par=.08)
        items = [lay(A('bed'), .7, .78, 4.0, .7), figure_layer('woman', .78, 4.0, 1.35),
                 figure_layer('frock', -.4, 3.95, 1.9, lean=76)]
        f = draw_anchored(f, cam, items)
        # flying tube lands between ear and chest
        target = cam.project(.6, .1, 3.97)
        e = ease_out((u - 4.35) / .65)
        if target:
            tx, ty, zr = target
            x = lerp(-220, tx, e); y = lerp(-180, ty, e); rot = lerp(80, -14, e)
            sc = 900 * .34 / zr / A('tube').shape[1]
            rot = lerp(80, -38, e)
            f = blit(f, A('tube'), x, y, sc, rot, 1.0, mb=(int(60 * (1 - e)), int(50 * (1 - e))) if e < .85 else None, shadow=(6, 10, 6, .45))
        if 5.0 < u < 5.4: f = f + (1 - f) * (1 - (u - 5.0) / .4) * .25
        if u < 4.45: f = mblur(f, 120 * (4.45 - u) / .25, 0)
        if u > 5.9:
            p = ease_in((u - 5.9) / .5)
            if target: f = zoom_blur(cover(f, 1 + 3 * p, (target[0] - W / 2) * p * .9, (target[1] - H / 2) * p * .9), p * 1.8)
            f = f * (1 - p) + tunnel(u) * p
    else:
        f = tunnel(u, 2.2)
        if u < 6.7: f = zoom_blur(f, (6.7 - u) * 4)
    f = draw_captions(f, 3, u)
    return finish(f, u, enter=(110, 0), exit_='zoom')

# ------------------------------------------------------------ scene 5: heartbeat burst -> wood -> STETHOSCOPE
def scene5(u):
    t_name = ctime(4, 'stethoscope') - .05
    if u < 2.8:
        sx, sy = impact_shake(u, .25, 18, 6)
        cz5 = lerp(-.6, .2, ease_out(u / 2.8))
        cam = Cam(.2 + sx * .002, -.15 + sy * .002, cz5, F=900, focus=4.0 - cz5, dof=1.0)
        f = backdrop('ward', 0, -.25, 1.04 + .02 * u, par=.08)
        items = [lay(A('bed'), .7, .78, 4.0, .7), figure_layer('woman', .78, 4.0, 1.35), figure_layer('frock', -.4, 3.95, 1.9, lean=76)]
        r = np.random.default_rng(9)
        for k in range(18):  # sheets blown outward
            ang = r.uniform(0, 2 * math.pi); sp = r.uniform(.6, 1.6); d = ease_out((u - .25) / 2.2) * sp * 2.6
            if u > .25:
                items.append(lay(A('sheet%d' % (k % 6)), .25 + math.cos(ang) * d, -.3 + math.sin(ang) * d * .7 - .2 * d, 3.2 - k * .05, .32,
                                 rot=(u * 300 * (1 if k % 2 else -1)) % 360))
        f = draw_anchored(f, cam, items)
        p = cam.project(.6, .1, 3.97)
        if p: f = blit(f, A('tube'), p[0], p[1], 900 * .34 / p[2] / A('tube').shape[1], -38, 1.0)
        for k in range(3):
            d = u - .25 - k * .45
            if 0 < d < 1.0 and p:
                m = np.zeros((H, W), np.float32); cv2.circle(m, (int(p[0]), int(p[1])), int(40 + d * 900), 1, int(26 * (1 - d)) + 2)
                f = f + blur(m, 8)[..., None] * np.array([1, .65, .3], np.float32) * .7 * (1 - d)
        if u < .35: f = f + (1 - f) * (1 - u / .35) * .95
        if u > 2.45: q = ease_in((u - 2.45) / .35); f = mblur(cover(f, 1, 220 * q, 0), 140 * q, 0)
    else:
        q = u - 2.8
        cx = .12 * math.sin(q * .7)
        if u > 9.2: cx += 3 * ease_in((u - 9.2) / .8)
        cz5 = lerp(.4, 1.2, ease_io(q / 6))
        cam = Cam(cx, -.05, cz5, F=900, focus=3.0 - cz5, dof=1.0, roll=2 * math.sin(q))
        f = backdrop('bench_wall', cx, 0, 1.04, par=.1)
        morph = ease_io((u - 4.3) / 1.4)
        bob = .02 * math.sin(u * 6)
        spin = 6 * math.sin(u * 3)
        items = []
        if morph < 1: items.append(lay(A('tube'), 0, .1 + bob, 3.0, .24, rot=spin, alpha=1 - morph))
        if morph > 0: items.append(lay(A('wood'), 0, .1 + bob, 3.0, .24, rot=spin, alpha=morph))
        f = draw_anchored(f, cam, items)
        # shavings
        if 3.9 < u < 6.4:
            r = np.random.default_rng(int(u * 30))
            for k in range(26):
                x = W / 2 + r.normal(0, 140); y = H * .47 + r.normal(0, 60) - (u * 90 % 120)
                cv2.ellipse(f, (int(x), int(y)), (int(r.uniform(5, 12)), int(r.uniform(2, 6))), r.uniform(0, 180), 0, 250,
                            tuple(float(v) for v in ORANGE * r.uniform(.6, 1.0)), 2, cv2.LINE_AA)
        if 4.3 < u < 5.9: f = glow_spot(f, W / 2, H * .47, 160, (1, .6, .25), .35 * math.sin((u - 4.3) / 1.6 * math.pi))
        # banner unfurls, then the name is stamped on it
        bt = u - (t_name - 1.0)
        if bt > 0:
            spr = A('stSTETH'); e = ease_out(bt / .5)
            cut = max(1, int(spr.shape[1] * e))
            f = blit(f, spr[:, :cut], W / 2 - spr.shape[1] * .5 * .95 + cut * .5 * .95, H * .3, .95, -3, 1.0, shadow=(8, 12, 8, .5))
        f = stamp(f, A('stSTETH_t'), W / 2, H * .3, u - t_name, 520, rot=-3, seed=11)
        if q < .3: f = mblur(f, 140 * (1 - q / .3), 0)
        if u > 9.2: f = mblur(f, 160 * ease_in((u - 9.2) / .8), 0)
    f = draw_captions(f, 4, u)
    return finish(f, u)

# ------------------------------------------------------------ scene 6: the nephew's diagnosis -> pull back to the row
def scene6(u):
    t_tb = ctime(5, 'tuberculosis') - .1
    if u < 9.0:
        sx, sy = impact_shake(u, t_tb + .13, 14)
        q = u
        if u < 4.0: cx, cy, cz = lerp(-.3, .1, u / 4), -.05, lerp(-.2, .6, ease_io(u / 4))
        else:
            e = ease_io((u - 4.0) / 1.4); cx, cy, cz = lerp(.1, .05, e), lerp(-.05, .25, e), lerp(.6, 2.5, e)
        if u > 8.55:
            p = ease_in((u - 8.55) / .45); cz -= 6 * p; cy -= .8 * p
        cam = Cam(cx + sx * .002, cy + sy * .002, cz, F=900, focus=max(.6, 4.0 - cz), dof=1.0)
        f = backdrop('bedroom', cx, cy, 1.03, par=.08)
        items = [lay(A('sickbed'), .3, .55, 4.0, 1.0)]
        items.append(figure_layer('young', -.8, 3.8, 1.8, lean=70))
        f = draw_anchored(f, cam, items)
        p = cam.project(.05, .3, 3.85)
        if p:
            sc = 900 * .42 / p[2] / A('wood').shape[1]
            f = blit(f, A('wood'), p[0], p[1], sc, -80, 1.0, shadow=(6, 10, 6, .5))
            if 4.6 < u < 7.0:  # crackle ripples travelling up the stethoscope
                for k in range(3):
                    d = ((u - 4.6) * 1.2 + k * .33) % 1.0
                    rx = p[0] + math.cos(math.radians(-62 + 180)) * 0 + (d - .5) * 220 * sc * 2.2 * .45
                    ry = p[1] - (d - .5) * 420 * sc * .9
                    m = np.zeros((H, W), np.float32); cv2.circle(m, (int(rx), int(ry)), int(18 + 30 * d), 1, 3)
                    f = f + blur(m, 3)[..., None] * np.array([1, .8, .6], np.float32) * .8 * (1 - d)
        f = glow_spot(f, W * .82, H * .55, 90, (1, .6, .3), .5)
        f = f * .92
        # orange strip drops, then TUBERCULOSIS is stamped onto it
        st = u - (t_tb - .55)
        if st > 0:
            e = min(1.0, ease_out(st / .35) * 1.0)
            y = lerp(-120, H * .3, e) + (8 * math.sin(st * 20) * math.exp(-st * 6) if st > .35 else 0)
            f = blit(f, A('stTB_strip'), W / 2 + sx, y + sy, .98, 2, 1.0, shadow=(8, 12, 8, .5))
        f = stamp(f, A('stTB_t'), W / 2 + sx, H * .3 + sy, u - t_tb, 560, rot=2, seed=13)
        if u > 8.55: f = zoom_blur(f, ease_in((u - 8.55) / .45) * 1.6)
    else:
        q = (u - 9.0) / 1.0
        cam = Cam(0, -.1, lerp(-4.0, 1.0, ease_out(q)), F=900, focus=4.0, dof=1.0, roll=lerp(4, -2, q))
        f = backdrop('row_backdrop', 0, 0, 1.08)
        items = [figure_layer('doc_white', x, z, 1.9) for x, z in ROW]
        f = draw_anchored(f, cam, items)
        if u < 9.3: f = zoom_blur(f, (9.3 - u) / .3 * 1.8)
        f = f * (1 - .9 * ease_in((u - 9.6) / .4))
    f = draw_captions(f, 5, u)
    return finish(f, u, enter=(0, 120), exit_='zoom')

SCENES = [scene1, scene2, scene3, scene4, scene5, scene6]

# ------------------------------------------------------------ global look
GRAIN = None; VIG = None
def post(f, i):
    global GRAIN, VIG
    if GRAIN is None:
        GRAIN = [(np.random.default_rng(1000 + k).normal(0, 1, (H, W, 1)).astype(np.float32) * .03) for k in range(6)]
        VIG = vignette(H, W, .45, 2.2)
    f = tilt_shift(f, 5.0, .3, .47)
    f = f * np.array([1.04, .98, .88], np.float32)  # warm tungsten
    f = f * VIG + GRAIN[i % 6]
    r = np.random.default_rng(i)
    for _ in range(3):  # flickering dust and hairs
        x, y = int(r.uniform(0, W)), int(r.uniform(0, H))
        if r.random() < .5: cv2.circle(f, (x, y), int(r.uniform(1, 3)), (.95, .92, .85) if r.random() < .5 else (.1, .08, .06), -1, cv2.LINE_AA)
        else: cv2.line(f, (x, y), (x + int(r.uniform(-20, 20)), y + int(r.uniform(-20, 20))), (.15, .12, .1), 1, cv2.LINE_AA)
    return np.clip(f, 0, 1)
