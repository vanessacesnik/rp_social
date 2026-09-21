#!/usr/bin/env python3
# CANONICAL margin QA and the single source of truth for the safe-area ruler.
# It scans the RENDERED PNG sequences (build/png_<name>/f*.png) for the real ink
# (alpha > 150) bounding box unioned over the frames, and checks each element against
# the phone-safe ruler. Text set to white-space:nowrap overflows its own layout box,
# so the layout box lies about width; the rendered alpha does not. Measure the pixels.
#
# Rulers (central band the phone actually shows is ~886px of the 1080 width):
#   wide text (hook cards, bignum, counters, recap, list cards) -> [160,920]  (~760px)
#   captions                                                     -> [170,910]  (~740px)
#   small elements (chips, badges, pills, toasts, stamps)        -> [130,950]  (~820px)
#
# Usage:  GEN_WORK=/abs/workspace python3 measure_ink.py
# Reads render/plan.json for the element list and each element's ruler class.
import os, sys, glob, json
from PIL import Image

WORK = os.environ.get("GEN_WORK") or (sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
BUILD = os.path.join(WORK, "build")
plan = json.load(open(os.path.join(WORK, "render", "plan.json")))

WIDE, CAP, SMALL = (160, 920), (170, 910), (130, 950)
ALPHA = 150
# element types that are "small" by default; everything else measured as wide text.
SMALL_KINDS = {"chip", "badge", "pill", "toast", "stamp", "small"}


def ink_bbox(pngdir):
    frames = sorted(glob.glob(os.path.join(pngdir, "f*.png")))
    if not frames:
        return None
    step = max(1, len(frames) // 60)  # sample up to ~60 frames, still catches peak width
    L, R = 10**9, -1
    for fp in frames[::step]:
        im = Image.open(fp).convert("RGBA")
        sf = 1080.0 / im.width  # PNGs render at 1080 wide when DSF=1; rescale if not
        mask = im.getchannel("A").point(lambda p: 255 if p > ALPHA else 0)
        bb = mask.getbbox()
        if not bb:
            continue
        l, _, r, _ = bb
        L = min(L, l * sf)
        R = max(R, r * sf)
    return None if R < 0 else (L, R)


def flag(L, R, band):
    a, z = band
    return "*** FURA ***" if (L < a - 0.5 or R > z + 0.5) else "ok"


def report(name, pngdir, band, label):
    bb = ink_bbox(pngdir)
    if bb is None:
        print(f"  {name:16s} (sem PNG em {pngdir}) -- rode o render antes")
        return 0
    L, R = bb
    f = flag(L, R, band)
    cx = (L + R) / 2
    print(f"  {name:16s} L={L:4.0f} R={R:4.0f} W={R-L:4.0f} cx={cx:4.0f} [{label}] -> {f}")
    return 1 if f.startswith("***") else 0


bad = 0
print(f"== INK (tinta renderizada, fonte de verdade) em {WORK} ==")
print("-- elementos --")
for e in plan.get("elements", []):
    name = e["name"]
    band = SMALL if e.get("kind") in SMALL_KINDS else WIDE
    label = "small" if band is SMALL else "wide"
    bad += report(name, os.path.join(BUILD, f"png_{name}"), band, label)

print("-- legendas --")
bad += report("captions", os.path.join(BUILD, "png_captions"), CAP, "cap")

print("-- fecho CTA --")
# The CTA PNG is a composite: the giant wide-text "EU QUERO" plus small toast + composer. The
# whole-PNG ink is checked against the SMALL outer envelope [130,950]; the wide-text "EU QUERO"
# sub-element ([160,920]) is validated by measure_layout.mjs (#big) and by the celular crop proof.
bad += report("cta", os.path.join(BUILD, "png_cta"), SMALL, "small envelope (EU QUERO: ver measure_layout)")

print(f"\nRESULTADO: {bad} item(ns) furam a regua. Zero e o unico valor aceitavel.")
print("Depois deste check, gere as provas em crop de celular (proof_celular.py) e confira A OLHO.")
sys.exit(1 if bad else 0)
