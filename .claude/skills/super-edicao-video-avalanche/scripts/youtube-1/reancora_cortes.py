#!/usr/bin/env python3
"""
reancora_cortes.py <pasta> --cortes plano.json --fim <nova_duracao>

Depois de tirar trechos do master (repeticao, divagacao), a apresentacao inteira
precisa andar para tras junto com a fala. Este script aplica a funcao
tempo_antigo -> tempo_novo em TODA a timeline: data-start das cenas, constantes
cNNbase, tempos absolutos nas linhas tl. e nas linhas de continuacao dos contadores.

Cena que ficava DENTRO de um trecho removido e apagada. Cena que so encostava tem
a duracao aparada.
"""
import re, sys, json, argparse

ap = argparse.ArgumentParser()
ap.add_argument('pasta')
ap.add_argument('--cortes', required=True)
ap.add_argument('--fim', type=float, required=True)
A = ap.parse_args()

CORTES = [tuple(c) for c in json.load(open(A.cortes))['cortes']]


def mapa(t):
    """tempo no master antigo -> tempo no master cortado. None se caiu no buraco."""
    desc = 0.0
    for a, b in CORTES:
        if t >= b:
            desc += b - a
        elif t > a:
            return None
        else:
            break
    return t - desc


p = f'{A.pasta}/proj/index.html'
s = open(p, encoding='utf-8').read()

# ---- cenas ----
removidas = []
def cena(m):
    cid, st, du = m.group(1), float(m.group(2)), float(m.group(3))
    a, b = st, st + du
    na, nb = mapa(a), mapa(b)
    if na is None and nb is None:
        removidas.append(cid); return m.group(0)
    if na is None: na = mapa(next(x[1] for x in CORTES if x[0] < a < x[1]))
    if nb is None: nb = mapa(next(x[0] for x in CORTES if x[0] < b < x[1]))
    return m.group(0)[:m.start(2)-m.start(0)] + f'{na:.2f}" data-duration="{max(0.5, nb-na):.2f}"'

s = re.sub(r'<div id="(c\w+)" class="clip[^"]*" data-start="([\d.]+)" data-duration="([\d.]+)"', cena, s)

for cid in removidas:
    i = s.index(f'<div id="{cid}" class="clip'); j = s.index('\n</div>', i) + len('\n</div>')
    s = s[:i] + s[j:]

# ---- constantes base ----
s = re.sub(r'const (c\w+)base = ([\d.]+);',
           lambda m: f'const {m.group(1)}base = {(mapa(float(m.group(2))) or 0):.2f};', s)

# ---- tempos absolutos (linhas tl. e continuacoes) ----
L = s.split('\n')
for i, l in enumerate(L):
    if 'base +' in l:
        continue
    m = re.search(r'(, )(\d+\.\d+)(\);\s*)$', l)
    if m and (l.startswith('tl.') or re.match(r'^\s*\} \},', l)):
        t = mapa(float(m.group(2)))
        if t is not None:
            L[i] = l[:m.start(2)] + f'{t:.2f}' + l[m.end(2):]
s = '\n'.join(L)

for pat, val in [(r'(data-composition-id="main" data-start="0" data-duration=")[\d.]+(")', A.fim),
                 (r'(id="chrome-fixo" class="clip" data-start="0" data-duration=")[\d.]+(")', A.fim-0.03),
                 (r'(id="rotulo-capitulo" class="clip capitulo" data-start="0" data-duration=")[\d.]+(")', A.fim-0.03),
                 (r'(id="video-chefe" class="clip" src="assets/chefe.mp4" data-start="0" data-duration=")[\d.]+(")', A.fim-0.03),
                 (r'(id="audio-chefe" src="assets/chefe.m4a" data-start="0" data-duration=")[\d.]+(")', A.fim-0.03)]:
    s = re.sub(pat, lambda m, v=val: f'{m.group(1)}{v:.2f}{m.group(2)}', s)

open(p, 'w', encoding='utf-8').write(s)
cl = re.findall(r'<div id="(c\w+)" class="clip[^"]*" data-start="([\d.]+)" data-duration="([\d.]+)"', s)
print(f'{len(cl)} cenas  ·  removidas: {removidas or "nenhuma"}  ·  fim %.2f' %
      max(float(a)+float(d) for _, a, d in cl))
sobre = [cl[i][0] for i in range(len(cl)-1)
         if float(cl[i][1])+float(cl[i][2]) > float(cl[i+1][1]) + 0.02]
print('sobreposicao:', sobre or 'nenhuma')
