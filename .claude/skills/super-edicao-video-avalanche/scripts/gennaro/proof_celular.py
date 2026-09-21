#!/usr/bin/env python3
# Phone-screen proof. A full-screen Reels frame on a real phone hides the sides: the screen
# shows only the central ~886px of the 1080 width. This extracts key frames from the final mp4
# and crops them to exactly what the phone shows, at the real print size (590x1280), so you can
# eyeball that NOTHING touches the edges and there is visible breathing room on both sides.
#
# Usage:  GEN_WORK=/abs/workspace python3 proof_celular.py <final.mp4> t1 t2 t3 [t4 t5 t6]
# Pick 4 to 6 timestamps at the strongest moments (hook, bignum, an image card, the CTA).
import os, sys, subprocess

WORK = os.environ.get("GEN_WORK") or os.getcwd()
if len(sys.argv) < 3:
    sys.exit("usage: GEN_WORK=... proof_celular.py <final.mp4> t1 t2 t3 ...")
VID = sys.argv[1]
TS = [float(x) for x in sys.argv[2:]]
OUT = os.path.join(WORK, "proof", "celular")
os.makedirs(OUT, exist_ok=True)

for i, t in enumerate(TS, 1):
    out = os.path.join(OUT, f"prova-tela-celular-{i:02d}.png")
    r = subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t), "-i", VID, "-frames:v", "1",
         "-vf", "crop=886:1920:97:0,scale=590:1280", out],
        capture_output=True, text=True)
    ok = os.path.exists(out) and os.path.getsize(out) > 0
    print(f"  {'OK ' if ok else 'ERR'} prova {i:02d} @ {t:6.2f}s -> {out}")
    if not ok:
        print(r.stderr[-300:])
print(f"\n{len(TS)} provas em {OUT}. Confira A OLHO: nada encostando, respiro visivel dos dois lados.")
