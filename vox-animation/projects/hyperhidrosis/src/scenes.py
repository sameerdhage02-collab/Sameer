"""Six 10-second paper-diorama scenes: why hyperhidrosis happens (Hinglish)."""
import os, math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
from dlib import *

SCENE_LEN = 10.0
ICONS = os.path.normpath(os.path.join(HERE, '..', 'assets', 'icons'))

# ------------------------------------------------------------ captions
CAPTIONS = [
    ["Kuch log AC mein", "baithe-baithe bhi", "paseene se bheeg jaate hain.", "Aur problem", "sweat glands mein *nahi,*", "kahin aur hai."],
    ["Ise kehte hain", "*hyperhidrosis.*", "Ek US study ke hisaab se,", "har *bees mein se ek*", "insaan ise jhelta hai."],
    ["Hamare jism mein", "do se chaar *million*", "sweat glands hain,", "aur sabse zyada bhare hain", "hatheliyon aur talvon mein."],
    ["Har gland ka switch", "ek *nerve* hai.", "Hyperhidrosis mein yeh nerves", "bina wajah", "*full volume* pe", "signal bhejti rehti hain."],
    ["Kyun sirf kuch log?", "*Genes.*", "Ek-tihai se zyada patients ke", "parivaar mein", "kisi aur ko bhi", "yahi hota hai."],
    ["Aur sabse ajeeb baat?", "*Neend* mein yeh paseena", "ruk jaata hai.", "Glands wahi hain,", "bas signal", "*shaant* ho jaata hai."],
]

def chunk_times(chunks, t0=.3, t1=9.5):
    n = [len(c.replace('*', '').split()) + .6 for c in chunks]
    tot = sum(n); out = []; t = t0
    for c, k in zip(chunks, n):
        d = (t1 - t0) * k / tot; out.append((t, t + d, c)); t += d
    return out
CTIMES = [chunk_times(c) for c in CAPTIONS]
def ctime(scene, needle):
    for a, b, c in CTIMES[scene]:
        if needle in c.lower(): return a
    return 0

