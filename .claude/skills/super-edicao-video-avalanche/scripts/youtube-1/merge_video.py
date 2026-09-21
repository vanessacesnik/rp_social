#!/usr/bin/env python3
"""
merge_video.py <pasta-do-video> <duracao-do-master> <rotulo-do-capitulo>

Junta os blocos de cena escritos pelos agentes num index.html completo, no padrao
do modelo YouTube 1. Cuida das armadilhas que ja custaram tempo:
  - o esqueleto vem do T1 e carrega o gancho antigo junto: ele e removido
  - nenhum .html solto fica dentro de proj/ (o motor acha duas composicoes e duplica o audio)
  - a duracao do master entra em TODOS os clipes de fundo, inclusive <video> e <audio>
  - o cabecalho da marca fica oculto: nesta geometria ele colide com o beat e a headline
"""
import re, sys, os, glob

PASTA = sys.argv[1]
FIM   = float(sys.argv[2])
ROTULO= sys.argv[3]
ESQ   = os.path.expanduser("~/workspace")

cab = open(f'{ESQ}/esq_cabeca.txt', encoding='utf-8').read()
meio= open(f'{ESQ}/esq_meio.txt',   encoding='utf-8').read()
jsi = open(f'{ESQ}/esq_js_ini.txt', encoding='utf-8').read()
jsf = open(f'{ESQ}/esq_js_fim.txt', encoding='utf-8').read()

# o esqueleto foi tirado do T1 e traz o gancho daquele video no meio: fora
i = cab.find('<div id="cG"')
if i != -1:
    j = cab.find('\n</div>', i)
    cab = cab[:i] + cab[j+len('\n</div>'):]

cenas, js = [], []
for f in sorted(glob.glob(f'{PASTA}/blocos/*.html')):
    t = open(f, encoding='utf-8').read()
    h, j = t.split('<!--JS-->')
    h = h.replace('<!--HTML-->', '').strip()
    js.append(j.strip())
    for m in re.finditer(r'(<div id="c\w+" class="clip[^"]*" data-start="([\d.]+)".*?)(?=\n<div id="c\w+" class="clip|\Z)', h, re.S):
        cenas.append((float(m.group(2)), m.group(1).rstrip()))
cenas.sort()

s = cab + '\n\n'.join(c for _, c in cenas) + '\n\n' + meio + jsi + '\n' + '\n'.join(js) + '\n\n' + jsf

s = re.sub(r'(data-composition-id="main" data-start="0" data-duration=")[\d.]+(")',
           lambda m: f'{m.group(1)}{FIM:.2f}{m.group(2)}', s)
for pat in [r'(id="chrome-fixo" class="clip" data-start="0" data-duration=")[\d.]+(")',
            r'(id="rotulo-capitulo" class="clip capitulo" data-start="0" data-duration=")[\d.]+(")',
            r'(id="video-chefe" class="clip" src="assets/chefe.mp4" data-start="0" data-duration=")[\d.]+(")',
            r'(id="audio-chefe" src="assets/chefe.m4a" data-start="0" data-duration=")[\d.]+(")']:
    s = re.sub(pat, lambda m: f'{m.group(1)}{FIM-0.03:.2f}{m.group(2)}', s)
s = re.sub(r'(class="clip capitulo"[^>]*>)[^<]*(</div>)', rf'\1{ROTULO}\2', s)

s = s.replace('      window.__timelines["main"] = tl;',
 'const cabecalho = ["#chrome-fixo .cab", "#chrome-fixo .regua", "#chrome-fixo .rod", "#rotulo-capitulo"];\n'
 'tl.set(cabecalho, { opacity: 0 }, 0);\n\n'
 '      window.__timelines["main"] = tl;')

open(f'{PASTA}/proj/index.html', 'w', encoding='utf-8').write(s)

# nenhum html solto no proj alem do index
for f in glob.glob(f'{PASTA}/proj/*.html'):
    if os.path.basename(f) != 'index.html':
        os.remove(f); print('removido do proj:', os.path.basename(f))

print(f'{len(cenas)} cenas  ·  fim %.2f  ·  {len(s)} bytes' % max(a for a, _ in cenas))
