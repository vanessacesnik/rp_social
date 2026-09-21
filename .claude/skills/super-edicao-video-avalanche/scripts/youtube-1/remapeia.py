#!/usr/bin/env python3
"""
remapeia.py <dir> · leva mapa.json e blocos/*.html do master ANTIGO para o master NOVO.

Encostar cada borda de corte no silêncio (a trava de 05/08/2026, que acabou com as 36
palavras partidas) muda a duração do gancho e a de cada trecho removido. O conteúdo é o
mesmo, mas TODO instante anda alguns centésimos, e uma cena que anda 0,2s deixa de bater
com a fala que ela ilustra.

Este programa não adivinha: o `prepara.py` grava em `remap.json` o que foi pedido e o que
foi aplicado, então a conversão é exata e monótona. Um tempo do master antigo vira tempo
do master novo em três passos: volta para o tempo do arquivo bruto, desconta os trechos
removidos NOVOS, e soma o gancho NOVO.

Reescreve `mapa.json` (ini de cada cena) e todo `blocos/*.html` (data-start e o segundo
argumento de cada `tl.to`, `tl.fromTo` e `tl.set`). Guarda `.antes` de cada arquivo.
"""
import json, os, re, shutil, sys

W = os.path.abspath(sys.argv[1])
R = json.load(open(f'{W}/remap.json'))

REM_A = [tuple(x) for x in R['remover_pedido']]
REM_N = [tuple(x) for x in R['remover_aplicado']]
GI_A, GF_A = R['gancho_pedido']
DG_N = R['gancho_dur']
DG_A = GF_A - GI_A


def limpo(t, rem):
    """tempo do bruto -> tempo do arquivo sem os trechos removidos"""
    d = 0.0
    for a, b in rem:
        if t >= b:
            d += b - a
        elif t > a:
            d += t - a
    return t - d


def bruto(tc, rem):
    """inverso de `limpo`, monotono"""
    t = tc
    for a, b in rem:
        if limpo(a, rem) <= tc + 1e-9:
            t += b - a
    return t


def converte(T):
    """tempo no master ANTIGO -> tempo no master NOVO"""
    if T < DG_A:                                  # dentro do gancho
        return T * (DG_N / DG_A) if DG_A > 0 else T
    tc_a = T - DG_A                               # tempo no corte limpo antigo
    tb = bruto(tc_a, REM_A)                       # tempo no bruto
    return DG_N + limpo(tb, REM_N)                # tempo no master novo


# ---------- mapa ----------
p = f'{W}/mapa.json'
shutil.copy(p, p + '.antes')
m = json.load(open(p))
mov = []
for i, c in enumerate(m['cenas']):
    a = c['ini']
    b = converte(a)
    fim = converte(c['ini'] + c['dur'])
    if abs(b - a) > 0.005 or abs((fim - b) - c['dur']) > 0.005:
        mov.append((c['id'], round(b - a, 3)))
    c['ini'] = round(b, 2)
    c['dur'] = round(fim - b, 2)
json.dump(m, open(p, 'w'), ensure_ascii=False, indent=1)
print(f'mapa: {len(m["cenas"])} cenas, {len(mov)} deslocadas  '
      f'{"  ".join(f"{i}{d:+.2f}" for i, d in mov[:10])}')

# ---------- blocos ----------
RX_START = re.compile(r'(data-start=")([\d.]+)(")')
RX_DUR = re.compile(r'(data-duration=")([\d.]+)(")')
RX_EV = re.compile(r'(\}\s*,\s*)(\d+\.\d+)(\s*\)\s*;)')
tot = 0
for f in sorted(os.listdir(f'{W}/blocos')):
    if not f.endswith('.html'):
        continue
    q = f'{W}/blocos/{f}'
    shutil.copy(q, q + '.antes')
    s = open(q, encoding='utf-8').read()

    # data-start e data-duration andam juntos: o par vai no MESMO passe, porque a duracao
    # nova e a diferenca entre o fim convertido e o inicio convertido, nao a duracao antiga.
    def _par(mo):
        # grupos: 1 data-start=" · 2 numero · 3 " · 4 ' data-duration="' · 5 numero · 6 "
        ini, du = float(mo.group(2)), float(mo.group(5))
        ni, nf = converte(ini), converte(ini + du)
        return f'{mo.group(1)}{ni:.2f}{mo.group(3)}{mo.group(4)}{nf-ni:.2f}{mo.group(6)}'
    s, n1 = re.subn(r'(data-start=")([\d.]+)(")(\s+data-duration=")([\d.]+)(")', _par, s)
    s, n2 = RX_EV.subn(lambda mo: f'{mo.group(1)}{converte(float(mo.group(2))):.2f}{mo.group(3)}', s)
    open(q, 'w', encoding='utf-8').write(s)
    tot += n2
    print(f'   {f}: {n1} clip(s), {n2} evento(s) remapeados')
print(f'blocos: {tot} eventos convertidos  ·  gancho {DG_A:.2f} -> {DG_N:.2f}')
