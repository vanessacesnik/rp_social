#!/usr/bin/env python3
# Emits render/render_all.sh (Playwright PNG -> ProRes 4444 alpha, for captions + every element)
# and render/build.sh (ffmpeg: cut -> punch-ins -> composite overlays -> outro CTA -> concat -> sfx)
# straight from render/plan.json. Deterministic; re-run whenever the plan changes.
#
# Usage:  GEN_WORK=/abs/workspace python3 emit_pipeline.py [port]   (port default 8100)
# plan.json must carry: slug, new_dur, outro, cap_start, elements[], sfx[], and (for img
# elements) an "img" object {file, kb, accent, logos, title}. serve.sh must run on <port>.
import json, os, sys, urllib.parse

WORK = os.environ.get("GEN_WORK") or os.getcwd()
PORT = sys.argv[1] if len(sys.argv) > 1 else "8100"
U = f"http://127.0.0.1:{PORT}"
SEEK = os.path.abspath(os.path.join(os.path.dirname(__file__), "seek_render.mjs"))  # harness lives in the skill
p = json.load(open(os.path.join(WORK, "render", "plan.json")))
SLUG = p["slug"]
ND, OUTRO, elems, sfx = p["new_dur"], p["outro"], p["elements"], p["sfx"]
FINAL = f"FINAL_{SLUG}_gennaro.mp4"


def enc(s):
    return urllib.parse.quote(s, safe="")


def url_for(e):
    n, dur = e["name"], e["dur"]
    if e.get("type") == "img":
        c = e["img"]  # {file, kb, accent, logos, title}
        q = f"src={enc('/img/' + c['file'])}&dur={dur}&kb={c.get('kb','push')}&accent={c.get('accent','cyan')}&title={enc(c.get('title',''))}"
        if c.get("logos"):
            q += f"&logos={enc(c['logos'])}"
        return f"{U}/elements/imgcard.html?{q}"
    return f"{U}/elements/{n}.html?dur={dur}"


# ---------------- render_all.sh (PNG -> ProRes, 3-at-a-time to stay CPU-friendly) ----------------
PRORES = ("ffmpeg -y -framerate 30 -start_number 0 -i build/png_{nm}/f%05d.png "
          "-c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le -qscale:v 8 build/mov_{nm}.mov >/dev/null 2>&1")
R = ["#!/bin/bash", f"cd {WORK} || exit 1", "set -e",
     'echo "== render captions (2 halves) =="',
     "rm -rf build/png_captions; mkdir -p build/png_captions"]
half = round(ND / 2, 2)
R += [f'node "{SEEK}" "{U}/elements/caption_track.html" build/png_captions {half} 30 1 0 >build/log_cap1.txt 2>&1 &',
      f'node "{SEEK}" "{U}/elements/caption_track.html" build/png_captions {round(ND-half,2)} 30 1 {half} >build/log_cap2.txt 2>&1 &',
      "wait",
      'echo "cap frames: $(ls build/png_captions | wc -l | tr -d " ")"',
      "ffmpeg -y -framerate 30 -start_number 0 -i build/png_captions/f%05d.png -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le -qscale:v 8 build/mov_captions.mov >/dev/null 2>&1 && echo captions_enc_OK",
      'echo "== render elements =="']
alljobs = [(e["name"], url_for(e), e["dur"]) for e in elems]
alljobs.append(("cta", f"{U}/elements/e_cta.html?dur={OUTRO}", OUTRO))
batch = []


def flush(b):
    for (nm, url, dur) in b:
        R.append(f'( rm -rf build/png_{nm}; mkdir -p build/png_{nm}; '
                 f'node "{SEEK}" "{url}" build/png_{nm} {dur} 30 1 0 >build/log_{nm}.txt 2>&1; '
                 f'{PRORES.format(nm=nm)} ) &')
    R.append("wait")
    R.append('echo "batch done: ' + " ".join(nm for nm, _, _ in b) + '"')


for j in alljobs:
    batch.append(j)
    if len(batch) == 3:
        flush(batch); batch = []
if batch:
    flush(batch)
R.append("echo RENDER_ALL_DONE")
open(os.path.join(WORK, "render", "render_all.sh"), "w").write("\n".join(R) + "\n")

