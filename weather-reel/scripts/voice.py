# Local narration with Kokoro. One take per sentence, so caption timing is exact per sentence;
# words inside a sentence are spaced by character length.
import json, re, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
VOICE = sys.argv[1] if len(sys.argv) > 1 else "af_heart"
SPEED = 1.08
LINES = [
 "It's almost November in India. Sweaters should be coming out. Instead, the fans are still spinning.",
 "Blame a super El Niño. A giant patch of the Pacific Ocean is running a fever.",
 "That heat bends winds across the planet. This year, India's monsoon came up short.",
 "Now October is running hotter than normal across most of the country. Even the nights refuse to cool.",
 "El Niño is expected to peak around December. So winter may arrive late, and arrive weak.",
 "The calendar says winter. The weather says summer. Our seasons are being rewritten.",
]
k = Kokoro(".models/kokoro-v1.0.onnx", ".models/voices-v1.0.bin")
GAP = 0.18
def trim(a, sr, th=0.01):
    idx = np.where(np.abs(a) > th)[0]
    return a[max(idx[0]-int(.02*sr),0): idx[-1]+int(.06*sr)] if len(idx) else a
out = []
for i, line in enumerate(LINES):
    sents = re.findall(r"[^.!?]+[.!?]", line)
    audio, words, t = [], [], 0.0
    for s in sents:
        s = s.strip()
        a, sr = k.create(s.replace("Niño", "Neenyo"), voice=VOICE, speed=SPEED, lang="en-us")
        a = trim(a, sr); d = len(a)/sr
        toks = s.split(); w8 = [len(re.sub(r"\W", "", x)) + 2 for x in toks]; tot = sum(w8); c = t
        for x, w in zip(toks, w8):
            dd = d * w / tot; words.append({"w": x, "s": round(c, 3), "e": round(c+dd, 3)}); c += dd
        audio += [a, np.zeros(int(GAP*sr), dtype=a.dtype)]; t += d + GAP
    full = np.concatenate(audio)
    sf.write(f"public/vo{i+1}.wav", full, sr)
    out.append({"file": f"vo{i+1}.wav", "dur": round(len(full)/sr, 3), "words": words})
    print(i+1, round(len(full)/sr, 2))
json.dump(out, open("src/voice.json", "w"), indent=1)
