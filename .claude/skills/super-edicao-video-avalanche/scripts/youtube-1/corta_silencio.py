#!/usr/bin/env python3
"""
corta_silencio.py entrada.mp4 saida.mp4 --words palavras.json [--offset 0]
                  [--conteudo cortes.json] [--limiar -40] [--min 0.30]

Corta pausa de um video JA RENDERIZADO, e opcionalmente tira trechos de conteudo
(repeticao e divagacao) no mesmo passe.

POR QUE ESTA VERSAO EXISTE. A primeira media so a energia do audio, com guarda fixa
de 90ms, e comia a ultima palavra das frases: consoante final (s, r, m, ão) tem
energia baixa e cai abaixo do limiar, entao o corte avancava por cima dela. O Chefe
pegou isso assistindo, em 04/08/2026. A regra ja estava escrita em nucleo/corte-fino.md
e nao foi seguida.

O METODO, agora com DUAS fontes que se corrigem:
  1. energia (envelope RMS em janelas de 25ms) diz ONDE pode haver pausa;
  2. os tempos por palavra do whisper dizem onde NAO PODE cortar, de jeito nenhum.
Todo intervalo candidato e aparado para nunca invadir [inicio-0.06, fim+0.22] de
nenhuma palavra. A guarda depois da palavra e maior que a de antes, porque o problema
esta sempre na cauda: e ali que a consoante final mora.
Sobrou menos de 0.12s depois de aparar? O corte e recusado, e o motivo entra no
relatorio. Na duvida, mantem.
"""
import subprocess, numpy as np, sys, os, json, tempfile, argparse, re

ap = argparse.ArgumentParser()
ap.add_argument('entrada'); ap.add_argument('saida')
ap.add_argument('--words', required=True, help='json do whisper -ml 1 -oj do MESMO audio')
ap.add_argument('--offset', type=float, default=0.0)
ap.add_argument('--conteudo', default=None, help='json com cortes de conteudo [{ini,fim,...}]')
ap.add_argument('--limiar', type=float, default=-40.0)
ap.add_argument('--min', type=float, default=0.30)
ap.add_argument('--guarda-antes', type=float, default=0.06)
ap.add_argument('--guarda-depois', type=float, default=0.22)
A = ap.parse_args()

# ---------- palavras: as zonas proibidas ----------
d = json.load(open(A.words))
W = []
for s in d['transcription']:
    t = s['text']
    if t.strip() and re.search(r'\w', t):
        W.append((t, s['offsets']['from']/1000.0 - A.offset, s['offsets']['to']/1000.0 - A.offset))
W = [(w, a, b) for w, a, b in W if b >= 0]
palavras = []
for w, a, b in W:
    if palavras and not w.startswith(' '):
        palavras[-1] = (palavras[-1][0] + w.strip(), palavras[-1][1], b)
    else:
        palavras.append((w.strip(), a, b))
proib = [(max(0, a - A.guarda_antes), b + A.guarda_depois) for _, a, b in palavras]
proib.sort()

# ---------- energia: os candidatos ----------
raw = tempfile.mktemp(suffix='.raw')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', A.entrada,
                '-ac', '1', '-ar', '16000', '-f', 's16le', raw], check=True)
a = np.fromfile(raw, dtype=np.int16).astype(np.float32) / 32768
os.unlink(raw)
sr, win = 16000, 400                                   # 25ms
n = len(a) // win
DUR = len(a) / sr
db = 20*np.log10(np.sqrt(np.maximum((a[:n*win].reshape(n, win)**2).mean(1), 1e-12)))
q = db < A.limiar
dd = np.diff(np.concatenate(([0], q.view(np.int8), [0])))
ini = np.where(dd == 1)[0] * (win/sr)
fim = np.where(dd == -1)[0] * (win/sr)

cortes, recusados = [], []
# A ENERGIA define o corte, com guardas curtas. O whisper NAO apara o corte: ele so
# VETA. Motivo (esta em nucleo/corte-fino.md): o whisper estica os timestamps por cima
# da pausa, entao aparar por ele congela o corte. Medido no T1 em 04/08/2026: aparando
# pelo whisper sairam 4,3s de silencio em 11 minutos; vetando, sai o que da para sair.
def cobertura(ca, cb):
    """maior fracao de uma palavra que este corte engoliria"""
    pior = 0.0
    for _, pa, pb in palavras:
        if pb <= ca or pa >= cb:
            continue
        dur = max(1e-6, pb - pa)
        pior = max(pior, (min(cb, pb) - max(ca, pa)) / dur)
    return pior

for a0, b0 in zip(ini, fim):
    if b0 - a0 < A.min:
        continue
    ca, cb = a0 + A.guarda_depois, b0 - A.guarda_antes    # guarda maior na cauda da fala
    if cb - ca < 0.12:
        recusados.append((round(a0, 2), round(b0, 2), 'pausa curta demais depois das guardas'))
        continue
    cob = cobertura(ca, cb)
    if cob >= 0.25:                                       # engoliria a palavra: veta
        recusados.append((round(a0, 2), round(b0, 2), 'cobriria %.0f%% de uma palavra' % (cob*100)))
        continue
    cortes.append((round(ca, 3), round(cb, 3)))

# ---------- cortes de conteudo, aparados pelas mesmas zonas ----------
if A.conteudo:
    for c in json.load(open(A.conteudo)):
        cortes.append((round(c['ini'], 3), round(c['fim'], 3)))

cortes.sort()
juntos = []
for c in cortes:
    if juntos and c[0] <= juntos[-1][1] + 0.02:
        juntos[-1] = (juntos[-1][0], max(juntos[-1][1], c[1]))
    else:
        juntos.append(list(c))
cortes = [tuple(c) for c in juntos]

keeps, cur = [], 0.0
for a0, b0 in cortes:
    if a0 > cur:
        keeps.append((round(cur, 3), round(a0, 3)))
    cur = b0
if cur < DUR:
    keeps.append((round(cur, 3), round(DUR, 3)))
keeps = [(x, y) for x, y in keeps if y - x > 0.08]

rem = sum(b - a for a, b in cortes)
print(f'pausas e trechos cortados: {len(cortes)}   removido: {rem:.1f}s')
print(f'recusados por encostar na fala: {len(recusados)}')
print(f'antes {DUR:.1f}s  ->  depois {DUR-rem:.1f}s  ({(DUR-rem)/60:.1f} min)')

v = ''.join(f'[0:v]trim={x}:{y},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={x}:{y},asetpts=PTS-STARTPTS[a{i}];'
            for i, (x, y) in enumerate(keeps))
cc = ''.join(f'[v{i}][a{i}]' for i in range(len(keeps))) + f'concat=n={len(keeps)}:v=1:a=1[vo][ao]'
f = tempfile.mktemp(suffix='.txt'); open(f, 'w').write(v + cc)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', A.entrada, '-filter_complex_script', f,
                '-map', '[vo]', '-map', '[ao]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '192k', A.saida], check=True)
os.unlink(f)
import json as _j
_j.dump({'cortes': [list(c) for c in cortes], 'removido': rem, 'dur': DUR,
         'recusados': recusados}, open(A.saida + '.plano.json', 'w'))
print('plano do corte gravado em', A.saida + '.plano.json')
print('escrito:', A.saida)
print('PROVA OBRIGATORIA: transcreva o arquivo de saida e compare a sequencia de palavras')
print('com a do original. Palavra que sumiu ou picotada reprova o corte.')
