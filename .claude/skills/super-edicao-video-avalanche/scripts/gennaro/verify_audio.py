#!/usr/bin/env python3
# Voice continuity at the cut seams (speech or a designed breath, never a hole) and SFX presence.
# The SFX layer is isolated as final-minus-(pre-sfx build/full.mp4), so each whoosh/tick/ding shows
# as a bump above its neighbors. Also lists long voice gaps so a swallowed word is caught.
#
# Usage:  GEN_WORK=/abs/workspace python3 verify_audio.py [final.mp4]
import subprocess, wave, struct, math, json, os, sys

WORK = os.environ.get("GEN_WORK") or os.getcwd(); os.chdir(WORK)
plan = json.load(open("render/plan.json")); ND = plan["new_dur"]
VID = sys.argv[1] if len(sys.argv) > 1 else f"FINAL_{plan['slug']}_gennaro.mp4"


def load(path):
    subprocess.run(["ffmpeg", "-y", "-i", path, "-ac", "1", "-ar", "16000", path + ".v.wav"], capture_output=True)
    w = wave.open(path + ".v.wav"); n = w.getnframes(); sr = w.getframerate()
    d = struct.unpack("<" + str(n) + "h", w.readframes(n)); w.close()
    return list(d), sr


fin, sr = load(VID)
full, _ = load("build/full.mp4")  # pre-SFX render
N = min(len(fin), len(full)); win = int(0.05 * sr)


def env(data):
    e = []
    for i in range(0, len(data), win):
        s = data[i:i + win]
        if not s:
            break
        e.append(math.sqrt(sum(x * x for x in s) / len(s)))
    return e


E_full = env(full[:N]); diff = [fin[i] - full[i] for i in range(N)]; E_sfx = env(diff)


def at(E, t):
    i = int(t / 0.05); return round(E[i], 1) if 0 <= i < len(E) else -1


KEEPS = plan["keeps"]; cum = []; c = 0.0
for a, b in KEEPS:
    cum.append(c); c += (b - a)
SEAMS = [round(cum[i], 3) for i in range(1, len(KEEPS))]
print("=== VOZ nos cortes (RMS ao redor da emenda; fala ou respiro desenhado, sem buraco) ===")
for s in SEAMS[:8] + SEAMS[-3:]:
    print(f"  emenda t={s:6.2f}: {[at(E_full, s + dt) for dt in (-0.2, -0.05, 0.05, 0.2)]}")
print("=== SFX (residual final-menos-presfx; bump vs vizinhos = SFX ali) ===")
for s in plan["sfx"]:
    t = s["ms"] / 1000.0
    print(f"  {s['kind']:6s} t={t:6.2f}: pre={at(E_sfx, t - 0.15)} AT={at(E_sfx, t + 0.04)} post={at(E_sfx, t + 0.3)}")
thr = 180; gaps = []; start = None; run = 0.0
for i, r in enumerate(E_full):
    t = i * 0.05
    if 3 <= t <= ND - 0.2:
        if r < thr:
            if start is None:
                start = round(t, 2)
            run += 0.05
        else:
            if start is not None and run >= 0.5:
                gaps.append((start, round(run, 2)))
            start = None; run = 0.0
if start is not None and run >= 0.5:
    gaps.append((start, round(run, 2)))
print(f"=== buracos de voz >0.5s em 3..{ND-0.2:.1f}s (pausas naturais ok):", gaps)
print("VERIFY_AUDIO_DONE")