@functools.lru_cache(maxsize=64)
def caption_sprite(chunk):
    f = font('inter', 56, 800)
    on = False; words = []
    for wd in chunk.split(' '):
        if wd.startswith('*'): on = True
        words.append((wd.replace('*', ''), on))
        if wd.rstrip('.,:?').endswith('*'): on = False
    sp = f.getlength(' ')
    tw = sum(f.getlength(w) for w, _ in words) + sp * (len(words) - 1)
    pad = 24; asc = f.getbbox('Hg')
    im = Image.new('RGBA', (int(tw + pad * 2), asc[3] - asc[1] + pad * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = pad
    for wd, hl in words:
        d.text((x, pad - asc[1]), wd, font=f, fill=(238, 110, 35, 255) if hl else (255, 250, 240, 255), stroke_width=6, stroke_fill=(15, 12, 10, 255))
        x += f.getlength(wd) + sp
    return np.asarray(im).astype(np.float32) / 255

def draw_captions(f, scene, u):
    for a, b, c in CTIMES[scene]:
        if a <= u < b:
            e = ease_out((u - a) / .12); spr = caption_sprite(c)
            f = blit(f, spr, W / 2, 1035, min(1.0, 660 / spr.shape[1]) * lerp(.9, 1.0, e), 0, e, shadow=(0, 6, 8, .55))
    return f

def finish(f, u, enter=None, exit_=None):
    if enter and u < .3:
        p = 1 - u / .3
        f = zoom_blur(f, p * 1.6) if enter == 'zoom' else mblur(f, enter[0] * p, enter[1] * p)
    if exit_ and u > SCENE_LEN - .45:
        p = ease_in((u - (SCENE_LEN - .45)) / .45)
        f = zoom_blur(f, p * 1.8) if exit_ == 'zoom' else mblur(f, exit_[0] * p, exit_[1] * p)
    return f

def glow_spot(f, x, y, r, col=(1, .7, .35), k=.6):
    m = np.zeros((H, W), np.float32); cv2.circle(m, (int(x), int(y)), int(r), 1, -1)
    return f + blur(m, r * .9)[..., None] * np.array(col, np.float32) * k

# ------------------------------------------------------------ icon cutouts
@functools.lru_cache(maxsize=None)
def icon_alpha(name, h):
    a = np.asarray(Image.open(os.path.join(ICONS, name + '.png')))[..., 3]
    ys, xs = np.where(a > 8); a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = h / a.shape[0]
    a = cv2.resize(a.astype(np.float32) / 255, (max(1, int(a.shape[1] * s)), h), interpolation=cv2.INTER_AREA)
    return a

def icon_halftone(name, h, gray=.7, seed=1, border=7, shade=.35):
    a = icon_alpha(name, h)
    hh, ww = a.shape
    xx = np.linspace(0, 1, ww, dtype=np.float32)[None]; yy = np.linspace(0, 1, hh, dtype=np.float32)[:, None]
    g = gray * (1 + shade / 2 - shade * xx) * (1.05 - .1 * yy) * (.92 + .16 * fbm(hh, ww, (40, 10), seed))
    inner = blur(a, 6)
    g = g * (.75 + .25 * inner)
    spr = halftone_sprite(np.clip(g, 0, 1), a, 4.5)
    return cutout_border(spr, border, seed) if border else spr

def icon_paper(name, h, color=ORANGE, seed=2, border=5, rim=True):
    a = icon_alpha(name, h); hh, ww = a.shape
    col = orange_paper(hh, ww, seed) if color is ORANGE else np.broadcast_to(np.array(color, np.float32), (hh, ww, 3)) * (.85 + .25 * fbm(hh, ww, (30, 8), seed))[..., None]
    xx = np.linspace(0, 1, ww, dtype=np.float32)[None, :, None]
    col = col * (1.12 - .3 * xx)
    spr = rgba(col, a)
    return cutout_border(spr, border, seed) if border else spr

@functools.lru_cache(maxsize=None)
def drop_sprite(h=120, seed=3):
    spr = icon_paper('drop', h, ORANGE, seed, border=3)
    hh, ww = spr.shape[:2]
    hl = np.zeros((hh, ww), np.float32)
    cv2.ellipse(hl, (int(ww * .38), int(hh * .58)), (max(2, int(ww * .09)), max(3, int(hh * .14))), -20, 0, 360, 1, -1)
    spr[..., :3] = spr[..., :3] * (1 - blur(hl, 2)[..., None] * .8) + blur(hl, 2)[..., None] * .8 * np.array([1, .93, .8])
    return spr

# ------------------------------------------------------------ assets
@functools.lru_cache(maxsize=None)
def A(name):
    if name == 'room':
        img = newsprint(1600, 900, 801, .9)
        fl = int(1600 * .68); img[fl:] = floor_planks(1600 - fl, 900, 802, .6)
        return img
    if name == 'ac':
        w, h = 520, 200; f = Fig(w, h)
        f.rect((0, 0, w, h), 225); f.rect((0, h * .78, w, h), 190)
        for k in range(6): f.line([(w * .06, h * (.82 + k * .028)), (w * .94, h * (.82 + k * .028))], 120, 2)
        f.rect((w * .78, h * .2, w * .92, h * .32), 90)
        return f.build(seed=803, shade=.15)
    if name == 'hand': return icon_halftone('hand-palm', 900, .8, 804)
    if name == 'snow': return icon_paper('snowflake', 120, WHITE_P, 805)
    if name == 'st18': return stamp_text('18°C', 120, ORANGE, 806, distress=.3)
    if name == 'wall_light': return newsprint(1600, 900, 807, 1.0)
    if name == 'person': return icon_halftone('person', 300, .55, 808, border=5)
    if name == 'person_o': return icon_paper('person', 300, ORANGE, 809)
    if name == 'stHH_strip': return torn_strip(620, 120, 810)
    if name == 'stHH_t': return stamp_text('HYPERHIDROSIS', 84, INK * 1.3, 811, distress=.18)
    if name == 'st1in20': return stamp_text('1 IN 20', 150, ORANGE, 812, distress=.3)
    if name == 'skin': return skin_section()
    if name == 'stMIL': return stamp_text('MILLIONS', 150, ORANGE, 813, distress=.3)
    if name == 'panel': return newsprint(1600, 900, 814, .95)
    if name == 'hand_s': return icon_halftone('hand-palm', 560, .8, 815)
    if name == 'feet_s': return icon_halftone('footprints', 520, .8, 816)
    if name == 'nerve_bg': return newsprint(1600, 900, 817, .55)
    if name == 'spine': return spine_sprite()
    if name == 'knob': return knob_sprite()
    if name == 'stMAX': return stamp_text('MAX', 120, ORANGE, 818, distress=.3)
    if name == 'family_bg': return newsprint(1600, 900, 819, .85)
    if name == 'portrait': return portrait_frame(820, .58)
    if name == 'portrait_o': return portrait_frame(821, .58, glow=True)
    if name == 'dna': return icon_paper('dna', 260, ORANGE, 822)
    if name == 'stGENES': return stamp_text('GENES', 150, ORANGE, 823, distress=.3)
    if name == 'night':
        img, glow = wall_with_windows(1600, 900, 824, 1, .45, lit=False)
        fl = int(1600 * .68); img[fl:] = floor_planks(1600 - fl, 900, 825, .38)
        return np.clip(img * np.array([.78, .82, .98], np.float32), 0, 1)
    if name == 'moon': return icon_paper('moon-stars', 220, (.95, .92, .8), 826)
    if name == 'bed': return sickbed(760, 827)
    if name == 'stSLEEP': return stamp_text('SLEEP', 150, ORANGE, 828, distress=.3)
    if name == 'z': return stamp_text('Z', 90, WHITE_P, 829, fnt='bebas', distress=.15)
    raise KeyError(name)

def skin_section():
    """Tall paper cross-section of skin: surface, epidermis, dermis with coiled glands, fat."""
    h, w = 2600, 900
    img = newsprint(h, w, 830, 1.0, density=.4)
    x = np.arange(w)
    top = (300 + 14 * np.sin(x / 38) + 6 * np.sin(x / 11)).astype(int)
    epi = newsprint(h, w, 831, 1.0, density=.2) * np.array([1.0, .9, .8], np.float32)
    der = newsprint(h, w, 832, .9, density=.3) * np.array([1.0, .82, .74], np.float32)
    fat = newsprint(h, w, 833, 1.0, density=.15) * np.array([1.0, .93, .7], np.float32)
    yy = np.arange(h)[:, None]
    m_epi = (yy >= top[None, :]); m_der = yy >= (top[None, :] + 220); m_fat = yy >= 1900
    img = np.where(m_epi[..., None], epi, img); img = np.where(m_der[..., None], der, img); img = np.where(m_fat[..., None], fat, img)
    ink = np.zeros((h, w), np.float32)
    for xi in range(0, w, 3):  # layer edges
        cv2.circle(ink, (xi, int(top[xi])), 2, 1, -1); cv2.circle(ink, (xi, int(top[xi] + 220)), 1, .6, -1)
    cv2.line(ink, (0, 1900), (w, 1900), .6, 2)
    r = np.random.default_rng(834)
    for k in range(22):  # fat cells
        cx, cy, rr = int(r.uniform(0, w)), int(r.uniform(1950, 2550)), int(r.uniform(50, 90))
        cv2.circle(ink, (cx, cy), rr, .7, 3)
    pores = []
    for k in range(7):  # coiled glands with ducts to pores
        gx = 70 + k * 125 + int(r.uniform(-20, 20)); gy = int(r.uniform(1450, 1700))
        for j in range(26):
            a = j * .9; rr = 30 + 6 * math.sin(j)
            cv2.ellipse(ink, (gx + int(math.cos(a) * rr * .8), gy + int(math.sin(a) * rr * .5)), (26, 16), math.degrees(a), 0, 360, .9, 3, cv2.LINE_AA)
        pts = []
        for yv in range(gy - 40, int(top[min(w - 1, gx)]), -8):
            pts.append((gx + int(14 * math.sin(yv / 30)), yv))
        cv2.polylines(ink, [np.array(pts, np.int32)], False, .85, 5, cv2.LINE_AA)
        pores.append((gx + int(14 * math.sin(pts[-1][1] / 30)), int(top[min(w - 1, gx)])))
    for k in range(5):  # nerve fibres (thin)
        sx = int(r.uniform(0, w)); pts = [(sx + int(40 * math.sin(yv / 90 + k)), yv) for yv in range(2600, 700, -20)]
        cv2.polylines(ink, [np.array(pts, np.int32)], False, .5, 2, cv2.LINE_AA)
    ink = blur(ink, .8)
    img = img * (1 - ink[..., None] * .75) + INK * ink[..., None] * .75
    sky = newsprint(h, w, 835, .7, density=.6)
    img = np.where((yy < top[None, :])[..., None], sky, img)
    skin_section.pores = pores
    return np.clip(img, 0, 1)

def spine_sprite():
    w, h = 220, 1500; f = Fig(w, h)
    for k in range(12):
        y = 20 + k * 122
        f.rect((w * .22, y, w * .78, y + 92), 205); f.rect((w * .05, y + 30, w * .95, y + 60), 175)
        f.rect((w * .3, y + 94, w * .7, y + 118), 120)
    return f.build(seed=840, shade=.4)

def knob_sprite():
    s = 300; f = Fig(s, s)
    f.ell((10, 10, s - 10, s - 10), 70); f.ell((40, 40, s - 40, s - 40), 205)
    for k in range(11):
        a = math.radians(-225 + k * 27); r0, r1 = s * .4, s * .47
        f.line([(s / 2 + math.cos(a) * r0, s / 2 + math.sin(a) * r0), (s / 2 + math.cos(a) * r1, s / 2 + math.sin(a) * r1)], 240, 6)
    f.rect((s / 2 - 8, 50, s / 2 + 8, s / 2), 30)
    return f.build(seed=841, shade=.3)

def portrait_frame(seed, gray, glow=False):
    s = 300; h = 380
    a = np.zeros((h, s), np.float32); cv2.ellipse(a, (s // 2, h // 2), (s // 2 - 4, h // 2 - 4), 0, 0, 360, 1, -1)
    inner = np.zeros_like(a); cv2.ellipse(inner, (s // 2, h // 2), (s // 2 - 30, h // 2 - 30), 0, 0, 360, 1, -1)
    frame_col = orange_paper(h, s, seed) * .9 if glow else np.broadcast_to(np.array([.32, .24, .16], np.float32), (h, s, 3)) * (.8 + .4 * fbm(h, s, (20, 6), seed))[..., None]
    bg = newsprint(h, s, seed + 1, 1.05, density=.3)
    col = frame_col * (1 - inner[..., None]) + bg * inner[..., None]
    p = icon_halftone('person', 300, gray, seed + 2, border=0)
    ph, pw = p.shape[:2]; y0 = h - 30 - ph + 60; x0 = s // 2 - pw // 2
    reg = col[max(0, y0):h, x0:x0 + pw]; pp = p[max(0, -y0):max(0, -y0) + reg.shape[0]]
    pa = pp[..., 3:4] * inner[max(0, y0):h, x0:x0 + pw, None]
    col[max(0, y0):h, x0:x0 + pw] = reg * (1 - pa) + pp[..., :3] * pa
    return cutout_border(rgba(col, a), 5, seed)

# ------------------------------------------------------------ helpers
def drops_on(f, pts, u, scale, cx, cy, starts, size=1.0, fall_from=None):
    """Grow orange drops at relative points (pixels around cx,cy). Drops after fall_from slide down."""
    d = drop_sprite()
    for (px, py), t0 in zip(pts, starts):
        e = ease_back((u - t0) / .45)
        if e <= 0: continue
        y = cy + py * scale
        if fall_from is not None and u > fall_from + (t0 % .7):
            q = u - fall_from - (t0 % .7); y += 260 * q * q
        f = blit(f, d, cx + px * scale, y, size * scale * e * .6, 0, 1.0, shadow=(3, 6, 4, .45))
    return f

def bezier(p0, p1, p2, p3, n=120):
    t = np.linspace(0, 1, n)[:, None]
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3

def nerve(f, pts, v, u, color=ORANGE, width=16, beads=True):
    pts_i = pts.astype(np.int32)
    lay_ = np.zeros((H, W), np.float32)
    cv2.polylines(lay_, [pts_i], False, 1, width, cv2.LINE_AA)
    sh = np.roll(np.roll(blur(lay_, 6), 10, 0), 6, 1)
    f = f * (1 - sh[..., None] * .4)
    tex = orange_paper(H, W, 850) if color is ORANGE else np.broadcast_to(np.array(color, np.float32), (H, W, 3))
    hl = np.zeros((H, W), np.float32); cv2.polylines(hl, [pts_i - [0, width // 4]], False, 1, max(2, width // 4), cv2.LINE_AA)
    f = f * (1 - lay_[..., None]) + (tex * (1 - .25 * hl[..., None]) + hl[..., None] * .25) * lay_[..., None]
    if beads and v > .02:
        n = len(pts); speed = .25 + 1.6 * v; count = int(2 + 7 * v)
        for k in range(count):
            ph = ((u * speed + k / count) % 1.0)
            x, y = pts[int(ph * (n - 1))]
            g = np.zeros((H, W), np.float32); cv2.circle(g, (int(x), int(y)), int(width * .9), 1, -1)
            f = f + blur(g, 10)[..., None] * np.array([1, .9, .6], np.float32) * (.6 + .6 * v)
    return f

# ------------------------------------------------------------ scene 1: AC room, sweating palm
HAND_PTS = [(-150, -60), (-60, -20), (40, -50), (130, 10), (-110, 90), (0, 70), (110, 120), (-40, 170), (60, 210), (-170, -260), (-60, -330), (60, -330), (170, -250), (200, 60)]
def scene1(u):
    z = 1.04 + .16 * ease_io(u / 7.2)
    f = cover(A('room'), 1.04 + .05 * u / 10, 0, 10 * u)
    acx, acy = W / 2, 250 - 40 * ease_io(u / 7.2)
    f = blit(f, A('ac'), acx, acy, .95, 0, 1.0, shadow=(8, 14, 10, .45))
    f = stamp(f, A('st18'), acx - 70, acy - 22, u - .7, 170, rot=-5, seed=3, dust=False)
    r = np.random.default_rng(4)
    for k in range(9):  # snowflakes drifting from the AC
        ph = (u * .18 + k / 9) % 1.0
        x = acx + r.uniform(-220, 220) + 80 * math.sin(ph * 6 + k); y = acy + 90 + ph * 700
        f = blit(f, A('snow'), x, y, .32 + .2 * r.random(), u * 60 * (1 if k % 2 else -1), clamp01(1.4 - ph * 1.6) * clamp01(u / .5), shadow=(4, 8, 4, .3))
    hx, hy = W / 2, 720 + 10 * math.sin(u * 1.4)
    hs = .78 * z
    f = blit(f, A('hand'), hx, hy, hs, 3 * math.sin(u * .8), 1.0, shadow=(14, 22, 14, .5))
    starts = [1.0 + k * .32 for k in range(len(HAND_PTS))]
    f = drops_on(f, HAND_PTS, u, hs, hx, hy + 60 * hs, starts, 1.0, fall_from=6.0)
    if u > 6.8:
        p = ease_in((u - 6.8) / .6)
        f = f * (1 - .12 * p)
    if u > 8.9:  # dive into the palm
        p = ease_in((u - 8.9) / 1.1)
        f = zoom_blur(cover(f, 1 + 3 * p, 0, 60 * p), p * 1.8)
    f = draw_captions(f, 0, u)
    return finish(f, u, enter='zoom')

# ------------------------------------------------------------ scene 2: the crowd, one in twenty
CROWD = [(c, r) for r in range(4) for c in range(5)]
def scene2(u):
    t_one = ctime(1, 'bees') - .35
    f = cover(A('wall_light'), 1.05 + .04 * u / 10, -15 * u, 0)
    pick = 12
    for i, (c, r) in enumerate(CROWD):  # back rows first
        pass
    order = sorted(range(len(CROWD)), key=lambda i: CROWD[i][1])
    for i in order:
        c, r = CROWD[i]
        sc = .46 + r * .07
        x = 95 + c * 132 + (r % 2) * 40 - 20 * u / 10 * (r + 1)
        y = 450 + r * 125
        pop = ease_back((u - .2 - r * .15 - c * .05) / .35)
        if pop <= 0: continue
        dim = 1.0
        if u > t_one and i != pick: dim = lerp(1, .45, ease_io((u - t_one) / .4))
        spr = A('person')
        if i == pick and u > t_one:
            spr = A('person_o'); sc *= lerp(1, 1.18, ease_back((u - t_one) / .35))
        f = blit(f, spr, x, y, sc * pop, 0, 1.0, shadow=(8, 12, 8, .4))
        if dim < 1:
            # fade toward the paper by overlaying a translucent wash on that figure
            f = blit(f, rgba(np.broadcast_to(PAPER * .9, spr.shape[:2] + (3,)).copy(), spr[..., 3] * (1 - dim)), x, y, sc * pop, 0, 1.0, shadow=None)
        if i == pick and u > t_one:
            px, py = x, y
    if u > t_one:
        c, r = CROWD[pick]
        px = 95 + c * 132 + (r % 2) * 40 - 20 * u / 10 * (r + 1); py = 450 + r * 125
        f = glow_spot(f, px, py, 110, (1, .6, .25), .35)
        d = drop_sprite(); rr = np.random.default_rng(7)
        for k in range(10):
            ph = ((u - t_one) * .9 + k / 10) % 1.0
            f = blit(f, d, px + rr.uniform(-70, 70), py - 150 + ph * 230, .28, 0, clamp01(1.3 - ph * 1.3), shadow=None)
    # HYPERHIDROSIS label drops in, then leaves
    e = ease_out((u - .25) / .45); out = ease_in((u - 3.4) / .4)
    if e > 0 and out < 1:
        y = lerp(-120, 230, e) - 500 * out
        f = blit(f, A('stHH_strip'), W / 2, y, 1.0, -3, 1.0, shadow=(8, 12, 8, .5))
        f = stamp(f, A('stHH_t'), W / 2, y, u - .75, 560, rot=-3, seed=5, dust=out == 0)
    f = stamp(f, A('st1in20'), W / 2 + 20, 230, u - (t_one + .45), 380, rot=-6, seed=6)
    f = draw_captions(f, 1, u)
    if u > 9.4: f = mblur(cover(f, 1, 0, 220 * ease_in((u - 9.4) / .6)), 0, 140 * ease_in((u - 9.4) / .6))
    return finish(f, u, enter=(0, 120))

# ------------------------------------------------------------ scene 3: inside the skin, millions of glands
def scene3(u):
    t_mil = ctime(2, 'million') + .1
    t_palm = ctime(2, 'hatheliyon') - .6
    if u < t_palm:
        sk = A('skin')
        q = ease_io5(clamp01((u - .2) / (t_palm - .6)))
        y0 = lerp(0, 1150, q)
        view = sk[int(y0):int(y0) + 1600]
        f = cover(view, 1.0 + .06 * q)
        # orange droplets on the surface pores at the start
        for k, (px, py) in enumerate(skin_section.pores):
            sy = (py - y0) * (H / 1600) / 1.0
            if -60 < sy < H:
                f = blit(f, drop_sprite(), px * W / 900, sy - 20, .32 * ease_back((u - .3 - k * .1) / .4), 0, 1.0, shadow=(3, 5, 3, .4))
        f = stamp(f, A('stMIL'), W / 2, 360, u - t_mil, 470, rot=-4, seed=7)
        if u > t_palm - .4: f = zoom_blur(f, ease_in((u - (t_palm - .4)) / .4) * 1.8)
    else:
        q = u - t_palm
        f = cover(A('panel'), 1.05 + .03 * q)
        e = ease_back(q / .4)
        f = blit(f, A('hand_s'), 220, 560, .9 * e, -6, 1.0, shadow=(12, 18, 12, .5))
        f = blit(f, A('feet_s'), 520, 600, .9 * e, 8, 1.0, shadow=(12, 18, 12, .5))
        rr = np.random.default_rng(9)
        n = int(min(1.0, q / 1.4) * 220)
        for k in range(n):  # dense orange dots = glands
            which = k % 2
            ax = icon_alpha('hand-palm' if which == 0 else 'footprints', 560 if which == 0 else 520)
            for _ in range(10):
                yy, xx = int(rr.uniform(0, ax.shape[0])), int(rr.uniform(0, ax.shape[1]))
                if ax[yy, xx] > .5: break
            cx0, cy0 = (220, 560) if which == 0 else (520, 600)
            x = cx0 + (xx - ax.shape[1] / 2) * .9; y = cy0 + (yy - ax.shape[0] / 2) * .9
            cv2.circle(f, (int(x), int(y)), 4, tuple(float(v) for v in ORANGE), -1, cv2.LINE_AA)
        if q < .3: f = zoom_blur(f, (.3 - q) / .3 * 1.6)
    f = draw_captions(f, 2, u)
    return finish(f, u, enter='zoom', exit_=(140, 0))

# ------------------------------------------------------------ scene 4: the nerve on full volume
NERVE = bezier(np.array([170, 420.]), np.array([420, 380.]), np.array([300, 820.]), np.array([560, 860.]))
def scene4(u):
    t_vol = ctime(3, 'full volume') - .2
    v = .18 + .82 * ease_io((u - t_vol) / .7)
    f = cover(A('nerve_bg'), 1.05 + .03 * u / 10, 0, 0)
    sx, sy = impact_shake(u, t_vol + .7, 10)
    # skin panel bottom right with a gland
    panel = np.zeros((H, W), np.float32); cv2.rectangle(panel, (380, 760), (W, H), 1, -1)
    f = f * (1 - panel[..., None] * .25) + panel[..., None] * np.array([.9, .74, .64], np.float32) * .25
    cv2.line(f, (380, 760), (W, 760), (.2, .15, .1), 3, cv2.LINE_AA)
    for j in range(24):
        a = j * .9
        cv2.ellipse(f, (590 + int(math.cos(a) * 24), 900 + int(math.sin(a) * 14)), (22, 13), math.degrees(a), 0, 360, (.15, .12, .1), 3, cv2.LINE_AA)
    cv2.line(f, (590, 880), (600, 762), (.15, .12, .1), 5, cv2.LINE_AA)
    f = blit(f, A('spine'), 120 + sx, 640 + sy, .85, 0, 1.0, shadow=(10, 14, 10, .5))
    f = nerve(f, NERVE + [sx, sy], v, u)
    # knob turns up
    kx, ky = 520, 330
    f = blit(f, A('knob'), kx, ky, .7, -lerp(-120, 120, ease_io((v - .18) / .82)) + 0, 1.0, shadow=(10, 14, 10, .5))
    f = stamp(f, A('stMAX'), kx, ky - 150, u - (t_vol + .7), 230, rot=-6, seed=8)
    # drops from the pore, rate grows with volume
    d = drop_sprite(); rr = np.random.default_rng(12)
    n = int(4 + 22 * v)
    for k in range(n):
        ph = (u * (.5 + .8 * v) + k / n) % 1.0
        ang = rr.uniform(-1.2, 1.2)
        x = 600 + math.sin(ang) * ph * 260; y = 750 - math.cos(ang) * ph * 300 + 480 * ph * ph
        f = blit(f, d, x, y, .26 + .1 * v, ang * 30, clamp01(1.4 - ph), shadow=None)
    # orange flood rising
    lvl = 40 + 150 * ease_io((u - t_vol - .3) / 2.5)
    yy = np.arange(W)
    top = (H - lvl + 8 * np.sin(yy / 30 + u * 4)).astype(int)
    m = (np.arange(H)[:, None] >= top[None, :]).astype(np.float32)
    f = f * (1 - m[..., None]) + orange_paper(H, W, 860) * .9 * m[..., None]
    f = draw_captions(f, 3, u)
    if u > 9.4: f = zoom_blur(f, ease_in((u - 9.4) / .6) * 1.6)
    return finish(f, u, enter=(140, 0))

# ------------------------------------------------------------ scene 5: the family tree
FAM = [(220, 300, .0), (500, 300, .2), (220, 610, .5), (500, 610, .7), (360, 900, 1.0)]
SWEATY = [0, 3, 4]
def scene5(u):
    t_genes = ctime(4, 'genes')
    t_fam = ctime(4, 'parivaar') - .3
    cy = -60 + 80 * ease_io(u / 10)
    f = cover(A('family_bg'), 1.04 + .03 * u / 10, 0, cy * .3)
    for (a, b) in ((0, 2), (1, 3), (2, 4), (3, 4), (0, 1), (2, 3)):
        e = ease_io((u - .6 - b * .12) / .5)
        if e > 0:
            x0, y0, _ = FAM[a]; x1, y1, _ = FAM[b]
            cv2.line(f, (x0, int(y0 - cy)), (int(lerp(x0, x1, e)), int(lerp(y0, y1, e) - cy)), (.18, .14, .1), 4, cv2.LINE_AA)
    for i, (x, y, t0) in enumerate(FAM):
        e = ease_back((u - .2 - t0 * .6) / .4)
        if e <= 0: continue
        lit = i in SWEATY and u > t_fam + SWEATY.index(i) * .45
        spr = A('portrait_o') if lit else A('portrait')
        f = blit(f, spr, x, y - cy, .62 * e, (-4 + i * 3) % 9 - 4, 1.0, shadow=(10, 14, 10, .5))
        if lit:
            q = u - t_fam - SWEATY.index(i) * .45
            f = glow_spot(f, x, y - cy, 120, (1, .6, .25), .25)
            f = drops_on(f, [(-60, -40), (55, -20), (-10, 50)], u, .62, x, y - cy, [t_fam + SWEATY.index(i) * .45 + k * .15 for k in range(3)], .9)
    # DNA twirls in with the word
    e = ease_out((u - t_genes + .2) / .5)
    if e > 0:
        f = blit(f, A('dna'), 610, 140 - cy * .5, .55 * e, 20 * math.sin(u * 2), 1.0, shadow=(8, 12, 8, .45))
    f = stamp(f, A('stGENES'), W / 2 - 40, 150 - cy * .5, u - t_genes, 400, rot=-5, seed=9)
    f = draw_captions(f, 4, u)
    if u > 9.4: f = mblur(cover(f, 1, -200 * ease_in((u - 9.4) / .6), 0), 140 * ease_in((u - 9.4) / .6), 0)
    return finish(f, u, enter=(0, 120))

# ------------------------------------------------------------ scene 6: sleep quiets the signal
def scene6(u):
    t_sleep = ctime(5, 'neend')
    t_calm = ctime(5, 'shaant') - .2
    v = 1 - ease_io((u - t_sleep) / 3.0)
    f = cover(A('night'), 1.06 - .03 * u / 10, 0, 0)
    f = blit(f, A('moon'), W * .5, 330 + 6 * math.sin(u), .9, -8, 1.0, shadow=None, glow=((.8, .85, 1.0), 30, .35))
    f = blit(f, A('bed'), W / 2 + 20, 830, .95, 0, 1.0, shadow=(14, 20, 14, .5))
    # the nerve along the wall, fading from orange to grey
    pts = bezier(np.array([0, 640.]), np.array([200, 600.]), np.array([260, 760.]), np.array([300, 800.]))
    col = ORANGE * v + np.array([.45, .43, .4], np.float32) * (1 - v)
    f = nerve(f, pts, v * .8, u, color=col if v < .98 else ORANGE)
    # drops on the pillow evaporate
    d = drop_sprite()
    for k, (dx, dy) in enumerate(((-150, -60), (-90, -90), (-200, -20), (-40, -50))):
        s = clamp01(v * 1.2 - k * .05)
        if s > .02: f = blit(f, d, W / 2 + dx, 830 + dy, .3 * s, 0, 1.0, shadow=None)
        if 0 < s < .9:
            rr = np.random.default_rng(k)
            for j in range(4):
                ph = (u * .7 + j / 4) % 1.0
                cv2.circle(f, (int(W / 2 + dx + rr.uniform(-15, 15)), int(830 + dy - ph * 90)), 3, (.9, .88, .82), -1, cv2.LINE_AA)
    # Zzz
    for k in range(3):
        ph = (u * .25 + k / 3) % 1.0
        if u > t_sleep:
            f = blit(f, A('z'), W / 2 - 160 + ph * 120 + k * 10, 700 - ph * 260, .5 + .4 * ph, -10, clamp01(1.2 - ph) * clamp01((u - t_sleep) / .5), shadow=None)
    # the knob turns down
    e = ease_io((u - t_calm) / .9)
    if u > t_calm - .3:
        a = clamp01((u - t_calm + .3) / .3)
        f = blit(f, A('knob'), 560, 560, .55, -lerp(120, -120, e), a, shadow=(8, 12, 8, .5))
    f = stamp(f, A('stSLEEP'), W / 2, 170, u - (t_sleep + .1), 380, rot=-5, seed=10)
    f = f * (1 - .9 * ease_in((u - 9.5) / .5))
    f = draw_captions(f, 5, u)
    return finish(f, u, enter=(-140, 0))

SCENES = [scene1, scene2, scene3, scene4, scene5, scene6]

GRAIN = None; VIG = None
def post(f, i):
    global GRAIN, VIG
    if GRAIN is None:
        GRAIN = [(np.random.default_rng(2000 + k).normal(0, 1, (H, W, 1)).astype(np.float32) * .03) for k in range(6)]
        VIG = vignette(H, W, .45, 2.2)
    f = tilt_shift(f, 5.0, .3, .47)
    f = f * np.array([1.04, .98, .88], np.float32)
    f = f * VIG + GRAIN[i % 6]
    r = np.random.default_rng(i)
    for _ in range(3):
        x, y = int(r.uniform(0, W)), int(r.uniform(0, H))
        if r.random() < .5: cv2.circle(f, (x, y), int(r.uniform(1, 3)), (.95, .92, .85) if r.random() < .5 else (.1, .08, .06), -1, cv2.LINE_AA)
        else: cv2.line(f, (x, y), (x + int(r.uniform(-20, 20)), y + int(r.uniform(-20, 20))), (.15, .12, .1), 1, cv2.LINE_AA)
    return np.clip(f, 0, 1)
