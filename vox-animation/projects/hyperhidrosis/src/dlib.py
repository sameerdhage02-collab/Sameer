"""Paper-diorama toolkit: newsprint textures, halftone cutout figures, torn edges,
letterpress stamps, a 2.5D layered camera and the compositing helpers."""
import os, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'reel', 'fonts'))

ORANGE = np.array([.86, .38, .11], np.float32)
PAPER = np.array([.86, .79, .66], np.float32)
INK = np.array([.13, .11, .09], np.float32)
WHITE_P = np.array([.94, .92, .86], np.float32)

# ------------------------------------------------------------ math
def clamp01(x): return max(0.0, min(1.0, float(x)))
def lerp(a, b, t): return a + (b - a) * t
def ease_out(x): x = clamp01(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp01(x); return x ** 3
def ease_io(x): x = clamp01(x); return x * x * (3 - 2 * x)
def ease_io5(x): x = clamp01(x); return x * x * x * (x * (6 * x - 15) + 10)
def ease_back(x, s=1.8): x = clamp01(x) - 1; return x * x * ((s + 1) * x + s) + 1
def smooth(a, b, x): return ease_io((x - a) / (b - a)) if b != a else float(x >= a)

def noise(h, w, scale, seed):
    r = np.random.default_rng(seed)
    sm = r.random((max(2, h // scale + 3), max(2, w // scale + 3))).astype(np.float32)
    big = cv2.resize(sm, (w + 3 * scale, h + 3 * scale), interpolation=cv2.INTER_CUBIC)
    return big[scale:scale + h, scale:scale + w]

def fbm(h, w, scales, seed):
    out = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for i, s in enumerate(scales):
        out += noise(h, w, s, seed + i * 17) * amp; tot += amp; amp *= .55
    return out / tot

def blur(a, s):
    if s <= .25: return a
    k = int(s * 3) * 2 + 1
    return cv2.GaussianBlur(a, (k, k), s)

def vignette(h, w, strength=.55, power=2.2):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / math.sqrt(2)
    return (1 - strength * d ** power)[..., None]

def font(name, size, wght=None):
    path = {'anton': 'Anton-Regular.ttf', 'oswald': 'Oswald%5Bwght%5D.ttf', 'inter': 'Inter%5Bopsz,wght%5D.ttf',
            'pfi': 'PlayfairDisplay-Italic%5Bwght%5D.ttf', 'pf': 'PlayfairDisplay%5Bwght%5D.ttf',
            'elite': 'SpecialElite-Regular.ttf', 'bebas': 'BebasNeue-Regular.ttf'}[name]
    f = ImageFont.truetype(os.path.join(FONTS, path), size)
    if wght is not None:
        try:
            axes = f.get_variation_axes()
            f.set_variation_by_axes([wght if a.get('name') in (b'Weight', 'Weight') else a['default'] for a in axes])
        except Exception:
            pass
    return f

# ------------------------------------------------------------ paper
def halftone(dark, cell=5.0, angle=45):
    """dark: 0..1 ink coverage -> antialiased dot mask."""
    h, w = dark.shape
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(angle)
    u = (x * math.cos(a) + y * math.sin(a)) / cell
    v = (-x * math.sin(a) + y * math.cos(a)) / cell
    du, dv = u - np.round(u), v - np.round(v)
    d = np.sqrt(du * du + dv * dv)  # 0..0.707
    r = np.sqrt(np.clip(dark, 0, 1)) * .62
    return np.clip((r - d) * cell * 1.2 + .5, 0, 1)

def newsprint(h, w, seed, tone=1.0, columns=True, density=1.0):
    r = np.random.default_rng(seed)
    base = PAPER * tone
    img = np.broadcast_to(base, (h, w, 3)).copy()
    stain = fbm(h, w, (220, 90, 30), seed)
    img *= (0.86 + .28 * stain)[..., None]
    brown = blur((noise(h, w, 120, seed + 5) > .7).astype(np.float32), 40)
    img *= (1 - .18 * brown)[..., None] * np.array([1, .97, .9], np.float32)
    if columns:
        m = np.zeros((h, w), np.float32)
        colw = int(r.integers(110, 150)); gap = 14; x0 = int(r.integers(-40, 0))
        while x0 < w:
            y = int(r.integers(-20, 30))
            while y < h:
                if r.random() < .06 * density:  # headline block
                    hh = int(r.integers(14, 26))
                    xx = x0
                    while xx < x0 + colw:
                        ww = int(r.integers(18, 50)); cv2.rectangle(m, (xx, y), (min(xx + ww, x0 + colw), y + hh), .9, -1); xx += ww + 8
                    y += hh + 10; continue
                if r.random() < .03 * density:  # photo block
                    ph = int(r.integers(60, 140)); cv2.rectangle(m, (x0, y), (x0 + colw, y + ph), .45, -1); y += ph + 10; continue
                xx = x0
                end = x0 + colw - (int(r.integers(0, 60)) if r.random() < .15 else 0)
                while xx < end:
                    ww = int(r.integers(6, 30)); cv2.rectangle(m, (xx, y), (min(xx + ww, end), y + 3), .55, -1); xx += ww + 4
                y += 9
            x0 += colw + gap
        m = blur(m, .7) * (.55 + .45 * noise(h, w, 3, seed + 9))
        img = img * (1 - m[..., None] * .32 * density)
    img += (noise(h, w, 1, seed + 11)[..., None] - .5) * .05
    return np.clip(img, 0, 1)

def torn_alpha(mask, seed, amt=5, rim=True):
    """Make the edge of a binary/soft mask look torn. Returns (alpha, rim)."""
    m = (mask > .5).astype(np.uint8)
    if m.sum() == 0: return mask.astype(np.float32), np.zeros_like(mask, np.float32)
    d = cv2.distanceTransform(m, cv2.DIST_L2, 3)
    n = fbm(*mask.shape, (9, 4, 2), seed)
    a = np.clip((d - n * amt) * .9, 0, 1).astype(np.float32)
    rm = np.clip(1 - (d - n * amt) / 3.5, 0, 1) * a if rim else np.zeros_like(a)
    return a, rm.astype(np.float32)

def rgba(color_img, alpha): return np.dstack([np.clip(color_img, 0, 1), np.clip(alpha, 0, 1)]).astype(np.float32)

def cutout_border(spr, px=6, seed=1, color=WHITE_P):
    """Add an off-white torn paper margin around a sprite (photo cutout look)."""
    h, w = spr.shape[:2]
    p = px + 6
    s = np.pad(spr, ((p, p), (p, p), (0, 0)))
    a = s[..., 3]
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (px * 2 + 1, px * 2 + 1))
    dil = cv2.dilate((a > .3).astype(np.uint8), k).astype(np.float32)
    ta, rim = torn_alpha(dil, seed, 3)
    base = np.broadcast_to(color, s.shape[:2] + (3,)) * (.95 + .08 * fbm(*a.shape, (20, 5), seed))[..., None]
    col = base * (1 - a[..., None]) + s[..., :3] * a[..., None]
    return rgba(col, np.maximum(ta, a))

def halftone_sprite(gray, alpha, cell=4.5, paper=WHITE_P * .97, ink=INK):
    ink_m = halftone(1 - gray, cell)
    # keep pure blacks solid
    ink_m = np.maximum(ink_m, np.clip((.18 - gray) * 8, 0, 1))
    col = paper[None, None] * (1 - ink_m[..., None]) + ink[None, None] * ink_m[..., None]
    return rgba(col, alpha)

# ------------------------------------------------------------ figures
def _L(w, h, ss=2):
    g = Image.new('L', (w * ss, h * ss), 0); a = Image.new('L', (w * ss, h * ss), 0)
    return g, a, ImageDraw.Draw(g), ImageDraw.Draw(a)

class Fig:
    """Draw a figure into grey + alpha images. Coordinates in final px; ss supersampling."""
    def __init__(s, w, h, ss=2):
        s.w, s.h, s.ss = w, h, ss
        s.g, s.a, s.dg, s.da = _L(w, h, ss)
        s.color_ops = []
    def P(s, pts): return [(x * s.ss, y * s.ss) for x, y in pts]
    def B(s, b): return [v * s.ss for v in b]
    def poly(s, pts, v): s.dg.polygon(s.P(pts), fill=int(v)); s.da.polygon(s.P(pts), fill=255)
    def ell(s, b, v): s.dg.ellipse(s.B(b), fill=int(v)); s.da.ellipse(s.B(b), fill=255)
    def rect(s, b, v): s.dg.rectangle(s.B(b), fill=int(v)); s.da.rectangle(s.B(b), fill=255)
    def line(s, pts, v, wd): s.dg.line(s.P(pts), fill=int(v), width=int(wd * s.ss), joint='curve'); s.da.line(s.P(pts), fill=255, width=int(wd * s.ss), joint='curve')
    def chord(s, b, a0, a1, v): s.dg.chord(s.B(b), a0, a1, fill=int(v)); s.da.chord(s.B(b), a0, a1, fill=255)
    def color_line(s, pts, wd, col=ORANGE): s.color_ops.append(('line', pts, wd, col))
    def color_ell(s, b, col=ORANGE): s.color_ops.append(('ell', b, col))
    def bar(s, cx, cy, ww, hh, rot=-4):
        s.color_ops.append(('bar', cx, cy, ww, hh, rot))
    def build(s, light_dir=-1, cell=4.5, border=6, seed=1, shade=.25):
        g = np.asarray(s.g.resize((s.w, s.h), Image.LANCZOS)).astype(np.float32) / 255
        a = np.asarray(s.a.resize((s.w, s.h), Image.LANCZOS)).astype(np.float32) / 255
        xx = np.linspace(0, 1, s.w, dtype=np.float32)[None]
        g = g * ((1 + shade / 2) - shade * (xx if light_dir < 0 else 1 - xx))
        g = blur(g, .8) * (.92 + .16 * fbm(s.h, s.w, (40, 10), seed))
        spr = halftone_sprite(np.clip(g, 0, 1), a, cell)
        im = Image.fromarray((spr * 255).astype(np.uint8), 'RGBA').resize((s.w * s.ss, s.h * s.ss), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        for op in s.color_ops:
            if op[0] == 'line':
                _, pts, wd, col = op; c = tuple(int(v * 255) for v in col) + (255,)
                d.line(s.P(pts), fill=c, width=int(wd * s.ss), joint='curve')
            elif op[0] == 'ell':
                _, b, col = op; d.ellipse(s.B(b), fill=tuple(int(v * 255) for v in col) + (255,))
            elif op[0] == 'bar':
                _, cx, cy, ww, hh, rot = op
                th = math.radians(rot); c, sn = math.cos(th), math.sin(th)
                pts = [(cx + dx * c - dy * sn, cy + dx * sn + dy * c) for dx, dy in ((-ww / 2, -hh / 2), (ww / 2, -hh / 2), (ww / 2, hh / 2), (-ww / 2, hh / 2))]
                d.polygon(s.P(pts), fill=(8, 8, 8, 255))
        spr = np.asarray(im.resize((s.w, s.h), Image.LANCZOS)).astype(np.float32) / 255
        return cutout_border(spr, border, seed) if border else spr

def _head(f, cx, cy, r, skin=200, hair=45, bald=False, female=False, bar=True, old=False):
    f.rect((cx - r * .38, cy + r * .6, cx + r * .38, cy + r * 1.35), skin * .82)
    f.ell((cx - r * .86, cy - r * 1.08, cx + r * .86, cy + r * 1.08), skin)
    f.ell((cx - r * 1.0, cy - r * .2, cx - r * .7, cy + r * .35), skin * .9)
    if female:
        f.chord((cx - r * .95, cy - r * 1.2, cx + r * .95, cy + r * .5), 180, 360, hair)
        f.ell((cx - r * .45, cy - r * 1.65, cx + r * .45, cy - r * .85), hair)
        f.rect((cx - r * .95, cy - r * .45, cx - r * .72, cy + r * .6), hair)
        f.rect((cx + r * .72, cy - r * .45, cx + r * .95, cy + r * .6), hair)
    elif not bald:
        f.chord((cx - r * .92, cy - r * 1.22, cx + r * .92, cy + (r * .1 if not old else -r * .3)), 180, 360, hair)
        f.rect((cx - r * .9, cy - r * .5, cx - r * .72, cy + r * .45), hair)
        f.rect((cx + r * .72, cy - r * .5, cx + r * .9, cy + r * .45), hair)
    f.poly([(cx + r * .05, cy - r * .05), (cx + r * .25, cy + r * .45), (cx - r * .05, cy + r * .5)], skin * .72)
    f.line([(cx - r * .32, cy + r * .72), (cx + r * .32, cy + r * .72)], skin * .55, max(1.5, r * .07))
    if bar: f.bar(cx, cy - r * .15, r * 2.1, r * .52)

def frock_doctor(h=820, thin=1.0, hat=False, seed=3, hair=45, old=False, skin=200):
    w = int(h * .5)
    f = Fig(w, h)
    cx = w / 2; sw = h * .17 * thin
    top = h * .21
    # legs
    f.poly([(cx - sw * .55, h * .62), (cx - sw * .05, h * .62), (cx - sw * .12, h * .97), (cx - sw * .5, h * .97)], 55)
    f.poly([(cx + sw * .05, h * .62), (cx + sw * .55, h * .62), (cx + sw * .5, h * .97), (cx + sw * .12, h * .97)], 48)
    f.ell((cx - sw * .7, h * .955, cx - sw * .05, h * .995), 15); f.ell((cx + sw * .05, h * .955, cx + sw * .72, h * .995), 15)
    # coat with tails
    f.poly([(cx - sw * .45, top), (cx + sw * .45, top), (cx + sw * 1.0, top + h * .04), (cx + sw * .95, h * .45), (cx + sw * 1.15, h * .74),
            (cx + sw * .3, h * .70), (cx - sw * .3, h * .70), (cx - sw * 1.12, h * .74), (cx - sw * .95, h * .45), (cx - sw * 1.0, top + h * .04)], 38)
    f.poly([(cx - sw * .3, top + h * .01), (cx, top + h * .2), (cx - sw * .55, top + h * .26), (cx - sw * .7, top + h * .05)], 70)
    f.poly([(cx + sw * .3, top + h * .01), (cx, top + h * .2), (cx + sw * .55, top + h * .26), (cx + sw * .7, top + h * .05)], 62)
    f.poly([(cx - sw * .28, top), (cx + sw * .28, top), (cx + sw * .1, top + h * .17), (cx, top + h * .19), (cx - sw * .1, top + h * .17)], 232)
    f.poly([(cx - sw * .16, top + h * .01), (cx + sw * .16, top + h * .01), (cx + sw * .08, top + h * .07), (cx - sw * .08, top + h * .07)], 200)
    for k in range(3): f.ell((cx - 4, top + h * (.24 + k * .06), cx + 4, top + h * (.24 + k * .06) + 8), 150)
    # arms
    f.poly([(cx - sw * 1.0, top + h * .04), (cx - sw * .72, top + h * .07), (cx - sw * .78, h * .56), (cx - sw * 1.08, h * .55)], 30)
    f.poly([(cx + sw * 1.0, top + h * .04), (cx + sw * .72, top + h * .07), (cx + sw * .78, h * .56), (cx + sw * 1.08, h * .55)], 34)
    f.ell((cx - sw * 1.08, h * .54, cx - sw * .74, h * .6), skin * .9); f.ell((cx + sw * .74, h * .54, cx + sw * 1.08, h * .6), skin * .85)
    _head(f, cx, top - h * .085, h * .062, skin=skin, hair=hair, old=old)
    if hat:
        r = h * .062; hy = top - h * .085 - r * 1.0
        f.rect((cx - r * .8, hy - r * 1.7, cx + r * .8, hy), 25); f.ell((cx - r * 1.35, hy - r * .25, cx + r * 1.35, hy + r * .2), 25)
    return f.build(seed=seed)

def white_coat_doctor(h=820, seed=5, steth=True):
    w = int(h * .5); f = Fig(w, h); cx = w / 2; sw = h * .18; top = h * .21
    f.poly([(cx - sw * .5, h * .7), (cx - sw * .05, h * .7), (cx - sw * .1, h * .97), (cx - sw * .45, h * .97)], 70)
    f.poly([(cx + sw * .05, h * .7), (cx + sw * .5, h * .7), (cx + sw * .45, h * .97), (cx + sw * .1, h * .97)], 64)
    f.ell((cx - sw * .62, h * .955, cx - sw * .05, h * .995), 20); f.ell((cx + sw * .05, h * .955, cx + sw * .64, h * .995), 20)
    f.poly([(cx - sw * .45, top), (cx + sw * .45, top), (cx + sw * 1.0, top + h * .04), (cx + sw * 1.05, h * .78), (cx - sw * 1.05, h * .78), (cx - sw * 1.0, top + h * .04)], 236)
    f.poly([(cx - sw * .3, top), (cx + sw * .3, top), (cx, top + h * .2)], 120)
    f.line([(cx, top + h * .2), (cx, h * .78)], 190, 3)
    f.poly([(cx - sw * .3, top), (cx - sw * .02, top + h * .22), (cx - sw * .5, top + h * .3), (cx - sw * .62, top + h * .04)], 214)
    f.poly([(cx + sw * .3, top), (cx + sw * .02, top + h * .22), (cx + sw * .5, top + h * .3), (cx + sw * .62, top + h * .04)], 208)
    f.poly([(cx - sw * 1.0, top + h * .04), (cx - sw * .74, top + h * .07), (cx - sw * .8, h * .58), (cx - sw * 1.1, h * .57)], 222)
    f.poly([(cx + sw * 1.0, top + h * .04), (cx + sw * .74, top + h * .07), (cx + sw * .8, h * .58), (cx + sw * 1.1, h * .57)], 216)
    f.ell((cx - sw * 1.1, h * .56, cx - sw * .76, h * .62), 185); f.ell((cx + sw * .76, h * .56, cx + sw * 1.1, h * .62), 180)
    f.rect((cx - sw * .9, h * .5, cx - sw * .5, h * .53), 160)
    _head(f, cx, top - h * .085, h * .062, hair=55)
    if steth:
        nk = top + h * .005
        pts = [(cx - sw * .42, nk - 4), (cx - sw * .55, top + h * .12), (cx - sw * .35, top + h * .27), (cx - sw * .05, top + h * .33)]
        pts2 = [(cx + sw * .42, nk - 4), (cx + sw * .55, top + h * .12), (cx + sw * .4, top + h * .24)]
        f.color_line(pts, h * .014); f.color_line(pts2, h * .014)
        f.color_ell((cx - sw * .02 - h * .03, top + h * .32, cx - sw * .02 + h * .03, top + h * .38))
        f.color_ell((cx + sw * .4 - h * .012, top + h * .235, cx + sw * .4 + h * .012, top + h * .26), (.75, .75, .74))
    return f.build(seed=seed)

def seated_woman(h=640, seed=7, hand=True):
    w = int(h * .62); f = Fig(w, h); cx = w * .45; sw = h * .16; top = h * .3
    f.poly([(cx - sw * .6, top), (cx + sw * .6, top), (cx + sw * 1.0, top + h * .06), (cx + sw * 1.1, h * .62), (cx + sw * 2.0, h * .7),
            (cx + sw * 2.0, h * .97), (cx - sw * 1.3, h * .97), (cx - sw * 1.1, h * .62), (cx - sw * 1.0, top + h * .06)], 228)
    f.line([(cx - sw * .5, h * .7), (cx - sw * .4, h * .95)], 195, 3); f.line([(cx + sw * .5, h * .72), (cx + sw * .7, h * .95)], 195, 3)
    f.poly([(cx - sw * .25, top), (cx + sw * .25, top), (cx, top + h * .07)], 175)
    if hand:
        f.poly([(cx + sw * 1.0, top + h * .06), (cx + sw * .7, top + h * .1), (cx + sw * .1, top + h * .2), (cx + sw * .25, top + h * .25), (cx + sw * 1.0, top + h * .2)], 214)
        f.ell((cx - sw * .1, top + h * .17, cx + sw * .3, top + h * .25), 195)
    _head(f, cx, top - h * .1, h * .072, skin=210, hair=60, female=True)
    return f.build(seed=seed)

def sickbed(w=760, seed=9):
    h = int(w * .55); f = Fig(w, h)
    f.rect((w * .02, h * .25, w * .07, h * .98), 40); f.rect((w * .93, h * .45, w * .97, h * .98), 40)
    f.rect((w * .04, h * .62, w * .96, h * .78), 60)
    f.ell((w * .06, h * .36, w * .3, h * .58), 235)
    f.poly([(w * .2, h * .52), (w * .5, h * .42), (w * .8, h * .46), (w * .95, h * .55), (w * .95, h * .72), (w * .15, h * .72)], 220)
    for k in range(4): f.line([(w * (.3 + k * .15), h * .47), (w * (.35 + k * .15), h * .7)], 190, 3)
    r = h * .1; cx, cy = w * .2, h * .42
    f.ell((cx - r * .9, cy - r * 1.05, cx + r * .9, cy + r * 1.05), 205)
    f.chord((cx - r * .95, cy - r * 1.15, cx + r * .95, cy - r * .2), 180, 360, 150)
    f.poly([(cx + r * .1, cy), (cx + r * .3, cy + r * .4), (cx, cy + r * .45)], 160)
    f.bar(cx, cy - r * .15, r * 2.1, r * .5, rot=-10)
    return f.build(seed=seed)

def leaning_young(h=760, seed=11):
    spr = frock_doctor(h, thin=.9, seed=seed, hair=35)
    return spr

def hand_sprite(right=True, seed=13, s=1.0):
    w, h = int(220 * s), int(520 * s); f = Fig(w, h)
    f.rect((w * .2, h * .35, w * .8, h), 35)
    f.rect((w * .17, h * .3, w * .83, h * .38), 235)
    f.ell((w * .15, h * .04, w * .85, h * .36), 200)
    f.ell((w * .72 if right else w * .02, h * .14, w * .98 if right else w * .28, h * .3), 190)
    for k in range(3): f.line([(w * (.32 + k * .14), h * .06), (w * (.32 + k * .14), h * .2)], 165, 2)
    spr = f.build(seed=seed, border=4)
    return spr

def tombstone(w=360, seed=15):
    h = int(w * 1.35); f = Fig(w, h)
    f.rect((w * .1, h * .25, w * .9, h * .95), 150); f.ell((w * .1, h * .02, w * .9, h * .5), 150)
    f.rect((w * .02, h * .9, w * .98, h), 110)
    f.line([(w * .5, h * .12), (w * .5, h * .38)], 95, 8); f.line([(w * .38, h * .2), (w * .62, h * .2)], 95, 8)
    return f.build(seed=seed, shade=.4)

def mini_stone(w=120, seed=17, cross=False):
    h = int(w * 1.4); f = Fig(w, h)
    if cross:
        f.rect((w * .42, 0, w * .58, h), 120); f.rect((w * .15, h * .2, w * .85, h * .32), 120)
    else:
        f.rect((w * .12, h * .3, w * .88, h), 135); f.ell((w * .12, h * .05, w * .88, h * .55), 135)
    return f.build(seed=seed, border=3, shade=.4)

# ------------------------------------------------------------ architecture
def house_row(width, seed, tone=1.0, hmin=260, hmax=520, dome=False):
    r = np.random.default_rng(seed)
    hh = hmax + 260
    canvas = np.zeros((hh, width, 4), np.float32)
    tex = newsprint(hh, width, seed + 1, tone)
    mask = np.zeros((hh, width), np.float32)
    shade = np.ones((hh, width), np.float32)
    x = 0
    while x < width:
        bw = int(r.integers(110, 200)); bh = int(r.integers(hmin, hmax))
        y0 = hh - bh
        cv2.rectangle(mask, (x, y0), (x + bw, hh), 1, -1)
        # mansard roof
        rh = int(bh * .18)
        cv2.fillPoly(mask, [np.array([[x + 6, y0], [x + bw - 6, y0], [x + bw - 22, y0 - rh], [x + 22, y0 - rh]], np.int32)], 1)
        cv2.fillPoly(shade, [np.array([[x + 6, y0], [x + bw - 6, y0], [x + bw - 22, y0 - rh], [x + 22, y0 - rh]], np.int32)], .55)
        for c in range(int(r.integers(1, 4))):
            cx = x + int(r.integers(25, bw - 30))
            cv2.rectangle(mask, (cx, y0 - rh - 45), (cx + 18, y0 - rh + 5), 1, -1)
            cv2.rectangle(shade, (cx, y0 - rh - 45), (cx + 18, y0 - rh + 5), .7, -1)
        for k in range(int(r.integers(0, 3))):  # dormers
            dx = x + 30 + k * 50
            if dx + 26 < x + bw - 20:
                cv2.rectangle(shade, (dx, y0 - rh + 10), (dx + 20, y0 - 6), .3, -1)
        # windows
        cols = max(2, bw // 45); rows = max(2, (bh - 40) // 70)
        for i in range(cols):
            for j in range(rows):
                wx = x + 14 + i * (bw - 28) // cols; wy = y0 + 22 + j * 70
                if wy + 40 > hh - 10: continue
                lit = r.random() < .18
                cv2.rectangle(shade, (wx, wy), (wx + 20, wy + 40), 1.35 if lit else .28, -1)
        cv2.line(shade, (x + bw - 1, y0), (x + bw - 1, hh), .6, 3)
        seg = shade[y0:hh, x:x + bw]; seg *= np.linspace(1.08, .85, seg.shape[1], dtype=np.float32)[None, :]
        x += bw - int(r.integers(0, 10))
    if dome:
        cx = width // 2; base = hh - hmax - 20
        cv2.rectangle(mask, (cx - 150, base), (cx + 150, hh), 1, -1)
        cv2.ellipse(mask, (cx, base), (130, 150), 0, 180, 360, 1, -1)
        cv2.rectangle(mask, (cx - 18, base - 210), (cx + 18, base - 140), 1, -1)
        cv2.ellipse(shade, (cx, base), (130, 150), 0, 180, 360, .8, -1)
        for k in range(-3, 4):
            cv2.line(shade, (cx + k * 36, base), (cx + int(k * 20), base - 140 + abs(k) * 12), .55, 3)
        for k in range(5):
            cv2.rectangle(shade, (cx - 120 + k * 52, base + 40), (cx - 98 + k * 52, base + 110), .3, -1)
    a, rim = torn_alpha(mask, seed, 4)
    col = tex * shade[..., None]
    col = col * (1 - rim[..., None]) + WHITE_P * rim[..., None]
    return rgba(col, a)

def cloud(w, seed):
    h = int(w * .45); m = np.zeros((h, w), np.float32); r = np.random.default_rng(seed)
    for k in range(7):
        cx = int(r.uniform(.2, .8) * w); cy = int(r.uniform(.45, .7) * h); rr = int(r.uniform(.12, .25) * w)
        cv2.circle(m, (cx, cy), rr, 1, -1)
    m[int(h * .8):] = 0
    a, rim = torn_alpha(m, seed, 5)
    col = newsprint(h, w, seed, 1.1, density=.3) * 1.04
    return rgba(col * (1 - rim[..., None]) + WHITE_P * rim[..., None], a)

def wall_with_windows(h, w, seed, n=2, tone=.92, lit=True):
    img = newsprint(h, w, seed, tone)
    glow = np.zeros((h, w), np.float32)
    ww = int(w * .26); gap = (w - n * ww) // (n + 1)
    for i in range(n):
        x0 = gap + i * (ww + gap); y0 = int(h * .2); y1 = int(h * .62)
        m = np.zeros((h, w), np.float32)
        cv2.rectangle(m, (x0, y0), (x0 + ww, y1), 1, -1); cv2.ellipse(m, (x0 + ww // 2, y0), (ww // 2, ww // 2), 0, 180, 360, 1, -1)
        frame = cv2.dilate(m, np.ones((15, 15), np.uint8)) - m
        img = img * (1 - frame[..., None] * .55)
        mull = np.zeros_like(m); cv2.line(mull, (x0 + ww // 2, y0 - ww // 2), (x0 + ww // 2, y1), 1, 6); cv2.line(mull, (x0, (y0 + y1) // 2), (x0 + ww, (y0 + y1) // 2), 1, 6)
        pane = np.clip(m - mull, 0, 1)
        bright = np.array([1.0, .93, .78]) if lit else np.array([.55, .55, .58])
        img = img * (1 - m[..., None]) + (pane[..., None] * bright + mull[..., None] * .25) * m[..., None]
        glow += m
    return np.clip(img, 0, 1), glow

def floor_planks(h, w, seed, tone=.7):
    img = newsprint(h, w, seed, tone, density=.6)
    for x in range(0, w, 60): cv2.line(img, (x, 0), (x, h), (.25, .2, .15), 2)
    return img

# ------------------------------------------------------------ orange props
def orange_paper(h, w, seed, tone=1.0):
    n = fbm(h, w, (60, 15, 4), seed)
    col = ORANGE * tone * (.82 + .3 * n)[..., None]
    fib = (noise(h, w, 1, seed + 3) > .93).astype(np.float32) * .12
    return np.clip(col + fib[..., None], 0, 1)

def tube_sprite(length=420, r=34, seed=21, wood=False, vertical=False):
    """Burnt-orange rolled paper tube (horizontal). wood=True gives a turned wooden one."""
    h = r * 2 + 40; w = length + 60
    out = np.zeros((h, w, 4), np.float32)
    yy = np.arange(h, dtype=np.float32)[:, None] - h / 2
    xx = np.arange(w, dtype=np.float32)[None, :] - w / 2
    if wood:
        f = (xx + length / 2) / length
        rad = np.where(f < .07, r * 1.25, np.where(f < .11, r * .6, np.where(f > .82, r * (.6 + (f - .82) / .18 * .9), r * .6)))
    else:
        rad = np.full_like(xx, r)
    inside = (np.abs(xx) < length / 2) & (np.abs(yy) < rad)
    u = yy / np.maximum(rad, 1)
    sh = np.sqrt(np.clip(1 - u ** 2, 0, 1))
    light = .5 + .55 * sh + .35 * np.exp(-((u + .45) / .18) ** 2)
    base = orange_paper(h, w, seed)
    if wood:
        grain = .9 + .12 * np.sin(xx * .25 + 6 * noise(h, w, 8, seed + 1))
        base = base * np.array([.92, .78, .7]) * grain[..., None]
    else:
        spiral = 1 - .12 * ((((xx + yy * 1.3) % 70) < 2.5)).astype(np.float32)
        base = base * spiral[..., None]
    col = base * light[..., None]
    a = np.clip((rad - np.abs(yy)) * .9, 0, 1) * (np.abs(xx) < length / 2)
    out = rgba(col, a)
    # open end
    ex = int(w / 2 + length / 2) if not wood else int(w / 2 - length / 2)
    cv2.ellipse(out, (ex, h // 2), (int(r * .32), int(r * .95 if not wood else r * 1.2)), 0, 0, 360, (.35, .14, .05, 1), -1, cv2.LINE_AA)
    if vertical: out = np.ascontiguousarray(np.rot90(out))
    return out

def stamp_text(s, size=150, color=ORANGE, seed=31, wght=None, fnt='anton', distress=.38, pad=30):
    f = font(fnt, size, wght)
    l, t, r, b = f.getbbox(s)
    w, h = r - l + pad * 2, b - t + pad * 2
    im = Image.new('L', (w, h), 0); d = ImageDraw.Draw(im)
    d.text((pad - l, pad - t), s, font=f, fill=255)
    a = np.asarray(im).astype(np.float32) / 255
    n = fbm(h, w, (14, 5, 2), seed)
    a = a * np.clip((n - distress) * 6 + .2, 0, 1)
    a = a * (1 - (noise(h, w, 1, seed + 2) > .965) * .9)
    col = np.broadcast_to(np.array(color, np.float32), (h, w, 3)) * (.85 + .25 * noise(h, w, 3, seed + 4))[..., None]
    return rgba(col, a)

def torn_strip(w, h, seed, color_fn=None, label=None, label_size=None, ink=INK):
    m = np.zeros((h + 30, w + 30), np.float32); cv2.rectangle(m, (15, 15), (w + 15, h + 15), 1, -1)
    a, rim = torn_alpha(m, seed, 7)
    col = orange_paper(h + 30, w + 30, seed)
    col = col * (1 - rim[..., None]) + np.array([.97, .82, .65]) * rim[..., None]
    spr = rgba(col, a)
    if label:
        t = stamp_text(label, label_size or int(h * .62), ink, seed + 1, distress=.3)
        th, tw = t.shape[:2]
        y0 = (spr.shape[0] - th) // 2; x0 = (spr.shape[1] - tw) // 2
        if x0 >= 0 and y0 >= 0:
            reg = spr[y0:y0 + th, x0:x0 + tw]
            ta = t[..., 3:4] * reg[..., 3:4]
            reg[..., :3] = reg[..., :3] * (1 - ta) + t[..., :3] * ta
    return spr

# ------------------------------------------------------------ compositing
def mblur(img, dx, dy):
    L = int(math.hypot(dx, dy))
    if L < 2: return img
    k = np.zeros((L * 2 + 1, L * 2 + 1), np.float32)
    cv2.line(k, (L - int(dx / 2), L - int(dy / 2)), (L + int(dx / 2), L + int(dy / 2)), 1, 1)
    k /= k.sum()
    return cv2.filter2D(img, -1, k, borderType=cv2.BORDER_REFLECT)

def zoom_blur(img, amt, n=7, cx=None, cy=None):
    if amt < .02: return img
    acc = np.zeros_like(img)
    cx = W / 2 if cx is None else cx; cy = H / 2 if cy is None else cy
    for i in range(n):
        s = 1 + .16 * amt * i / (n - 1)
        M = np.float32([[s, 0, cx - s * cx], [0, s, cy - s * cy]])
        acc += cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_REFLECT)
    return acc / n

def blit(dst, spr, cx, cy, scale=1.0, rot=0.0, alpha=1.0, sig=0.0, mb=None, shadow=(9, 13, 9, .42), glow=None):
    """Composite RGBA sprite centred at screen (cx,cy). Works on a cropped bbox for speed."""
    if alpha <= .004 or scale <= .002: return dst
    sh, sw = spr.shape[:2]
    M = cv2.getRotationMatrix2D((sw / 2, sh / 2), rot, scale)
    M[0, 2] += cx - sw / 2; M[1, 2] += cy - sh / 2
    corners = np.array([[0, 0, 1], [sw, 0, 1], [0, sh, 1], [sw, sh, 1]], np.float32) @ M.T
    mbl = int(math.hypot(*mb)) if mb else 0
    marg = int(3 * sig + 4 + mbl + (abs(shadow[0]) + abs(shadow[1]) + 3 * shadow[2] if shadow else 0) + (3 * glow[1] if glow else 0))
    x0 = int(max(0, corners[:, 0].min() - marg)); x1 = int(min(W, corners[:, 0].max() + marg))
    y0 = int(max(0, corners[:, 1].min() - marg)); y1 = int(min(H, corners[:, 1].max() + marg))
    if x1 <= x0 or y1 <= y0: return dst
    M2 = M.copy(); M2[0, 2] -= x0; M2[1, 2] -= y0
    pm = spr.copy(); pm[..., :3] *= pm[..., 3:4]
    big = scale > 1.6
    lay = cv2.warpAffine(pm, M2, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR if not big else cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    if sig > .3: lay = blur(lay, sig)
    if mb: lay = mblur(lay, *mb)
    lay = np.clip(lay, 0, None)
    reg = dst[y0:y1, x0:x1]
    a = lay[..., 3:4] * alpha
    if shadow:
        ox, oy, sb, st = shadow
        sa = blur(lay[..., 3], sb)
        M3 = np.float32([[1, 0, ox], [0, 1, oy]])
        sa = cv2.warpAffine(sa, M3, (sa.shape[1], sa.shape[0]))
        reg = reg * (1 - (sa * st * alpha)[..., None])
    if glow:
        col, gs, gk = glow
        reg = reg + blur(lay[..., 3], gs)[..., None] * np.array(col, np.float32) * gk * alpha
    reg = reg * (1 - a) + lay[..., :3] * alpha
    dst[y0:y1, x0:x1] = reg
    return dst

def cover(img, zoom=1.0, dx=0.0, dy=0.0, rot=0.0):
    ih, iw = img.shape[:2]
    s = max(W / iw, H / ih) * zoom
    cx, cy = iw / 2 + dx, ih / 2 + dy
    M = cv2.getRotationMatrix2D((cx, cy), rot, s)
    M[0, 2] += W / 2 - cx; M[1, 2] += H / 2 - cy
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

class Cam:
    """Pinhole camera for 2.5D layered paper sets. World y grows downward."""
    def __init__(s, x=0, y=0, z=0, F=900, roll=0.0, focus=6.0, dof=1.2):
        s.x, s.y, s.z, s.F, s.roll, s.focus, s.dof = x, y, z, F, roll, focus, dof
    def project(s, x, y, z):
        zr = z - s.z
        if zr <= .05: return None
        sx = W / 2 + s.F * (x - s.x) / zr; sy = H / 2 + s.F * (y - s.y) / zr
        if s.roll:
            th = math.radians(s.roll); dx, dy = sx - W / 2, sy - H / 2
            sx, sy = W / 2 + dx * math.cos(th) - dy * math.sin(th), H / 2 + dx * math.sin(th) + dy * math.cos(th)
        return sx, sy, zr

def draw_layers(dst, cam, layers):
    """layers: dicts with spr, x, y, z, size(world height of sprite), rot, alpha, shadow."""
    for L in sorted(layers, key=lambda l: -l['z']):
        p = cam.project(L['x'], L['y'], L['z'])
        if p is None: continue
        sx, sy, zr = p
        sc = cam.F * L['size'] / zr / L['spr'].shape[0]
        a = L.get('alpha', 1.0)
        if zr < .5: a *= clamp01((zr - .08) / .42)
        sig = min(9.0, cam.dof * abs(zr - cam.focus) / max(zr, .3) * 4) * L.get('dofk', 1.0)
        dst = blit(dst, L['spr'], sx, sy, sc, L.get('rot', 0) - cam.roll, a, sig, L.get('mb'),
                   L.get('shadow', (8, 12, 8, .42)), L.get('glow'))
    return dst

def tilt_shift(img, strength=6.0, band=.28, center=.5):
    b = blur(img, strength)
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    m = np.clip((np.abs(y - center) - band) / (.5 - band), 0, 1) ** 1.5
    return img * (1 - m) + b * m

def dust_burst(dst, cx, cy, t, seed=1, n=60, spread=420, col=(.95, .9, .8)):
    if t < 0 or t > 1.2: return dst
    r = np.random.default_rng(seed)
    for i in range(n):
        ang = r.uniform(0, 2 * math.pi); sp = r.uniform(.3, 1.0) * spread
        d = sp * (1 - math.exp(-t * 4))
        x = cx + math.cos(ang) * d; y = cy + math.sin(ang) * d * .6 + 60 * t * t
        rad = max(1, int(r.uniform(1, 4) * (1 - t / 1.2)))
        a = (1 - t / 1.2)
        if 0 <= x < W and 0 <= y < H:
            cv2.circle(dst, (int(x), int(y)), rad, tuple(float(c * a + dst[int(y), int(x), k] * (1 - a)) for k, c in enumerate(col)), -1, cv2.LINE_AA)
    return dst

def stamp(dst, spr, cx, cy, t, size_px, rot=-4, seed=1, dust=True):
    """Slam a letterpress stamp: t seconds since impact start."""
    if t < 0: return dst
    q = clamp01(t / .13)
    sc = lerp(2.6, 1.0, ease_in(q)) * size_px / spr.shape[1]
    a = clamp01(t / .06)
    dst = blit(dst, spr, cx, cy, sc, rot, a, sig=(1 - q) * 6, shadow=(5, 8, 4, .5 * q))
    if dust and t > .13: dst = dust_burst(dst, cx, cy, t - .13, seed, 70, size_px * .9)
    return dst

def impact_shake(t, t0, amp=14, decay=10):
    if t < t0: return 0.0, 0.0
    d = t - t0; e = amp * math.exp(-d * decay)
    return e * math.sin(d * 63), e * math.cos(d * 51) * .6
