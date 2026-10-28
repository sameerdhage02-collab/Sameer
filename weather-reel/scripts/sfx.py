# Synthesized music bed + cartoon SFX, no downloads.
import numpy as np, soundfile as sf
SR = 44100
rng = np.random.default_rng(7)
def t(d): return np.arange(int(d*SR))/SR
def env(n, a=0.005, r=0.2):
    x = np.arange(n)/SR; return np.minimum(1, x/a) * np.exp(-x/r)
def save(name, a, peak=0.9):
    a = a/ (np.max(np.abs(a))+1e-9) * peak
    sf.write(f"public/{name}.wav", a.astype(np.float32), SR)

# --- SFX ---
d = t(0.7); n = rng.standard_normal(len(d))
f = np.fft.rfft(n); fr = np.fft.rfftfreq(len(d), 1/SR)
w = np.fft.irfft(f * np.exp(-((fr-1800)/1500)**2), len(d))
sweep = np.sin(np.pi*d/0.7)**2
save("whoosh", w*sweep, 0.6)
d = t(0.18); save("pop", np.sin(2*np.pi*(900*d - 2500*d**2)) * env(len(d), .002, .05), 0.7)
d = t(1.2); save("boom", (np.sin(2*np.pi*(60*d + 40*np.exp(-d*8)/8)) + 0.3*rng.standard_normal(len(d))*np.exp(-d*20)) * env(len(d), .003, .35), 0.95)
d = t(0.9); save("ding", sum(np.sin(2*np.pi*f0*d)*np.exp(-d*k) for f0, k in [(1320,4),(1980,6),(2640,9)]), 0.5)
d = t(0.5); save("boing", np.sin(2*np.pi*(220*d + 30*np.sin(2*np.pi*14*d)/(2*np.pi*14)*20)) * env(len(d), .005, .2), 0.6)

# --- Music: 116 BPM bouncy loop ---
BPM = 116; beat = 60/BPM; total = 40.0
N = int(total*SR); mix = np.zeros(N)
def add(sig, at):
    i = int(at*SR); j = min(N, i+len(sig)); mix[i:j] += sig[:j-i]
kd = t(0.35); kick = np.sin(2*np.pi*(50*kd + 90*(1-np.exp(-kd*30))/30)) * env(len(kd), .001, .12)
hd = t(0.06); hat = rng.standard_normal(len(hd)) * env(len(hd), .001, .015); hat = np.diff(hat, prepend=0)
cd = t(0.2); clap = rng.standard_normal(len(cd)) * env(len(cd), .002, .06)
notes = {"C":261.63,"D":293.66,"E":329.63,"F":349.23,"G":392.0,"A":440.0,"B":493.88}
prog = [("C",["C","E","G"]),("A",["A","C","E"]),("F",["F","A","C"]),("G",["G","B","D"])]
nb = int(total/beat)
for b in range(nb):
    tb = b*beat
    add(kick*0.9, tb)
    add(hat*0.25, tb+beat/2)
    if b % 2 == 1: add(clap*0.35, tb)
    root, ch = prog[(b//4) % 4]
    # bass: octave bounce
    bd = t(beat*0.45); f0 = notes[root]/4 * (2 if b % 2 else 1)
    add(np.sign(np.sin(2*np.pi*f0*bd))*0.18*env(len(bd), .005, .15), tb)
    # marimba-ish plucks on offbeats
    for k2, nn in enumerate(ch):
        if (b + k2) % 3 == 0:
            pd = t(0.3); add(np.sin(2*np.pi*notes[nn]*2*pd)*np.exp(-pd*14)*0.22, tb + beat/2 + k2*0.04)
fade = np.ones(N); fl = int(1.5*SR); fade[-fl:] = np.linspace(1, 0, fl)
save("music", mix*fade, 0.5)
print("ok")