# ---------------- build.sh (base is input 0; elements from input 1; captions last) ----------------
inputs = [f"-itsoffset {e['off']:.3f} -i build/mov_{e['name']}.mov" for e in elems]
inputs.append("-itsoffset 0 -i build/mov_captions.mov")
cap_idx = len(elems) + 1
inputs_str = " \\\n ".join(inputs)
chain = []
prev = "[0:v]"
for i, e in enumerate(elems):
    out = f"[v{i+1}]"
    chain.append(f"{prev}[{i+1}:v]overlay=0:0:enable='between(t,{e['off']:.3f},{e['en_end']:.3f})':eof_action=pass{out}")
    prev = out
chain.append(f"{prev}[{cap_idx}:v]overlay=0:0:enable='between(t,{p['cap_start']:.3f},{ND:.3f})':eof_action=pass[vo]")
main_filter = ";\\\n".join(chain)

KMAP = {"whoosh": "assets/sfx/whoosh.wav", "tick": "assets/sfx/tick.wav", "ding": "assets/sfx/ding.wav"}
# Os SFX vivem em assets/, nao em scripts/. Na unificacao as pastas se separaram e o caminho
# relativo herdado (scripts/../assets/sfx) deixou de existir: o build ia ate o passo 6 e morria
# em "No such file or directory", com o video pronto e sem audio final. Terceiro caso do mesmo
# gotcha (playwright e fonte Bricolage foram os outros), entao aqui a busca e explicita.
def _acha_sfx():
    aqui = os.path.dirname(os.path.abspath(__file__))
    for c in (os.path.join(aqui, "..", "..", "assets", "gennaro", "sfx"),
              os.path.join(aqui, "..", "..", "assets", "sfx"),
              os.path.join(aqui, "..", "assets", "sfx"),
              os.path.join(aqui, "assets", "sfx")):
        if os.path.isdir(c) and os.path.isfile(os.path.join(c, "whoosh.wav")):
            return c
    raise SystemExit("SFX nao encontrados (whoosh/tick/ding.wav). Procurei em assets/gennaro/sfx "
                     "e vizinhos a partir de " + aqui)
SFXDIR = _acha_sfx()
sfx_inputs = " ".join(f"-i {os.path.abspath(os.path.join(SFXDIR, s['kind'] + '.wav'))}" for s in sfx)
sfx_chain = [f"[{i+1}]adelay={s['ms']}|{s['ms']},volume={s['vol']}[a{i+1}]" for i, s in enumerate(sfx)]
mixins = "".join(f"[a{i+1}]" for i in range(len(sfx)))
sfx_filter = ";".join(sfx_chain) + f";[0:a]{mixins}amix=inputs={len(sfx)+1}:normalize=0:duration=first[am]"

