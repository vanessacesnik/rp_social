#!/usr/bin/env python3
# Confirm the animations actually MOVE (not a frozen poster): burst frames inside each element
# window and diff consecutive frames ON THE REGION WHERE THAT ELEMENT ACTUALLY IS.
#
# v2 (2026-07-25): the crop is now derived per element from the rendered PNG ink bbox
# (build/png_<name>/), instead of one hardcoded lower-third band for every html element and one
# hardcoded box for every image card. With the fixed band, any element living outside it (hook card
# at the top, corner stamp, full-frame card) was measured on empty pixels and came back "STATIC?!"
# when it was fine, or "MOVE OK" when it was frozen. Falls back to the old band only when the PNG
# sequence is missing.
#
# Usage:  GEN_WORK=/abs/workspace python3 verify_motion.py [final.mp4]
import subprocess, os, glob, json, sys
from PIL import Image, ImageChops, ImageStat

WORK = os.environ.get("GEN_WORK") or os.getcwd(); os.chdir(WORK)
plan = json.load(open("render/plan.json")); ND = plan["new_dur"]
VID = sys.argv[1] if len(sys.argv) > 1 else f"FINAL_{plan['slug']}_gennaro.mp4"
if not os.path.isfile(VID):
    sys.exit(f"MOTION_FAIL: video nao encontrado: {VID}")

LOW_FALLBACK = "1080:700:0:1044"     # lower third, so usado quando nao ha PNG do elemento
ALPHA = 150
W, H = 1080, 1920


def ink_box(pngdir):
    """Bounding box (x0,y0,x1,y1) da tinta real, unida sobre uma amostra dos frames."""
    frames = sorted(glob.glob(os.path.join(pngdir, "f*.png")))
    if not frames:
        return None
    step = max(1, len(frames) // 40)
    box = None
    for fp in frames[::step]:
        im = Image.open(fp).convert("RGBA")
        sf = W / im.width
        bb = im.getchannel("A").point(lambda p: 255 if p > ALPHA else 0).getbbox()
        if not bb:
            continue
        b = (bb[0] * sf, bb[1] * sf, bb[2] * sf, bb[3] * sf)
        box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    return box


def crop_for(name):
    box = ink_box(os.path.join("build", f"png_{name}"))
    if box is None:
        return LOW_FALLBACK, "fallback"
    pad = 24
    x0 = max(0, int(box[0]) - pad); y0 = max(0, int(box[1]) - pad)
    x1 = min(W, int(box[2]) + pad); y1 = min(H, int(box[3]) + pad)
    w = max(64, x1 - x0); h = max(64, y1 - y0)
    w = min(w, W - x0); h = min(h, H - y0)
    return f"{w}:{h}:{x0}:{y0}", "ink"


def burst(t0, d, fps, outdir, crop):
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(outdir + "/*.png"):
        os.remove(f)
    subprocess.run(["ffmpeg", "-y", "-ss", str(t0), "-t", str(d), "-i", VID,
                    "-vf", f"fps={fps},crop={crop}", outdir + "/f%03d.png"], capture_output=True)
    return sorted(glob.glob(outdir + "/f*.png"))


def diffs(files):
    ims = [Image.open(f).convert("L") for f in files]
    out = []
    for a, b in zip(ims, ims[1:]):
        dd = ImageChops.difference(a, b); out.append(round(ImageStat.Stat(dd).mean[0], 2))
    return out


wins = []
for e in plan["elements"]:
    crop, src = crop_for(e["name"])
    d = min(e["dur"] - 0.2, 4.0) if e["dur"] > 0.7 else max(0.5, e["dur"])
    wins.append((e["name"], e["off"] + 0.15, d, crop, src))
cta_crop, cta_src = crop_for("cta")
wins.append(("cta", ND + 0.05, min(3.7, plan["outro"] - 0.1), cta_crop, cta_src))

allok = True
for name, t0, d, crop, src in wins:
    fs = burst(t0, d, 10, "build/mot_" + name, crop); ds = diffs(fs)
    nz = sum(1 for x in ds if x > 0.25); ok = nz >= 3
    allok = allok and ok
    print(f"[{name:14s}] crop={crop:22s} ({src}) {len(fs)} frames | moving(>0.25)={nz}/{len(ds)} "
          f"max={max(ds) if ds else 0:.1f} -> {'MOVE OK' if ok else 'STATIC?!'}")
print("MOTION_OK" if allok else "MOTION_SUSPECT")
sys.exit(0 if allok else 1)
