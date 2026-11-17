# Aligns script segments to pauses in the voiceover (dynamic programming over detected silences).
import re, json, math
src = open('index.html').read().split('const SEGS = [')[1].split('];')[0]
texts = [m.group(1).replace('*', '').replace('_', '') for m in re.finditer(r"\['[a-z]+', '(.*?)'", src)]
SPOKEN = {'1977': 'उन्नीस सौ सतहत्तर', '1966': 'उन्नीस सौ छियासठ', '11 ': 'ग्यारह ', '03': 'ज़ीरो थ्री', 'R.N.': 'आर एन', 'Dr.': 'डॉक्टर'}
def spoken(t):
    for k, v in SPOKEN.items(): t = t.replace(k, v)
    return len(re.sub(r'[\s…,।:?.“”"]', '', t))
L = [spoken(t) for t in texts]
D = float(open('audio/duration.txt').read())
sil = [tuple(map(float, l.split())) for l in open('audio/silences.tsv') if l.strip()]
sil = [(s, e) for s, e in sil if e - s >= .28]
cands = [(s + e) / 2 for s, e in sil]; durs = [e - s for s, e in sil]
def speech(a, b):  # speech time between a and b
    x = b - a
    for s, e in sil: x -= max(0, min(b, e) - max(a, s))
    return max(x, .05)
total_speech = speech(0, D); rate = total_speech / sum(L)
n = len(texts); K = len(cands)
INF = 1e18
# dp[i][j]: segments 0..i-1 placed, boundary i at candidate j
best = [[INF] * K for _ in range(n)]; prev = [[-1] * K for _ in range(n)]
def cost(a, b, i, j):
    r = speech(a, b) / (L[i] * rate)
    return math.log(r) ** 2 - .15 * (durs[j] if j is not None else 0)
for j in range(K): best[0][j] = cost(0, cands[j], 0, j)
for i in range(1, n - 1):
    for j in range(K):
        for k in range(j):
            v = best[i - 1][k] + cost(cands[k], cands[j], i, j)
            if v < best[i][j]: best[i][j] = v; prev[i][j] = k
# last segment ends at D
fin = min(range(K), key=lambda k: best[n - 2][k] + cost(cands[k], D, n - 1, None))
bounds = [fin]
for i in range(n - 2, 0, -1): bounds.append(prev[i][bounds[-1]])
bounds = [cands[b] for b in reversed(bounds)]
starts = [0] + bounds; ends = bounds + [D]
for s, e, t in zip(starts, ends, texts): print(f'{s:6.2f} {e:6.2f} {e-s:5.2f}  {t[:44]}')
json.dump({'duration': D, 'starts': starts, 'ends': ends, 'silences': sil}, open('audio/align.json', 'w'), indent=1)
