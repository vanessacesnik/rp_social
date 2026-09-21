#!/usr/bin/env python3
"""
mapa_corte.py video.mp4 palavras.json saida.txt [--cauda 10]

Gera o MATERIAL DE ANÁLISE que o agente de limpeza lê para propor cortes de conteúdo.

Não é a transcrição crua: é a transcrição com três coisas que a transcrição não tem e
que são justamente o que denuncia trecho descartável.

1. PAUSA MARCADA. Toda pausa de 0,6s ou mais aparece como uma linha própria, com a
   duração. Pausa longa no meio de uma frase é assinatura de duas coisas: ele
   procurando algo na tela, ou ele PARADO esperando (áudio de outra pessoa vazando na
   chamada, ele congelado até mutar o invasor). O agente não enxerga isso na
   transcrição limpa, e é o defeito que o Chefe mais sente assistindo.

2. NÍVEL DE VOZ POR FALA. A voz dele fica numa faixa; quem entra pela chamada entra
   mais baixo e mais abafado. A coluna `dB` deixa o intruso visível: uma frase 8 a 15
   decibéis abaixo da vizinhança quase sempre é outra pessoa, não ele.

3. TEMPO ABSOLUTO EM CADA LINHA, para o corte proposto poder ser aplicado sem
   adivinhação.

O agente devolve um JSON com ini, fim, tipo e texto de cada trecho a remover, e o
`corta_fino.py` aplica encostando cada borda no silêncio mais próximo.
"""
import argparse, json, os, re, subprocess, tempfile
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('video'); ap.add_argument('words'); ap.add_argument('saida')
ap.add_argument('--cauda', type=float, default=10.0)
ap.add_argument('--pausa', type=float, default=0.6)
A = ap.parse_args()

raw = tempfile.mktemp(suffix='.raw')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', A.video,
                '-ac', '1', '-ar', '16000', '-f', 's16le', raw], check=True)
a = np.fromfile(raw, dtype=np.int16).astype(np.float32) / 32768
os.unlink(raw)
HOP = 0.010
win = int(16000 * HOP)
n = len(a) // win
DUR = len(a) / 16000
db = 20 * np.log10(np.sqrt(np.maximum((a[:n * win].reshape(n, win) ** 2).mean(1), 1e-12)))

d = json.load(open(A.words))
brutas = [(s['text'], s['offsets']['from'] / 1000, s['offsets']['to'] / 1000)
          for s in d['transcription'] if s['text'].strip() and re.search(r'\w', s['text'])]
pal = []
for w, x, y in brutas:
    if pal and not w.startswith(' '):
        pal[-1] = (pal[-1][0] + w.strip(), pal[-1][1], y)
    else:
        pal.append((w.strip(), x, y))

# agrupa em falas, quebrando na pausa
falas, cur, ini = [], [], pal[0][1]
for i, (w, x, y) in enumerate(pal):
    cur.append(w)
    prox = pal[i + 1][1] if i + 1 < len(pal) else DUR
    if prox - y >= A.pausa or len(cur) >= 26:
        falas.append((ini, y, ' '.join(cur), prox - y))
        cur = []
        ini = prox
if cur:
    falas.append((ini, pal[-1][2], ' '.join(cur), 0))


def nivel(x, y):
    i0, i1 = int(x / HOP), min(int(y / HOP), n - 1)
    seg = db[i0:i1 + 1]
    seg = seg[seg > -45]
    return float(np.median(seg)) if len(seg) else -99.0


niveis = [nivel(x, y) for x, y, _, _ in falas]
mediana = float(np.median([v for v in niveis if v > -60]))

L = [f'# MAPA DE CORTE  ·  {os.path.basename(A.video)}  ·  {DUR:.1f}s '
     f'(os ultimos {A.cauda:.0f}s sao a arte de encerramento e NAO se corta)',
     f'# nivel mediano da voz dele: {mediana:.1f} dB. Fala muito abaixo disso costuma ser',
     '# outra pessoa entrando na chamada.',
     '# [tempo_ini - tempo_fim] (dB, +- em relacao a mediana) texto',
     '']
for (x, y, txt, gap), v in zip(falas, niveis):
    if x >= DUR - A.cauda:
        break
    delta = v - mediana
    marca = '  <<< VOZ BAIXA' if delta < -7 else ''
    L.append(f'[{x:7.2f} - {y:7.2f}] ({v:5.1f} dB, {delta:+5.1f}){marca}  {txt}')
    if gap >= A.pausa and y + gap < DUR - A.cauda:
        L.append(f'          ... PAUSA DE {gap:.2f}s ...')
open(A.saida, 'w', encoding='utf-8').write('\n'.join(L))
print(f'{len(falas)} falas  ·  nivel mediano {mediana:.1f} dB  ·  escrito em {A.saida}')
print(f'falas mais de 7 dB abaixo da mediana: {sum(1 for v in niveis if v - mediana < -7)}')
print(f'pausas de {A.pausa}s ou mais: {sum(1 for _,_,_,g in falas if g >= A.pausa)}')
