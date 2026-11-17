# Synthesises a sound bed synced to timeline.json (written by render.js).
import json, wave, numpy as np
SR = 44100
tl = json.load(open('timeline.json'))
N = int((tl['total'] + .5) * SR); t = np.arange(N) / SR
rs = np.random.default_rng(7)
def env(n, a, d): x = np.arange(n) / SR; return np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / d)
def brown(n):
    w = rs.standard_normal(n); b = np.cumsum(w); b -= np.convolve(b, np.ones(2001) / 2001, 'same'); return b / (np.abs(b).max() + 1e-9)
def lp(x, k): return np.convolve(x, np.ones(k) / k, 'same')
mix = np.zeros((N, 2))
# drone: detuned low sines + slow swell + brown-noise air
dr = (np.sin(2*np.pi*55*t) + .7*np.sin(2*np.pi*55.4*t) + .4*np.sin(2*np.pi*82.4*t + np.sin(t*.3))) * (.55 + .45*np.sin(2*np.pi*t/9)**2)
air = brown(N) * .5
fade = np.minimum(1, t / 2) * np.minimum(1, (tl['total'] - t) / 2).clip(0)
mix[:, 0] += (dr * .05 + air * .05) * fade; mix[:, 1] += (dr * .05 + air * .045) * fade
# slow heartbeat pulse under everything (kept soft: narration sits on top)
for bt in np.arange(1.0, tl['total'] - 1, 1.15):
    for off, g in ((0, 1), (.22, .6)):
        i = int((bt + off) * SR); n = int(.25 * SR)
        if i + n < N: s = np.sin(2*np.pi*48*np.arange(n)/SR) * env(n, .005, .06) * .09 * g; mix[i:i+n] += s[:, None]
def add(at, sig, gain=1, pan=0):
    i = int(at * SR); sig = sig[:max(0, N - i)]
    if i < 0 or not len(sig): return
    mix[i:i+len(sig), 0] += sig * gain * (1 - max(0, pan)); mix[i:i+len(sig), 1] += sig * gain * (1 + min(0, pan))
def crash():
    n = int(2.5 * SR); x = np.arange(n) / SR
    boom = np.sin(2*np.pi*(60*np.exp(-x*3) + 30)*x) * env(n, .002, .5)
    noise = lp(rs.standard_normal(n), 3) * env(n, .001, .25)
    glass = rs.standard_normal(n) * env(n, .001, .5) * (x > .05) * .3
    glass = glass - lp(glass, 4)
    return np.tanh((boom * 1.2 + noise * .8 + glass) * 1.5) * .7
def horn():
    n = int(1.3 * SR); x = np.arange(n) / SR
    s = np.sign(np.sin(2*np.pi*233*x)) * .5 + np.sign(np.sin(2*np.pi*294*x)) * .5
    return lp(s, 6) * np.minimum(1, x / .05) * np.minimum(1, (1.3 - x) / .1) * np.linspace(.4, 1, n) * .22
def stamp():
    n = int(.6 * SR); x = np.arange(n) / SR
    return np.tanh((np.sin(2*np.pi*(120*np.exp(-x*20) + 50)*x) * env(n, .001, .08) * 1.5 + lp(rs.standard_normal(n), 2) * env(n, .0005, .02)) * 2) * .5
def whoosh(d=.7):
    n = int(d * SR); x = np.arange(n) / SR
    s = lp(rs.standard_normal(n), 12) * np.sin(np.pi * x / d) ** 2
    return s / np.abs(s).max() * .16
def heartstop():
    n = int(2.2 * SR); x = np.arange(n) / SR
    s = np.sin(2*np.pi*220*x) * .4 + np.sin(2*np.pi*440*x) * .1
    return s * np.minimum(1, x / .3) * np.minimum(1, (2.2 - x) / .8) * .12
def click():
    n = int(.25 * SR); x = np.arange(n) / SR
    s = rs.standard_normal(n) * env(n, .0005, .012) + np.sin(2*np.pi*2400*x) * env(n, .001, .03) * .3
    return s * .25
def blow():
    n = int(.5 * SR); x = np.arange(n) / SR
    s = lp(rs.standard_normal(n), 6) * np.sin(np.pi * x / .5) ** 1.5
    return s / np.abs(s).max() * .12
fx = {'crash': (crash, 0), 'horn': (horn, -.3), 'stamp': (stamp, 0), 'whoosh': (whoosh, .2), 'cut': (lambda: whoosh(.5), 0), 'heartstop': (heartstop, 0), 'blow': (blow, 0), 'click': (click, .2)}
for ev in tl['events']:
    f, pan = fx[ev['type']]; sig = f()
    at = ev['t'] - (.35 if ev['type'] == 'cut' else 0)
    add(at, sig, 1, pan)
# soft limiter + normalise
mix = np.tanh(mix * 1.4); mix /= np.abs(mix).max() / .85
with wave.open('soundbed.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype('<i2').tobytes())
print('events', len(tl['events']), 'dur', round(N / SR, 2))
