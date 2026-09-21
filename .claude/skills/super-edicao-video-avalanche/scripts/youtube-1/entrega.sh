#!/bin/zsh
# entrega_generica.sh <NN> <workspace> <render.mp4> <CTA1|CTA2> <"Nome da pasta">
set -e
S=~/.claude/skills/super-edicao-video-avalanche/scripts/youtube-1
W="$2"; R="$3"; CTA="$4"; NOME="$5"
cd "$W"
echo "[]" > cortes_vazio.json
# O corta_fino quer o JSON CRU do whisper (chave "transcription" com offsets em ms).
# Cada agente gravou o seu com nome e formato proprios: uns tem o dict do whisper, outros
# so a lista compacta [["palavra", ini, fim], ...]. Este passo normaliza para um arquivo
# unico, entao a entrega nao depende de qual convencao o agente daquele video usou.
python3 - <<'NORM'
import json, os, sys
# ORDEM IMPORTA: a transcricao tem que ser a do MASTER, nunca a da fonte, senao os
# tempos do corte fino apontam para outro lugar do audio.
cands = ['palavras_master.json', 'pal_master.json', 'palavras.json', 'pal.json']
mestres = [c for c in cands if 'master' in c]
for c in mestres:
    if not os.path.exists(c):
        continue
    d = json.load(open(c, encoding='utf-8'))
    if isinstance(d, dict) and 'transcription' in d:
        json.dump(d, open('words_corte.json', 'w', encoding='utf-8'), ensure_ascii=False)
        print('transcricao crua do master:', c); sys.exit(0)
for c in mestres:
    if not os.path.exists(c):
        continue
    d = json.load(open(c, encoding='utf-8'))
    if isinstance(d, list) and d and isinstance(d[0], (list, tuple)) and len(d[0]) >= 3:
        tr = [{'text': ' ' + str(w), 'offsets': {'from': int(float(a) * 1000), 'to': int(float(b) * 1000)}}
              for w, a, b in d]
        json.dump({'transcription': tr}, open('words_corte.json', 'w', encoding='utf-8'), ensure_ascii=False)
        print('lista compacta do master convertida:', c, len(tr), 'palavras'); sys.exit(0)
for c in cands:
    if not os.path.exists(c):
        continue
    d = json.load(open(c, encoding='utf-8'))
    if isinstance(d, list) and d and isinstance(d[0], (list, tuple)) and len(d[0]) >= 3:
        tr = [{'text': ' ' + str(w), 'offsets': {'from': int(float(a) * 1000), 'to': int(float(b) * 1000)}}
              for w, a, b in d]
        json.dump({'transcription': tr}, open('words_corte.json', 'w', encoding='utf-8'), ensure_ascii=False)
        print('lista compacta convertida:', c, len(tr), 'palavras'); sys.exit(0)
print('SEM TRANSCRICAO USAVEL'); sys.exit(1)
NORM
WORDS=words_corte.json
[ -f "$WORDS" ] || { echo "sem transcricao do master"; exit 1; }
echo "== 10 corte fino =="
python3 "$S/corta_fino.py" "$R" cortado.mp4 --words "$WORDS" --conteudo cortes_vazio.json --cauda 0 --plano plano.json | tail -2
echo "== provas =="
python3 "$S/audita_2s.py" cortado.mp4 | tail -4
python3 - <<'PY'
import numpy as np, subprocess
raw = subprocess.run(['ffmpeg','-v','error','-i','cortado.mp4','-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout
a = np.frombuffer(raw, dtype=np.int16).astype(np.float32)/32768
H=0.002; w=int(16000*H); n=len(a)//w
db = 20*np.log10(np.sqrt(np.maximum((a[:n*w].reshape(n,w)**2).mean(1), 1e-12)))
q=[]
for i in range(3, n-3):
    if db[i-3] > -30 and db[i+3] < -55:
        if q and i*H - q[-1] < 0.10: continue
        q.append(round(i*H,2))
print('PALAVRAS PARTIDAS:', len(q), q[:20])
PY
python3 "$S/prova_emendas.py" cortado.mp4 plano.json prova_emendas_final.txt | tail -2
echo "== 11 encerramento =="
ffmpeg -y -v error -i cortado.mp4 -i ~/workspace/t1-full/enc10.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k bruto_enc.mp4
python3 "$S/emenda_encerramento.py" bruto_enc.mp4 --saida com_enc.mp4 || true
[ -f com_enc.mp4 ] || cp bruto_enc.mp4 com_enc.mp4
echo "== 11 CTA =="
if [ "$CTA" = "CTA1" ]; then P=~/workspace/cta1-kimi/CTA1-kimi.mp4; else P=~/workspace/cta2-kimi/CTA2-kimi.mp4; fi
python3 "$S/insere_cta.py" com_enc.mp4 "$P" final.mp4 --cauda 10 | tail -4
ffprobe -v error -show_entries format=duration -of csv=p=0 final.mp4
echo "== 12 pacote =="
PASTA="/Users/naiarodrigues/Desktop/conteudo youtube/$NOME"
mkdir -p "$PASTA"
cp final.mp4 "$PASTA/$NOME.mp4"
[ -f thumbnail.png ] && cp thumbnail.png "$PASTA/thumbnail.png"
[ -f legenda.txt ] && cp legenda.txt "$PASTA/legenda.txt"
echo "ENTREGUE: $PASTA"
ls -la "$PASTA"
