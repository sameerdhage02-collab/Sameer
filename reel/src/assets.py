"""Procedural stand-in images + shared drawing helpers for the stethoscope reel.
Any asset can be replaced by dropping a file into images/<name>.jpg|png."""
import os, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 720, 1280
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', 'fonts')
IMGDIR = os.path.join(HERE, 'images')
RNG = np.random.default_rng(7)

# ---------------------------------------------------------------- basics
def clamp01(x): return max(0.0, min(1.0, x))
def ease_out(x): x = clamp01(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp01(x); return x ** 3
def ease_io(x): x = clamp01(x); return x * x * (3 - 2 * x)
def ease_back(x, s=1.7):
    x = clamp01(x) - 1; return x * x * ((s + 1) * x + s) + 1
def bounce(x):
    x = clamp01(x)
    n, d = 7.5625, 2.75
    if x < 1 / d: return n * x * x
    if x < 2 / d: x -= 1.5 / d; return n * x * x + .75
    if x < 2.5 / d: x -= 2.25 / d; return n * x * x + .9375
    x -= 2.625 / d; return n * x * x + .984375
def lerp(a, b, t): return a + (b - a) * t

def noise(h, w, scale, seed=None):
    r = np.random.default_rng(seed) if seed is not None else RNG
    sm = r.random((max(2, h // scale + 3), max(2, w // scale + 3))).astype(np.float32)
    big = cv2.resize(sm, (w + 3 * scale, h + 3 * scale), interpolation=cv2.INTER_CUBIC)
    return big[scale:scale + h, scale:scale + w]

def fbm(h, w, scales=(256, 128, 64, 32), seed=0):
    out = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for i, s in enumerate(scales):
        out += noise(h, w, s, seed + i) * amp; tot += amp; amp *= .5
    return out / tot

def vgrad(h, w, top, bot):
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    return np.broadcast_to(np.array(top, np.float32) * (1 - t) + np.array(bot, np.float32) * t, (h, w, 3)).copy()

def vignette(h, w, strength=.55, power=2.2):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / math.sqrt(2)
    return (1 - strength * d ** power)[..., None]

def blur(a, s):
    if s <= .05: return a
    k = int(s * 3) * 2 + 1
    return cv2.GaussianBlur(a, (k, k), s)

def pil_layer(h, w, ss=2):
    im = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)

def pil_to_rgba(im, ss=2):
    if ss != 1: im = im.resize((im.width // ss, im.height // ss), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255

def over_full(dst, rgba):
    a = rgba[..., 3:4]; return dst * (1 - a) + rgba[..., :3] * a

def add_light(dst, mask, color, k):
    return dst + mask[..., None] * np.array(color, np.float32) * k

def bloom(img, thresh=.7, s=18, k=.5):
    b = np.clip(img - thresh, 0, None)
    return img + blur(b, s) * k

def sat(img, s):
    g = img.mean(2, keepdims=True); return g + (img - g) * s

def font(name, size, wght=None):
    path = {
        'pfi': 'PlayfairDisplay-Italic%5Bwght%5D.ttf', 'pf': 'PlayfairDisplay%5Bwght%5D.ttf',
        'lilita': 'LilitaOne-Regular.ttf', 'luckiest': 'LuckiestGuy-Regular.ttf',
        'anton': 'Anton-Regular.ttf', 'oswald': 'Oswald%5Bwght%5D.ttf', 'inter': 'Inter%5Bopsz,wght%5D.ttf'}[name]
    f = ImageFont.truetype(os.path.join(FONTS, path), size)
    if wght is not None:
        try:
            axes = f.get_variation_axes()
            vals = [wght if a.get('name', b'') in (b'Weight', 'Weight') else a['default'] for a in axes]
            f.set_variation_by_axes(vals)
        except Exception:
            pass
    return f

def load_override(name, size=None, alpha=False):
    for ext in ('.png', '.jpg', '.jpeg', '.webp'):
        p = os.path.join(IMGDIR, name + ext)
        if os.path.exists(p):
            im = Image.open(p).convert('RGBA' if alpha else 'RGB')
            if size and not alpha:  # cover fit
                tw, th = size; s = max(tw / im.width, th / im.height)
                im = im.resize((int(im.width * s + .5), int(im.height * s + .5)), Image.LANCZOS)
                l, t = (im.width - tw) // 2, (im.height - th) // 2
                im = im.crop((l, t, l + tw, t + th))
            return np.asarray(im).astype(np.float32) / 255
    return None

# ---------------------------------------------------------------- people (stylized)
def draw_person(d, x, yfeet, h, coat, skin=(205, 160, 125), seated=False, hair=(40, 28, 20),
                lean=0, collar=(235, 230, 220), gown=False, female=False):
    """Simple painterly figure on a PIL ImageDraw (supersampled coords)."""
    head = h * .13
    body_h = h * (.55 if seated else .87)
    top = yfeet - body_h
    sh = h * .14  # half shoulder width
    hx, hy = x + lean, top - head * .55
    # legs/skirt
    if gown:
        d.polygon([(x - sh * .9, top + h * .08), (x + sh * .9, top + h * .08), (x + sh * 1.5, yfeet), (x - sh * 1.4, yfeet)], fill=coat)
    else:
        d.polygon([(x - sh * .75, top + body_h * .45), (x + sh * .75, top + body_h * .45), (x + sh * .6, yfeet), (x - sh * .65, yfeet)], fill=tuple(int(c * .7) for c in coat[:3]))
    # torso
    d.polygon([(x - sh * .35 + lean * .5, top), (x + sh * .35 + lean * .5, top), (x + sh, top + h * .06), (x + sh * .85, top + body_h * .55),
               (x - sh * .85, top + body_h * .55), (x - sh, top + h * .06)], fill=coat)
    d.ellipse([x - sh, top - h * .01, x + sh, top + h * .12], fill=coat)
    if not gown:
        d.polygon([(x - sh * .22 + lean * .5, top), (x + sh * .22 + lean * .5, top), (x + lean * .5, top + h * .12)], fill=collar)
    # neck + head
    d.rectangle([hx - head * .22, top - head * .3, hx + head * .22, top + h * .01], fill=tuple(int(c * .8) for c in skin))
    d.ellipse([hx - head * .42, hy - head * .55, hx + head * .42, hy + head * .55], fill=skin)
    # shading on far side of face
    d.chord([hx - head * .42, hy - head * .55, hx + head * .42, hy + head * .55], 300, 60, fill=tuple(int(c * .72) for c in skin))
    # hair
    if female:
        d.ellipse([hx - head * .5, hy - head * .66, hx + head * .5, hy - head * .02], fill=hair)
        d.ellipse([hx - head * .2, hy - head * .95, hx + head * .3, hy - head * .45], fill=hair)
    else:
        d.chord([hx - head * .46, hy - head * .66, hx + head * .46, hy + head * .3], 180, 360, fill=hair)
        d.rectangle([hx - head * .44, hy - head * .2, hx - head * .34, hy + head * .25], fill=hair)
        d.rectangle([hx + head * .34, hy - head * .2, hx + head * .44, hy + head * .25], fill=hair)

# ---------------------------------------------------------------- scenes (stand-ins)
def lab(busy=False):
    ov = load_override('lab_busy' if busy else 'lab_empty', (820, 1440))
    if ov is not None: return ov
    h, w = 1440, 820
    img = vgrad(h, w, (.62, .38, .18), (.30, .15, .07))
    tex = fbm(h, w, (200, 90, 40, 12), 3)[..., None]
    img *= .75 + .5 * tex
    # rug / floor
    fl = int(h * .66)
    rug = vgrad(h - fl, w, (.42, .10, .07), (.22, .05, .04)) * (.8 + .4 * fbm(h - fl, w, (60, 20, 6), 9)[..., None])
    img[fl:] = rug
    im, d = pil_layer(h, w)
    S = 2
    # window (left)
    d.rectangle([30 * S, 190 * S, 270 * S, 640 * S], fill=(255, 226, 160, 255))
    for xx in (110, 190):
        d.rectangle([xx * S, 190 * S, (xx + 10) * S, 640 * S], fill=(90, 55, 30, 255))
    for yy in (340, 490):
        d.rectangle([30 * S, yy * S, 270 * S, (yy + 10) * S], fill=(90, 55, 30, 255))
    d.rectangle([20 * S, 180 * S, 280 * S, 650 * S], outline=(70, 40, 20, 255), width=14 * S)
    # shelves (right)
    r = np.random.default_rng(4)
    for i, yy in enumerate((260, 400, 540, 680)):
        d.rectangle([440 * S, yy * S, 815 * S, (yy + 14) * S], fill=(70, 40, 20, 255))
        x = 450
        while x < 790:
            bw = int(r.integers(18, 40)); bh = int(r.integers(40, 110))
            col = [(150, 95, 35), (70, 100, 60), (120, 60, 30), (190, 160, 110), (60, 45, 35)][int(r.integers(0, 5))]
            if r.random() < .5:
                d.rounded_rectangle([x * S, (yy - bh) * S, (x + bw) * S, yy * S], radius=6 * S, fill=col + (255,))
                d.rectangle([(x + bw * .5 - 4) * S, (yy - bh - 12) * S, (x + bw * .5 + 4) * S, (yy - bh) * S], fill=col + (255,))
            else:
                d.ellipse([x * S, (yy - bw) * S, (x + bw) * S, yy * S], fill=col + (255,))
            d.line([(x + 5) * S, (yy - bh + 8) * S, (x + 5) * S, (yy - 8) * S], fill=(255, 230, 190, 140), width=3 * S)
            x += bw + int(r.integers(4, 16))
    # desk + lamp + instruments
    d.polygon([(0, 930 * S), (820 * S, 900 * S), (820 * S, 1010 * S), (0, 1050 * S)], fill=(60, 32, 16, 255))
    d.polygon([(0, 920 * S), (820 * S, 890 * S), (820 * S, 905 * S), (0, 935 * S)], fill=(150, 95, 50, 255))
    d.rectangle([60 * S, 1040 * S, 100 * S, 1440 * S], fill=(45, 24, 12, 255))
    d.rectangle([700 * S, 1000 * S, 740 * S, 1440 * S], fill=(45, 24, 12, 255))
    d.polygon([(300 * S, 900 * S), (330 * S, 900 * S), (318 * S, 780 * S), (312 * S, 780 * S)], fill=(160, 120, 50, 255))
    d.polygon([(270 * S, 790 * S), (360 * S, 790 * S), (335 * S, 740 * S), (295 * S, 740 * S)], fill=(40, 70, 40, 255))
    for bx, by, rr in ((470, 880, 26), (540, 870, 18), (600, 885, 30)):
        d.ellipse([(bx - rr) * S, (by - rr * 2) * S, (bx + rr) * S, by * S], fill=(170, 130, 60, 255))
    d.rectangle([150 * S, 870 * S, 240 * S, 905 * S], fill=(225, 210, 175, 255))
    # pendant lamp
    d.line([(560 * S, 0), (560 * S, 120 * S)], fill=(30, 20, 10, 255), width=4 * S)
    d.polygon([(520 * S, 170 * S), (600 * S, 170 * S), (575 * S, 120 * S), (545 * S, 120 * S)], fill=(60, 45, 25, 255))
    if busy:
        draw_person(d, 270 * S, 1120 * S, 520 * S, (70, 52, 38, 255), seated=True)
        draw_person(d, 610 * S, 1250 * S, 700 * S, (95, 80, 60, 255), lean=-6 * S)
        draw_person(d, 470 * S, 960 * S, 420 * S, (55, 40, 30, 255), seated=True, hair=(70, 70, 70))
        draw_person(d, 130 * S, 1400 * S, 640 * S, (60, 45, 35, 255), seated=True, hair=(200, 200, 195), skin=(220, 180, 150))
    lay = pil_to_rgba(im)
    img = over_full(img, lay)
    # light shaft from window + lamp glows
    m = np.zeros((h, w), np.float32)
    cv2.fillPoly(m, [np.array([[30, 190], [270, 190], [620, 1440], [120, 1440]], np.int32)], 1)
    img = add_light(img, blur(m, 40), (1, .8, .5), .35)
    g = np.zeros((h, w), np.float32)
    cv2.circle(g, (315, 790), 60, 1, -1); cv2.circle(g, (560, 175), 45, 1, -1)
    img = add_light(img, blur(g, 60), (1, .75, .35), 1.2)
    img = blur(img, 1.0)
    img = bloom(img, .75, 25, .6)
    img *= vignette(h, w, .55)
    return np.clip(img, 0, 1)

def stone_wall():
    ov = load_override('stone_wall', (800, 1400))
    if ov is not None: return ov
    h, w = 1400, 800
    r = np.random.default_rng(11)
    base = np.full((h, w), .26, np.float32)
    stones = np.zeros((h, w), np.float32)
    y = 0; row = 0
    while y < h:
        rh = int(r.integers(70, 95)); x = -int(r.integers(0, 120))
        while x < w:
            sw = int(r.integers(100, 170)); v = r.uniform(.42, .60)
            cv2.rectangle(stones, (x + 4, y + 4), (x + sw - 4, y + rh - 4), v, -1)
            x += sw
        y += rh; row += 1
    mask = (stones > 0).astype(np.float32)
    mb = blur(mask, 4)
    bevel = np.gradient(mb, axis=0) * -6 + np.gradient(mb, axis=1) * -3
    tex = fbm(h, w, (64, 24, 8, 3), 21)
    img = base * (1 - mask) + stones * mb + (tex - .5) * .18 + bevel * .25
    img = img - .12 * (1 - mb)
    img = np.repeat(img[..., None], 3, 2)
    # arched window
    win = np.zeros((h, w), np.float32)
    cv2.rectangle(win, (260, 230), (540, 520), 1, -1); cv2.ellipse(win, (400, 230), (140, 130), 0, 180, 360, 1, -1)
    bars = np.zeros((h, w), np.float32)
    for xx in (320, 380, 440, 500):
        cv2.rectangle(bars, (xx - 7, 90), (xx + 7, 520), 1, -1)
    cv2.rectangle(bars, (260, 330), (540, 342), 1, -1)
    winm = np.clip(win - bars, 0, 1)
    frame = blur(win, 8) - win
    img = img * (1 - win[..., None]) + winm[..., None] * 1.0 + (win - winm)[..., None] * .1
    img -= np.clip(frame, 0, 1)[..., None] * .3
    # rays
    rays = np.zeros((h, w), np.float32)
    for k in range(6):
        x0 = 280 + k * 50
        cv2.fillPoly(rays, [np.array([[x0, 300], [x0 + 22, 300], [x0 + 22 + 260 + k * 30, h], [x0 - 60 + k * 40, h]], np.int32)], .5 + .5 * r.random())
    rays = blur(rays, 22) * (1 - win)
    img = add_light(img, rays, (1, 1, 1), .28)
    g = np.zeros((h, w), np.float32); cv2.ellipse(g, (400, 380), (260, 300), 0, 0, 360, 1, -1)
    img = add_light(img, blur(g, 90), (1, 1, 1), .25)
    img *= vignette(h, w, .75, 1.8)
    return np.clip(blur(img, .8), 0, 1)

def wooden_stethoscope(hh=440):
    ov = load_override('stethoscope_cutout', alpha=True)
    if ov is not None: return ov
    w = 110; h = hh
    out = np.zeros((h, w, 4), np.float32)
    ys = np.arange(h)
    def hw(y):
        f = y / h
        if f < .06: return 46
        if f < .09: return 26
        if f < .80: return 20 + 3 * math.sin(f * 40) * (f > .7)
        return 20 + (f - .80) / .20 * 30
    grain = noise(h, 8, 3, 5)
    for y in ys:
        r = hw(y); xs = np.arange(w) - w / 2
        u = xs / r
        a = np.clip((r - np.abs(xs)) * .9, 0, 1)
        sh = np.sqrt(np.clip(1 - u ** 2, 0, 1))
        light = .45 + .55 * sh + .35 * np.exp(-((u + .45) / .18) ** 2)
        gstripe = .95 + .08 * np.sin(u * 9 + grain[y, (np.abs(u) * 7).clip(0, 7).astype(int)] * 6)
        col = np.array([.60, .38, .20], np.float32)[None] * (light * gstripe)[:, None]
        if any(abs(y - g0) < 3 for g0 in (int(h * .06), int(h * .09), int(h * .78), int(h * .80))):
            col *= .55
        out[y, :, :3] = col; out[y, :, 3] = a
    # earpiece top face
    return np.clip(out, 0, 1)

def portrait(old=False):
    ov = load_override('laennec_old' if old else 'laennec_young', (420, 420))
    if ov is not None: return ov
    s = 420
    img = vgrad(s, s, (.62, .62, .60), (.38, .38, .37)) * (.85 + .3 * fbm(s, s, (120, 40), 31)[..., None])
    im, d = pil_layer(s, s)
    S = 2; cx = 210
    # shoulders / coat
    d.ellipse([(cx - 190) * S, 300 * S, (cx + 190) * S, 560 * S], fill=(28, 28, 28, 255))
    d.polygon([(cx - 55) * S, 285 * S, (cx + 55) * S, 285 * S, (cx + 80) * S, 420 * S, (cx - 80) * S, 420 * S], fill=(225, 225, 220, 255))
    d.polygon([(cx - 22) * S, 300 * S, (cx + 22) * S, 300 * S, (cx + 30) * S, 380 * S, cx * S, 400 * S, (cx - 30) * S, 380 * S], fill=(190, 190, 185, 255))
    d.polygon([(cx - 80) * S, 330 * S, (cx - 10) * S, 420 * S, (cx - 100) * S, 420 * S], fill=(50, 50, 50, 255))
    d.polygon([(cx + 80) * S, 330 * S, (cx + 10) * S, 420 * S, (cx + 100) * S, 420 * S], fill=(50, 50, 50, 255))
    fw = 62 if old else 70
    skin = (175, 175, 172) if old else (165, 162, 158)
    d.rectangle([(cx - 30) * S, 230 * S, (cx + 30) * S, 300 * S], fill=(130, 130, 128, 255))
    d.ellipse([(cx - fw) * S, 110 * S, (cx + fw) * S, 285 * S], fill=skin + (255,))
    hair = (40, 40, 40) if not old else (70, 70, 70)
    d.chord([(cx - fw - 8) * S, (95 if not old else 105) * S, (cx + fw + 8) * S, 230 * S], 180, 360, fill=hair + (255,))
    if old:
        d.ellipse([(cx - 40) * S, 100 * S, (cx + 40) * S, 135 * S], fill=skin + (255,))
    d.rectangle([(cx - fw - 4) * S, 160 * S, (cx - fw + 10) * S, 235 * S], fill=hair + (255,))
    d.rectangle([(cx + fw - 10) * S, 160 * S, (cx + fw + 4) * S, 235 * S], fill=hair + (255,))
    eye = 70 if old else 85
    for ex in (cx - 26, cx + 26):
        d.ellipse([(ex - 14) * S, 175 * S, (ex + 14) * S, 195 * S], fill=(eye, eye, eye, 255))
        d.ellipse([(ex - 5) * S, 181 * S, (ex + 5) * S, 190 * S], fill=(25, 25, 25, 255))
    d.line([(cx - 40) * S, 166 * S, (cx - 14) * S, 163 * S], fill=(50, 50, 50, 255), width=4 * S)
    d.line([(cx + 14) * S, 163 * S, (cx + 40) * S, 166 * S], fill=(50, 50, 50, 255), width=4 * S)
    d.polygon([(cx - 4) * S, 190 * S, (cx + 2) * S, 190 * S, (cx + 10) * S, 228 * S, (cx - 8) * S, 230 * S], fill=(135, 135, 132, 255))
    d.line([(cx - 18) * S, 252 * S, (cx + 18) * S, 252 * S], fill=(95, 90, 90, 255), width=3 * S)
    lay = pil_to_rgba(im)
    img = over_full(img, lay)
    # side light shading
    xx = np.linspace(0, 1, s, dtype=np.float32)[None, :, None]
    img *= .8 + .35 * (1 - xx)
    img = blur(img, 1.6)
    img += (noise(s, s, 1, 3)[..., None] - .5) * .08
    img *= vignette(s, s, .6)
    img = img * np.array([1.0, .97, .9], np.float32)  # slight sepia
    return np.clip(img, 0, 1)

def ward(close=False):
    ov = load_override('listen' if close else 'ward', (820, 1440))
    if ov is not None: return ov
    h, w = 1440, 820
    img = vgrad(h, w, (.36, .38, .40), (.20, .20, .21)) * (.8 + .4 * fbm(h, w, (160, 60, 16), 41)[..., None])
    fl = 960
    floor = vgrad(h - fl, w, (.24, .18, .13), (.12, .09, .07))
    for i in range(0, w + 400, 70):
        cv2.line(floor, (i, 0), (int((i - w / 2) * 2.4 + w / 2), h - fl), (.08, .06, .05), 2)
    img[fl:] = floor
    im, d = pil_layer(h, w); S = 2
    for wx in (90, 520):
        d.rectangle([wx * S, 260 * S, (wx + 200) * S, 700 * S], fill=(225, 230, 235, 255))
        d.pieslice([wx * S, 160 * S, (wx + 200) * S, 360 * S], 180, 360, fill=(225, 230, 235, 255))
        d.rectangle([(wx + 95) * S, 160 * S, (wx + 105) * S, 700 * S], fill=(60, 60, 60, 255))
        d.rectangle([wx * S, 440 * S, (wx + 200) * S, 450 * S], fill=(60, 60, 60, 255))
    # background beds
    for bx, by, bw in ((40, 900, 160), (600, 880, 190)):
        d.rectangle([bx * S, (by - 50) * S, (bx + bw) * S, by * S], fill=(200, 200, 195, 255))
        d.rectangle([bx * S, (by - 120) * S, (bx + 12) * S, (by + 30) * S], fill=(50, 45, 40, 255))
    # main bed
    if close:
        d.polygon([(300 * S, 1050 * S), (820 * S, 1000 * S), (820 * S, 1300 * S), (260 * S, 1350 * S)], fill=(225, 222, 212, 255))
        draw_person(d, 600 * S, 1150 * S, 760 * S, (230, 228, 220, 255), seated=True, gown=True, female=True, hair=(60, 40, 25), skin=(225, 185, 155))
        draw_person(d, 250 * S, 1440 * S, 980 * S, (35, 33, 38, 255), lean=150 * S)
        # paper tube from doctor ear to patient chest
        d.line([(420 * S, 720 * S), (560 * S, 840 * S)], fill=(230, 215, 180, 255), width=26 * S)
        d.line([(420 * S, 712 * S), (560 * S, 832 * S)], fill=(250, 240, 215, 255), width=6 * S)
    else:
        d.polygon([(330 * S, 1010 * S), (820 * S, 980 * S), (820 * S, 1140 * S), (300 * S, 1180 * S)], fill=(225, 222, 212, 255))
        d.rectangle([310 * S, 880 * S, 330 * S, 1200 * S], fill=(55, 48, 40, 255))
        draw_person(d, 560 * S, 1050 * S, 620 * S, (232, 230, 222, 255), seated=True, gown=True, female=True, hair=(60, 40, 25), skin=(225, 185, 155))
        draw_person(d, 210 * S, 1230 * S, 820 * S, (35, 33, 38, 255), lean=-8 * S)
    # candle
    cx, cy = (720, 1000) if close else (740, 960)
    d.rectangle([(cx - 30) * S, cy * S, (cx + 30) * S, (cy + 10) * S], fill=(90, 70, 40, 255))
    d.rectangle([(cx - 7) * S, (cy - 60) * S, (cx + 7) * S, cy * S], fill=(235, 225, 200, 255))
    d.ellipse([(cx - 6) * S, (cy - 85) * S, (cx + 6) * S, (cy - 60) * S], fill=(255, 220, 140, 255))
    lay = pil_to_rgba(im)
    img = over_full(img, lay)
    m = np.zeros((h, w), np.float32)
    for wx in (90, 520):
        cv2.fillPoly(m, [np.array([[wx, 260], [wx + 200, 260], [wx + 420, 1440], [wx + 120, 1440]], np.int32)], 1)
    img = add_light(img, blur(m, 45), (.8, .85, .9), .22)
    g = np.zeros((h, w), np.float32); cv2.circle(g, (cx, cy - 72), 40, 1, -1)
    img = add_light(img, blur(g, 110), (1, .65, .3), 1.4)
    img = blur(img, 1.2)
    img = sat(img, .75)
    img *= vignette(h, w, .65)
    return np.clip(bloom(img, .8, 20, .4), 0, 1)

def wood_table():
    ov = load_override('table', (800, 1400))
    if ov is not None: return ov
    h, w = 1400, 800
    img = np.zeros((h, w), np.float32)
    ph = 130
    for i, y in enumerate(range(0, h, ph)):
        base = .30 + .06 * np.random.default_rng(i).random()
        gr = noise(ph, w // 30 + 4, 1, 100 + i)
        gr = cv2.resize(noise(ph // 3 + 3, w // 40 + 3, 1, 100 + i), (w, ph), interpolation=cv2.INTER_CUBIC)
        fine = cv2.resize(np.random.default_rng(200 + i).random((ph, w // 25)).astype(np.float32), (w, ph), interpolation=cv2.INTER_LINEAR)
        plank = base + (gr - .5) * .12 + (fine - .5) * .08
        img[y:y + ph] = plank[:h - y]
        img[y:y + 4] = .12
    img = np.repeat(img[..., None], 3, 2) * np.array([1.0, .98, .95], np.float32)
    img *= vignette(h, w, .7)
    return np.clip(img, 0, 1)

def grid_paper(base, line, step=40, crumple=.06, seed=1, h=1400, w=820, lw=1):
    img = np.broadcast_to(np.array(base, np.float32), (h, w, 3)).copy()
    n = fbm(h, w, (300, 120, 50), seed)
    gx = np.gradient(blur(n, 6), axis=1) * 30
    img *= (1 + (n - .5) * crumple * .6 + gx * crumple * 1.2)[..., None]
    lines = np.zeros((h, w), np.float32)
    for x in range(0, w, step): cv2.line(lines, (x, 0), (x, h), 1, lw)
    for y in range(0, h, step): cv2.line(lines, (0, y), (w, y), 1, lw)
    lines = blur(lines, .6)
    img = img * (1 - lines[..., None]) + np.array(line, np.float32) * lines[..., None]
    img += (noise(h, w, 1, seed + 50)[..., None] - .5) * .03
    return np.clip(img, 0, 1)

def orange_paper():
    img = grid_paper((.80, .45, .14), (.74, .40, .12), 46, .1, 3)
    h, w = img.shape[:2]
    # radial warm glow
    img = add_light(img, blur(cv2.circle(np.zeros((h, w), np.float32), (520, 300), 380, 1, -1), 150), (1, .7, .3), .35)
    img *= vignette(h, w, .65)
    return np.clip(img, 0, 1)

def window_shadow(h=1600, w=1200):
    m = np.ones((h, w), np.float32)
    pw, ph = 230, 300
    for i in range(3):
        for j in range(3):
            x0 = 200 + i * (pw + 40); y0 = 200 + j * (ph + 40)
            cv2.rectangle(m, (x0, y0), (x0 + pw, y0 + ph), 0, -1)
    return 1 - m  # 1 = light pane

def chalkboard():
    h, w = 1400, 820
    n = fbm(h, w, (260, 120, 40, 10), 61)
    sm = blur((noise(h, w, 90, 62) > .62).astype(np.float32), 50)
    v = .10 + (n - .5) * .06 + sm * .05
    img = np.repeat(v[..., None], 3, 2)
    img += (noise(h, w, 1, 63)[..., None] - .5) * .03
    img *= vignette(h, w, .5)
    return np.clip(img, 0, 1)

def navy():
    h, w = 1400, 820
    n = fbm(h, w, (200, 80, 20, 5), 71)
    img = np.array([.035, .06, .11], np.float32) * (.6 + .8 * n)[..., None]
    return np.clip(img * vignette(h, w, .5), 0, 1)

def torn_sheet(color, h, w, poly_line, below, seed):
    """RGBA torn paper occupying one side of a jagged line."""
    r = np.random.default_rng(seed)
    (x0, y0), (x1, y1) = poly_line
    n = 80
    pts = []
    for i in range(n + 1):
        t = i / n
        nx, ny = -(y1 - y0), (x1 - x0); L = math.hypot(nx, ny); nx /= L; ny /= L
        j = r.normal(0, 4) + 10 * math.sin(t * 13 + seed)
        pts.append((x0 + (x1 - x0) * t + nx * j, y0 + (y1 - y0) * t + ny * j))
    if below:
        poly = pts + [(w + 50, h + 50), (-50, h + 50)]
    else:
        poly = pts + [(w + 50, -50), (-50, -50)]
    m = np.zeros((h, w), np.float32)
    cv2.fillPoly(m, [np.array(poly, np.int32)], 1)
    m = blur(m, .8)
    edge = np.clip(blur(m, 3) * 2 - m * 2 + (m * (1 - blur(m, 6))) * 3, 0, 1)
    tex = fbm(h, w, (120, 40, 8), seed)[..., None]
    col = np.array(color, np.float32) * (.75 + .5 * tex)
    col = col * (1 - edge[..., None] * .8) + edge[..., None] * .85
    return np.dstack([np.clip(col, 0, 1), m])

def white_paper():
    img = grid_paper((.90, .90, .90), (.55, .56, .58), 52, .18, 81, lw=1)
    h, w = img.shape[:2]
    return np.clip(img * vignette(h, w, .45), 0, 1)

def clinic_fisheye():
    ov = load_override('modern', (720, 1280))
    if ov is not None: return ov
    h, w = 1280, 720
    img = vgrad(h, w, (.62, .72, .80), (.48, .58, .66))
    t = np.zeros((h, w), np.float32)
    for x in range(0, w, 60): cv2.line(t, (x, 0), (x, h), 1, 2)
    for y in range(0, h, 60): cv2.line(t, (0, y), (w, y), 1, 2)
    img -= t[..., None] * .05
    im, d = pil_layer(h, w); S = 2
    d.rectangle([520 * S, 150 * S, 720 * S, 700 * S], fill=(200, 210, 215, 255))
    d.rectangle([0, 900 * S, 720 * S, 1280 * S], fill=(235, 238, 240, 255))
    # doctor: white coat, big head
    d.ellipse([60 * S, 700 * S, 660 * S, 1500 * S], fill=(245, 246, 248, 255))
    d.polygon([(300 * S, 720 * S), (420 * S, 720 * S), (360 * S, 900 * S)], fill=(110, 150, 190, 255))
    d.rectangle([310 * S, 560 * S, 410 * S, 740 * S], fill=(205, 150, 120, 255))
    d.ellipse([200 * S, 230 * S, 520 * S, 640 * S], fill=(228, 175, 140, 255))
    d.chord([190 * S, 200 * S, 530 * S, 470 * S], 180, 360, fill=(60, 40, 28, 255))
    for ex in (300, 420):
        d.ellipse([(ex - 22) * S, 410 * S, (ex + 22) * S, 440 * S], fill=(255, 255, 255, 255))
        d.ellipse([(ex - 10) * S, 414 * S, (ex + 10) * S, 436 * S], fill=(60, 40, 30, 255))
    d.chord([290 * S, 470 * S, 430 * S, 580 * S], 0, 180, fill=(250, 250, 250, 255))
    d.arc([290 * S, 470 * S, 430 * S, 580 * S], 0, 180, fill=(140, 60, 60, 255), width=5 * S)
    # stethoscope around neck + earpieces
    d.arc([180 * S, 600 * S, 540 * S, 980 * S], 20, 160, fill=(25, 25, 28, 255), width=18 * S)
    d.line([(205 * S, 520 * S), (230 * S, 700 * S)], fill=(150, 150, 155, 255), width=10 * S)
    d.line([(515 * S, 520 * S), (490 * S, 700 * S)], fill=(150, 150, 155, 255), width=10 * S)
    # hand + chestpiece towards camera
    d.ellipse([380 * S, 860 * S, 640 * S, 1120 * S], fill=(228, 175, 140, 255))
    d.ellipse([400 * S, 820 * S, 620 * S, 1040 * S], fill=(200, 205, 210, 255))
    d.ellipse([430 * S, 850 * S, 590 * S, 1010 * S], fill=(25, 25, 28, 255))
    d.ellipse([450 * S, 870 * S, 570 * S, 990 * S], fill=(170, 175, 180, 255))
    d.line([(510 * S, 820 * S), (470 * S, 760 * S)], fill=(25, 25, 28, 255), width=18 * S)
    lay = pil_to_rgba(im)
    lay = np.roll(lay, 150, 0); lay[:150] = 0
    img = over_full(img, lay)
    img = blur(img, 1.0)
    # fisheye barrel distortion
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (x - w / 2) / (w / 2), (y - h / 2) / (w / 2)
    r2 = nx * nx + ny * ny
    k = 1 / (1 + .2 * r2)
    mx, my = nx * k * (w / 2) + w / 2, ny * k * (w / 2) + h / 2
    img = cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    img *= vignette(h, w, .45)
    return np.clip(img, 0, 1)

# ---------------------------------------------------------------- evolution objects
def _bez(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]

def paper_tube(h=420):
    ov = load_override('evo_paper', alpha=True)
    if ov is not None: return ov
    w = 90; out = np.zeros((h, w, 4), np.float32)
    xs = np.arange(w) - w / 2; r = 30; u = xs / r
    a = np.clip((r - np.abs(xs)) * .9, 0, 1)
    sh = np.sqrt(np.clip(1 - u ** 2, 0, 1))
    light = .55 + .45 * sh + .3 * np.exp(-((u + .4) / .2) ** 2)
    for y in range(h):
        spiral = .93 + .07 * (np.abs(((y + xs * 1.6) % 60) - 30) < 1.5)
        out[y, :, :3] = np.array([.93, .87, .72])[None] * (light * spiral)[:, None]
        out[y, :, 3] = a if 8 < y < h - 8 else a * .0
    cv2.ellipse(out, (w // 2, 12), (30, 8), 0, 0, 360, (.55, .5, .4, 1), -1)
    cv2.ellipse(out, (w // 2, h - 12), (30, 8), 0, 0, 180, (.85, .8, .66, 1), -1)
    return np.clip(out, 0, 1)

def binaural(h=440, modern=False):
    ov = load_override('evo_modern' if modern else 'evo_binaural', alpha=True)
    if ov is not None: return ov
    w = 200; S = 3
    im, d = pil_layer(h, w, S)
    tube = (28, 28, 30, 255) if modern else (150, 35, 28, 255)
    metal = (175, 178, 182, 255) if modern else (190, 160, 90, 255)
    cx = w / 2
    # earpieces / headset
    if modern:
        pts = _bez((cx - 60, 30), (cx - 75, 110), (cx - 18, 175)); pts2 = _bez((cx + 60, 30), (cx + 75, 110), (cx + 18, 175))
    else:
        pts = _bez((cx - 55, 30), (cx - 50, 100), (cx - 14, 170)); pts2 = _bez((cx + 55, 30), (cx + 50, 100), (cx + 14, 170))
    for p in (pts, pts2):
        d.line([(x * S, y * S) for x, y in p], fill=metal, width=8 * S, joint='curve')
        ex, ey = p[0]; d.ellipse([(ex - 9) * S, (ey - 12) * S, (ex + 9) * S, (ey + 4) * S], fill=(20, 20, 20, 255))
    # rubber tubes to Y
    yj = h * .55
    for sgn in (-1, 1):
        p = _bez((cx + sgn * 14, 168), (cx + sgn * 30, (168 + yj) / 2), (cx, yj))
        d.line([(x * S, y * S) for x, y in p], fill=tube, width=11 * S, joint='curve')
    p = _bez((cx, yj), (cx + 25, (yj + h - 70) / 2), (cx, h - 70))
    d.line([(x * S, y * S) for x, y in p], fill=tube, width=12 * S, joint='curve')
    # chest piece
    cr = 34 if modern else 28
    d.ellipse([(cx - cr) * S, (h - 70 - 6) * S, (cx + cr) * S, (h - 70 + 2 * cr - 6) * S], fill=metal)
    d.ellipse([(cx - cr + 7) * S, (h - 70 + 1) * S, (cx + cr - 7) * S, (h - 70 + 2 * cr - 13) * S], fill=(225, 228, 230, 255) if modern else (220, 195, 130, 255))
    d.ellipse([(cx - cr + 12) * S, (h - 70 + 6) * S, (cx - 4) * S, (h - 70 + cr) * S], fill=(255, 255, 255, 160))
    out = pil_to_rgba(im, S)
    # add highlights on tubes
    hl = blur(out[..., 3], 2) * 0
    return np.clip(out, 0, 1)