B = f"""#!/bin/bash
cd {WORK} || exit 1
set -e
mkdir -p build
echo "== 0. SINCRONIA PNG -> ProRes (o erro mais caro do pipeline) =="
# Re-renderizar um elemento gera PNG novo, mas o build consome o .mov. Sem esta etapa, o video
# sai montado com a VERSAO ANTIGA do elemento e nenhum verificador acusa: o overlay esta la, so
# que errado. Ja aconteceu duas vezes; agora o build compara as datas e re-encoda sozinho.
for pd in build/png_*; do
  nm=$(basename "$pd" | sed 's/^png_//')
  [ "$nm" = "captions" ] && continue
  novo=$(ls -t "$pd"/f*.png 2>/dev/null | head -1)
  [ -z "$novo" ] && continue
  mov="build/mov_$nm.mov"
  if [ ! -f "$mov" ] || [ "$novo" -nt "$mov" ]; then
    echo "   re-encodando $nm (PNG mais novo que o mov)"
    ffmpeg -y -framerate 30 -start_number 0 -i "$pd/f%05d.png" -c:v prores_ks -profile:v 4444 \
      -pix_fmt yuva444p10le -qscale:v 8 "$mov" >/dev/null 2>&1 || {{ echo "SYNC_FAIL $nm"; exit 1; }}
  fi
done
if [ -d build/png_captions ]; then
  novo=$(ls -t build/png_captions/f*.png 2>/dev/null | head -1)
  if [ -n "$novo" ] && {{ [ ! -f build/mov_captions.mov ] || [ "$novo" -nt build/mov_captions.mov ]; }}; then
    echo "   re-encodando captions"
    ffmpeg -y -framerate 30 -start_number 0 -i build/png_captions/f%05d.png -c:v prores_ks \
      -profile:v 4444 -pix_fmt yuva444p10le -qscale:v 8 build/mov_captions.mov >/dev/null 2>&1
  fi
fi

echo "== 1+2. CUT + PUNCH-INS numa passada so (jump cuts word-level, micro-fade 10ms, zoom de rosto) =="
# Uma geracao de x264 a menos: o punch le [vv] direto da saida do cut, em vez de reencodar
# build/base_flat.mp4. Menos perda por recompressao e menos tempo de render.
ffmpeg -y -i original.mp4 -filter_complex_script render/cut_punch_filter.txt \\
  -map "[vout]" -map "[aa]" -r 30 -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p \\
  -c:a aac -b:a 192k -ar 48000 -ac 2 build/base_punch.mp4 2>build/cutpunch.log \\
  && echo "cut+punch OK $(ffprobe -v error -show_entries format=duration -of csv=p=0 build/base_punch.mp4)" || {{ echo CUTPUNCH_FAIL; tail -10 build/cutpunch.log; exit 1; }}

echo "== 3. MAIN composite (overlays on the timeline of the fala) =="
ffmpeg -y -i build/base_punch.mp4 \\
 {inputs_str} \\
 -filter_complex "{main_filter}" \\
 -map "[vo]" -map 0:a -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p \\
 -c:a aac -b:a 192k -ar 48000 -ac 2 build/main.mp4 2>build/main_ff.log \\
 && echo "main OK $(ffprobe -v error -show_entries format=duration -of csv=p=0 build/main.mp4)" || {{ echo MAIN_FAIL; tail -8 build/main_ff.log; exit 1; }}

echo "== 4. OUTRO (freeze last frame + CTA signature) =="
ffmpeg -y -sseof -0.15 -i build/main.mp4 -frames:v 1 build/last.png >/dev/null 2>&1
ffmpeg -y -loop 1 -t {OUTRO} -i build/last.png -f lavfi -t {OUTRO} -i anullsrc=channel_layout=stereo:sample_rate=48000 \\
  -i build/mov_cta.mov \\
  -filter_complex "[0:v]scale=1080:1920,setsar=1[bg];[bg][2:v]overlay=0:0:eof_action=pass[vo]" \\
  -map "[vo]" -map 1:a -t {OUTRO} -r 30 -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p \\
  -c:a aac -b:a 192k -ar 48000 -ac 2 build/outro.mp4 2>build/outro_ff.log \\
  && echo "outro OK" || {{ echo OUTRO_FAIL; tail -6 build/outro_ff.log; exit 1; }}

echo "== 5. CONCAT main + outro =="
ffmpeg -y -i build/main.mp4 -i build/outro.mp4 \\
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \\
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p \\
  -c:a aac -b:a 192k -ar 48000 build/full.mp4 2>build/concat.log && echo "concat OK"

echo "== 6. SFX mix (subtle whoosh on entrances, tick on logos, ding on the DM) =="
ffmpeg -y -i build/full.mp4 {sfx_inputs} \\
 -filter_complex "{sfx_filter}" \\
 -map 0:v -map "[am]" -c:v copy -c:a aac -b:a 192k -ar 48000 build/final.mp4 2>build/sfx.log && echo "sfx OK"

cp build/final.mp4 {FINAL}
echo "== DONE =="
ffprobe -v error -show_entries format=duration:stream=width,height,codec_name -of default=noprint_wrappers=1 {FINAL} 2>/dev/null
echo BUILD_DONE
"""
# ---- filtro fundido cut+punch (cut termina em [vv][aa]; punch passa a ler [vv]) ----
_cut = open(os.path.join(WORK, "render", "cut_filter.txt"), encoding="utf-8").read().rstrip().rstrip(";")
_pun = open(os.path.join(WORK, "render", "punch_filter.txt"), encoding="utf-8").read().strip()
assert "[vv][aa]" in _cut, "cut_filter.txt nao termina em [vv][aa]; rode o cut_plan.py de novo"
assert _pun.startswith("[0:v]split"), "punch_filter.txt em formato inesperado"
_pun = _pun.replace("[0:v]split", "[vv]split", 1).rstrip().rstrip(";")
open(os.path.join(WORK, "render", "cut_punch_filter.txt"), "w").write(_cut + ";\n" + _pun + "\n")

open(os.path.join(WORK, "render", "build.sh"), "w").write(B)
print("emitted render/render_all.sh + render/build.sh for slug:", SLUG)
print("elements:", [e["name"] for e in elems], "| sfx:", len(sfx), "| main chains:", len(chain))
for e in elems:
    print(f"  url {e['name']:14s} dur={e['dur']:.2f} -> {url_for(e)[:100]}")
