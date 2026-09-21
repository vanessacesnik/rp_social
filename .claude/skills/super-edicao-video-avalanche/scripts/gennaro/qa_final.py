#!/usr/bin/env python3
# Full QA on the final mp4: durations, A/V sync, decode, audio-seam click check, safe-area frame
# grid with guides (red at x=97/983 = what the phone shows; green at 112/968 = breathing), punch-in
# proof (before vs during), and the travessao guard on captions AND on every element HTML.
# Writes a grid png to build/qa/.
#
# v2 (2026-07-25): this is a GUARD, not a report. It now REPROVES:
#   - exit 1 with a QA_FAIL verdict listing every failed check (was: always exit 0, and the verdict
#     only looked at travessao, so a flagged click still printed "QA_DONE").
#   - the click check compares like with like: global p99.9 and local max now use the SAME sample
#     stride (before, global sampled 1-in-7 while local used every sample, which understated the
#     global p99.9 and manufactured false clicks).
#   - the travessao guard also scans the element HTML actually used in the plan, not only the
#     captions (INEGOCIAVEL #6 says zero travessao in everything on screen).
#   - final duration vs plan and A/V delta are now hard checks.
#
# Usage:  GEN_WORK=/abs/workspace python3 qa_final.py [final.mp4]
import json, os, subprocess, wave, struct, sys
from PIL import Image, ImageDraw, ImageFont

WORK = os.environ.get("GEN_WORK") or os.getcwd(); os.chdir(WORK)
plan = json.load(open("render/plan.json"))
VID = sys.argv[1] if len(sys.argv) > 1 else f"FINAL_{plan['slug']}_gennaro.mp4"
if not os.path.isfile(VID):
    sys.exit(f"QA_FAIL: video nao encontrado: {VID}")
QA = "build/qa"; os.makedirs(QA, exist_ok=True)
FONT = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "Montserrat-Bold.ttf")
KEEPS = plan["keeps"]; ND = plan["new_dur"]
cum = []; c = 0.0
for a, b in KEEPS:
    cum.append(c); c += (b - a)
SEAMS = [round(cum[i], 3) for i in range(1, len(KEEPS))]

FAILS = []          # cada item vira uma linha do veredito final
STRIDE = 7          # mesma amostragem para o global e para o local (comparacao justa)


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout.strip() or 0)


print("=== DURATIONS ===")
print(f"  base talking head: {plan['base_dur']:.2f}s -> {ND:.2f}s (removeu {plan['removed_total']:.2f}s) +outro {plan['outro']}")
final_dur = dur(VID)
print(f"  FINAL: {final_dur:.2f}s")
esperado = ND + plan["outro"]
if abs(final_dur - esperado) > 0.6:
    FAILS.append(f"duracao final {final_dur:.2f}s foge do esperado {esperado:.2f}s (delta {final_dur-esperado:+.2f}s)")

vd = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "csv=p=0", VID], capture_output=True, text=True).stdout.strip()
ad = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration", "-of", "csv=p=0", VID], capture_output=True, text=True).stdout.strip()
try:
    delta_ms = abs(float(vd) - float(ad)) * 1000
    print(f"  A/V sync: video={vd}s audio={ad}s (delta {delta_ms:.0f} ms)")
    if delta_ms > 120:
        FAILS.append(f"A/V fora de sync: delta {delta_ms:.0f} ms (limite 120)")
except ValueError:
    print(f"  A/V sync: video={vd} audio={ad}")
    FAILS.append("nao consegui ler as duracoes de video/audio para conferir sync")

r = subprocess.run(["ffmpeg", "-v", "error", "-i", VID, "-f", "null", "-"], capture_output=True, text=True)
decode_clean = not r.stderr.strip()
print(f"\n=== DECODE === {'CLEAN' if decode_clean else 'ERRORS: ' + r.stderr[:300]}")
if not decode_clean:
    FAILS.append("decode do mp4 final acusou erro")

# ---- audio seam click check ----
subprocess.run(["ffmpeg", "-y", "-i", VID, "-ac", "1", "-ar", "48000", QA + "/a.wav"], capture_output=True)
w = wave.open(QA + "/a.wav"); srr = w.getframerate(); n = w.getnframes()
if w.getsampwidth() != 2:
    w.close(); sys.exit("QA_FAIL: wav extraido nao e PCM 16-bit")
d = struct.unpack("<" + str(n) + "h", w.readframes(n)); w.close()
# global e local com o MESMO passo, senao a comparacao e desonesta e inventa clique.
diffs = sorted(abs(d[i] - d[i - STRIDE]) for i in range(STRIDE, len(d), STRIDE))
p999 = diffs[min(int(len(diffs) * 0.999), len(diffs) - 1)] if diffs else 0
print(f"\n=== AUDIO SEAMS (click check, stride={STRIDE} nos dois lados) global |step| p99.9={p999} ===")
clicks = 0
for k, s in enumerate(SEAMS):
    i0, i1 = int((s - 0.025) * srr), int((s + 0.025) * srr)
    lo, hi = max(STRIDE, i0), max(STRIDE + 1, i1)
    loc = max((abs(d[i] - d[i - STRIDE]) for i in range(lo, hi, STRIDE)), default=0)
    click = loc > p999 * 2.2
    clicks += click
    print(f"  seam {k+1:2d} t={s:6.2f}s localMaxStep={loc:5d} {'<CLICK?>' if click else 'ok'}")
