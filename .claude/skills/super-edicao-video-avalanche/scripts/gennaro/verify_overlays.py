#!/usr/bin/env python3
# NOVO em v2 (2026-07-25). Prova que CADA overlay do plano REALMENTE aparece no video final.
#
# Por que existe: o build monta um filter_complex com um input por elemento e um `enable=between(...)`
# por janela. Um indice deslocado, um mov que nao renderizou ou uma janela fora do tempo fazem o
# overlay sumir SEM ERRO NENHUM: o ffmpeg entrega um mp4 perfeito, so que sem o elemento. Ate agora
# o unico jeito de pegar isso era olhar frame a frame. Este script pega automaticamente.
#
# Como prova: compara o FINAL com a base pre-overlay (build/base_punch.mp4) no MESMO instante,
# dentro da bbox onde o elemento deveria estar (tinta real do PNG renderizado). Se a base e o final
# forem praticamente iguais naquela regiao, o overlay nao entrou.
#
# Usage:  GEN_WORK=/abs/workspace python3 verify_overlays.py [final.mp4]
import subprocess, os, glob, json, sys
from PIL import Image, ImageChops, ImageStat

WORK = os.environ.get("GEN_WORK") or os.getcwd(); os.chdir(WORK)
plan = json.load(open("render/plan.json"))
VID = sys.argv[1] if len(sys.argv) > 1 else f"FINAL_{plan['slug']}_gennaro.mp4"
BASE = "build/base_punch.mp4"
OUT = "build/ovl"; os.makedirs(OUT, exist_ok=True)
ALPHA = 150; W, H = 1080, 1920
DIFF_MIN = 3.0          # diferenca media minima (0-255) para considerar que tem algo por cima

if not os.path.isfile(VID):
    sys.exit(f"OVERLAYS_FAIL: final nao encontrado: {VID}")
if not os.path.isfile(BASE):
    sys.exit(f"OVERLAYS_SKIP: {BASE} nao existe (rode o build antes; sem a base nao da pra provar)")


def ink_box(pngdir):
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


def grab(src, t, out):
    subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1", out], capture_output=True)
    return out if os.path.isfile(out) else None


falhas = []
print("=== PRESENCA DE OVERLAY (final vs base pre-overlay, na regiao do elemento) ===")
for e in plan["elements"]:
    name = e["name"]
    t = round((e["off"] + e["en_end"]) / 2, 3)
    box = ink_box(os.path.join("build", f"png_{name}"))
    if box is None:
        print(f"  {name:14s} SEM PNG renderizado (build/png_{name}) -> nao da pra provar")
        falhas.append(f"{name}: sem PNG renderizado")
        continue
    x0, y0, x1, y1 = (max(0, int(box[0])), max(0, int(box[1])), min(W, int(box[2])), min(H, int(box[3])))
    if x1 - x0 < 8 or y1 - y0 < 8:
        print(f"  {name:14s} PNG praticamente vazio (bbox {x1-x0}x{y1-y0}) -> elemento nao desenhou nada")
        falhas.append(f"{name}: PNG vazio")
        continue
    fa = grab(VID, t, f"{OUT}/{name}_final.png")
    fb = grab(BASE, t, f"{OUT}/{name}_base.png")
    if not fa or not fb:
        print(f"  {name:14s} nao consegui extrair o frame em t={t}")
        falhas.append(f"{name}: frame nao extraido")
        continue
    a = Image.open(fa).convert("RGB").crop((x0, y0, x1, y1))
    b = Image.open(fb).convert("RGB").crop((x0, y0, x1, y1))
    if a.size != b.size:
        b = b.resize(a.size)
    dmean = ImageStat.Stat(ImageChops.difference(a, b)).mean
    score = sum(dmean) / len(dmean)
    ok = score >= DIFF_MIN
    print(f"  {name:14s} t={t:6.2f} box=({x0},{y0})-({x1},{y1}) diff={score:6.2f} -> {'PRESENTE' if ok else 'AUSENTE ?!'}")
    if not ok:
        falhas.append(f"{name}: overlay ausente no video final (diff {score:.2f} < {DIFF_MIN})")

print()
if falhas:
    print("OVERLAYS_FAIL. Problemas:")
    for f in falhas:
        print("  - " + f)
    print("Causa tipica: indice de input deslocado no filter_complex, mov que nao renderizou,")
    print("ou janela enable fora do tempo. Confira render/build.sh e build/log_<nome>.txt.")
    sys.exit(1)
print("OVERLAYS_OK (todo elemento do plano aparece de fato no final)")
