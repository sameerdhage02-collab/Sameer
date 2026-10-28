# Local narration with Kokoro. One take per sentence, so caption timing is exact per sentence;
# words inside a sentence are spaced by character length.
import json, re, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
VOICE = sys.argv[1] if len(sys.argv) > 1 else "af_heart"
SPEED = 1.08
LINES = [
 "Your blood pressure just dropped. Deep inside your kidneys, an alarm goes off.",
 "Special cells in the kidney's arterioles sense the drop, and release an enzyme called renin.",
 "Renin snips angiotensinogen, a protein made by the liver, into angiotensin one.",
 "In the lungs, ACE trims it again, into angiotensin two, the real power player.",
 "Angiotensin two squeezes your blood vessels, and tells the adrenal glands to release aldosterone. Now the kidneys hold on to salt and water.",
 "Pressure climbs back to normal. Block this cascade with an ACE inhibitor, and you have a blood pressure drug.",
]
k = Kokoro(".models/kokoro-v1.0.onnx", ".models/voices-v1.0.bin")
GAP = 0.18
# Correct medical pronunciations: REE-nin, an-jee-oh-TEN-sin(-oh-jen).
FIX = [("ˈæŋɡɪˌoʊtənsˌɪnədʒən", "ˌændʒiːˌoʊtˌɛnsˈɪnədʒən"), ("ˈæŋɡɪˌoʊtənsˌɪn", "ˌændʒiːoʊtˈɛnsɪn"), ("ɹᵻnˈɪn", "ɹˈiːnɪn")]
def trim(a, sr, th=0.01):
    idx = np.where(np.abs(a) > th)[0]
    return a[max(idx[0]-int(.02*sr),0): idx[-1]+int(.06*sr)] if len(idx) else a
out = []
for i, line in enumerate(LINES):
    sents = re.findall(r"[^.!?]+[.!?]", line)
    audio, words, t = [], [], 0.0
    for s in sents:
        s = s.strip()
        ph = k.tokenizer.phonemize(s.replace("ACE", "ace"), "en-us")
        for a_, b_ in FIX: ph = ph.replace(a_, b_)
        a, sr = k.create(ph, voice=VOICE, speed=SPEED, is_phonemes=True)
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