print(f"  CLICKS flagged: {clicks}/{len(SEAMS)} (0 e o alvo)")
if clicks:
    FAILS.append(f"{clicks} emenda(s) de audio com clique acima do limiar")

# ---- safe-area frame grid ----
SAFE = (97, 983); RESP = (112, 968)


def frame(t, name):
    out = f"{QA}/{name}.png"
    subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", VID, "-frames:v", "1", out], capture_output=True)
    return out


def guides(im):
    dd = ImageDraw.Draw(im)
    for x in SAFE:
        dd.line([(x, 0), (x, im.height)], fill=(255, 40, 40), width=3)
    for x in RESP:
        dd.line([(x, 0), (x, im.height)], fill=(40, 220, 90), width=2)
    return im


def label(im, txt):
    dd = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype(FONT, 30)
    except Exception:
        f = ImageFont.load_default()
    dd.rectangle([0, 0, im.width, 46], fill=(0, 0, 0)); dd.text((10, 7), txt, fill=(255, 255, 255), font=f)
    return im


def grid(items, cols, outname, cellw=330):
    ims = []
    for t, name, cap in items:
        p = frame(t, name)
        if not os.path.isfile(p):
            continue
        im = Image.open(p).convert("RGB"); guides(im)
        h = int(im.height * cellw / im.width); im = im.resize((cellw, h)); label(im, cap); ims.append(im)
    if not ims:
        return
    rows = (len(ims) + cols - 1) // cols; ch = max(i.height for i in ims)
    cv = Image.new("RGB", (cols * cellw + (cols + 1) * 8, rows * ch + (rows + 1) * 8), (20, 20, 24))
    for i, im in enumerate(ims):
        rr, cc = divmod(i, cols); cv.paste(im, (8 + cc * (cellw + 8), 8 + rr * (ch + 8)))
    cv.save(f"{QA}/{outname}.png"); print("  saved", outname, cv.size)


print("\n=== SAFE-AREA FRAMES (guides x=97/983 red, 112/968 verde) ===")
items = [(round((e["off"] + e["en_end"]) / 2, 2), "f_" + e["name"], e["name"]) for e in plan["elements"]]
items.append((max(0.0, final_dur - 1.6), "f_cta", "CTA EU QUERO"))
grid(items, 5, "qa_safearea")

# ---- punch proof ----
if plan.get("punches"):
    def crop_head(t, name):
        p = frame(t, name); im = Image.open(p).convert("RGB"); return im.crop((150, 300, 930, 1150)).resize((300, 327))
    cells = []
    for q in plan["punches"][:3]:
        b = crop_head(q["s"] - 0.25, f"pb_{q['kind']}_{q['s']}"); dd = crop_head((q["s"] + q["e"]) / 2, f"pd_{q['kind']}_{q['s']}")
        label(b, "BEFORE 1.0x"); label(dd, f"{q['kind'].upper()} {q['phrase'][:16]}")
        cells += [b, dd]
    if cells:
        cw, chh = cells[0].size
        cv = Image.new("RGB", (2 * cw + 24, ((len(cells) + 1) // 2) * chh + 32), (20, 20, 24))
        for i, im in enumerate(cells):
            rr, cc = divmod(i, 2); cv.paste(im, (8 + cc * (cw + 8), 8 + rr * (chh + 8)))
        cv.save(f"{QA}/qa_punch.png"); print("  saved qa_punch", cv.size)

# ---- travessao: legendas E todo HTML que foi pro ar ----
DASHES = (chr(8212), chr(8211))          # em-dash, en-dash
print("\n=== TRAVESSAO (INEGOCIAVEL #6: zero em TUDO que aparece na tela) ===")
txt = open("captions/captions.json", encoding="utf-8").read()
tv = sum(txt.count(ch) for ch in DASHES)
print(f"  captions.json: {tv}")
if tv:
    FAILS.append(f"{tv} travessao(oes) na legenda")

html_alvo = []
for e in plan["elements"]:
    html_alvo.append(os.path.join("elements", "imgcard.html" if e.get("type") == "img" else e["name"] + ".html"))
html_alvo.append(os.path.join("elements", "e_cta.html"))
for hp in sorted(set(html_alvo)):
    if not os.path.isfile(hp):
        print(f"  {hp}: AUSENTE")
        FAILS.append(f"html do elemento nao encontrado: {hp}")
        continue
    h = open(hp, encoding="utf-8").read()
    ct = sum(h.count(ch) for ch in DASHES)
    print(f"  {hp}: {ct}")
    if ct:
        FAILS.append(f"{ct} travessao(oes) em {hp}")

# ---- veredito ----
print("\n" + "=" * 60)
if FAILS:
    print("QA_FAIL. Reprovado por:")
    for f in FAILS:
        print("  - " + f)
    print("=" * 60)
    sys.exit(1)
print("QA_DONE (duracao, sync, decode, cliques e travessao limpos)")
print("Falta ainda: measure_ink.py em 0 furos, verify_overlays.py em 0 ausentes,")
print("e a prova em crop de celular conferida A OLHO.")
print("=" * 60)
