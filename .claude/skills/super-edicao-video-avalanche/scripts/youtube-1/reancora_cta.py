#!/usr/bin/env python3
"""
reancora_cta.py legenda.txt <entrada_s> <dur_cta_s> [--rotulo "..."]

Conserta os capítulos da legenda depois que o CTA entrou no meio do vídeo.

Um CTA de 78 segundos empurra TODO capítulo que vem depois dele. Sem isso a barra do
YouTube fica certa na primeira metade e errada por mais de um minuto na segunda, que é
pior que não ter capítulo nenhum: o espectador clica e cai no lugar errado.

O que faz, nesta ordem:
  1. lê os capítulos do bloco publicável (as linhas `M:SS Texto` e `H:MM:SS Texto`);
  2. soma a duração do CTA em todo capítulo que começa em ou depois da entrada;
  3. insere um capítulo próprio no instante da entrada, para o recado ter nome na barra
     e o espectador saber que pode pular;
  4. reescreve o contador de caracteres do cabeçalho, que é conferido byte a byte.

Não encosta em título, descrição, links, hashtags nem no estudo de SEO.
"""
import argparse, re, sys

ap = argparse.ArgumentParser()
ap.add_argument('legenda'); ap.add_argument('entrada', type=float); ap.add_argument('dur', type=float)
ap.add_argument('--rotulo', default='Um recado rápido (pode pular)')
A = ap.parse_args()

s = open(A.legenda, encoding='utf-8').read()
linhas = s.split('\n')
RX = re.compile(r'^((?:\d+:)?\d{1,2}:\d{2}) (.+)$')


def para_s(t):
    p = [int(x) for x in t.split(':')]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


def para_t(v):
    v = int(round(v))
    h, r = divmod(v, 3600)
    m, sg = divmod(r, 60)
    return f'{h}:{m:02d}:{sg:02d}' if h else f'{m}:{sg:02d}'


idx = [i for i, l in enumerate(linhas) if RX.match(l)]
if not idx:
    # Os quatro primeiros videos da serie sairam sem capitulo. Nao ter capitulo nao e
    # defeito a consertar aqui, entao o programa avisa e sai limpo em vez de falhar.
    print('sem capitulos nesta legenda, nada a reancorar')
    raise SystemExit(0)
i0, i1 = idx[0], idx[-1]
if idx != list(range(i0, i1 + 1)):
    sys.exit('ERRO: os capitulos nao estao em bloco continuo')

caps = [(para_s(RX.match(linhas[i]).group(1)), RX.match(linhas[i]).group(2)) for i in idx]
novos = [(t + A.dur if t >= A.entrada - 0.5 else t, x) for t, x in caps]
novos.append((A.entrada, A.rotulo))
novos.sort()

# o YouTube exige 10s entre capitulos: se o CTA nasceu colado no seguinte, empurra o
# proprio CTA para tras, nunca o capitulo de conteudo, que esta ancorado numa fala.
for i in range(len(novos) - 1):
    if novos[i + 1][0] - novos[i][0] < 10:
        if novos[i][1] == A.rotulo:
            novos[i] = (novos[i + 1][0] - 10, novos[i][1])
        elif novos[i + 1][1] == A.rotulo:
            novos[i + 1] = (novos[i][0] + 10, novos[i + 1][1])
novos.sort()

linhas[i0:i1 + 1] = [f'{para_t(t)} {x}' for t, x in novos]
s2 = '\n'.join(linhas)

# contador do cabecalho: o numero declarado e o len do texto depois da marca
# O bloco publicavel vive ENTRE a regua que segue a marca "COLE DAQUI" e a regua que
# antecede "FIM DO QUE VAI PARA O YOUTUBE". Contar ate o fim do arquivo somava o estudo
# de SEO e as tags, e o contador saia mil caracteres acima do real.
m = re.search(r'(COLE DAQUI PARA BAIXO NO YOUTUBE\s+·\s+)(\d+)( de 5000 caracteres)', s2)
if m:
    L2 = s2.split('\n')
    ini = next(i for i, l in enumerate(L2) if 'COLE DAQUI PARA BAIXO' in l)
    reg = next(i for i in range(ini + 1, len(L2)) if set(L2[i].strip()) == {'='})
    fim = next(i for i in range(reg + 1, len(L2))
               if set(L2[i].strip()) == {'='} and 'FIM DO QUE VAI PARA O YOUTUBE' in L2[i + 1])
    corpo = '\n'.join(L2[reg + 1:fim]).strip('\n')
    s2 = s2.replace(m.group(0), f'{m.group(1)}{len(corpo)}{m.group(3)}')
    if len(corpo) > 5000:
        print(f'   ! ATENCAO: o bloco publicavel ficou com {len(corpo)} caracteres, '
              f'{len(corpo)-5000} acima do limite do YouTube')

open(A.legenda, 'w', encoding='utf-8').write(s2)
desl = sum(1 for t, _ in caps if t >= A.entrada - 0.5)
print(f'{len(caps)} capitulos  ·  {desl} deslocados em +{A.dur:.0f}s  ·  1 capitulo de CTA '
      f'em {para_t(A.entrada)}  ·  bloco com {len(corpo) if m else "?"} caracteres')
