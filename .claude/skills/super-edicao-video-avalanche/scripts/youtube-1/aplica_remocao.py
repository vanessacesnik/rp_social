#!/usr/bin/env python3
"""
aplica_remocao.py <pasta> · reancora o mapa quando o diretor declarou `remover` em
tempo de MASTER sem ter aplicado aos tempos das cenas.

O diretor mede tudo no corte cheio e depois aponta a tela morta. Se ninguém aplicar,
as cenas ficam deslocadas pela soma do que foi removido (no vídeo 07 seriam 40,59s).

O que faz:
  1. converte `remover` de tempo de master para tempo de CORTE (subtrai a duração do
     gancho), que é o que o `prepara.py` espera;
  2. desloca todo início de cena pelo que foi removido antes dele;
  3. apaga cena que ficou inteira dentro de um trecho removido e apara a que só encostou;
  4. reancora as `batidas` de faixa, quando o diretor as declarou;
  5. reescreve o mapa e guarda o original ao lado.

Rode ANTES do `prepara.py`.
"""
import json, os, sys, shutil

W = os.path.abspath(sys.argv[1])
mapa = json.load(open(f'{W}/mapa.json'))
gan = json.load(open(f'{W}/gancho.json'))
rem_master = mapa.get('remover') or []
if not rem_master:
    sys.exit('nada a remover, mapa intocado')

DG = gan['fim'] - gan['ini']
shutil.copy(f'{W}/mapa.json', f'{W}/mapa.antes-remocao.json')

# ---- 1. master -> corte, para o prepara.py ----
rem_corte = [[round(a - DG, 2), round(b - DG, 2)] for a, b in rem_master]
if any(a < 0 for a, _ in rem_corte):
    sys.exit(f'ERRO: trecho a remover cai dentro do gancho: {rem_corte}')

# o gancho tambem vive no corte cheio; se ele estiver depois de um trecho removido,
# o prepara.py ja mapeia sozinho. Aqui so avisamos se ele CAIR dentro de um.
for a, b in rem_corte:
    if a < gan['ini'] < b or a < gan['fim'] < b:
        sys.exit(f'ERRO: o gancho ({gan["ini"]}..{gan["fim"]}) cai dentro de {a}..{b}')


def novo(t):
    """tempo de master antigo -> tempo de master depois da remocao. None se caiu no buraco."""
    d = 0.0
    for a, b in rem_master:
        if t >= b:
            d += b - a
        elif t > a:
            return None
    return round(t - d, 2)


cenas, apagadas, aparadas = [], [], []
for c in mapa['cenas']:
    a, b = c['ini'], c['ini'] + c['dur']
    na, nb = novo(a), novo(b)
    if na is None and nb is None:
        apagadas.append(c['id']); continue
    if na is None:                       # comecava dentro do buraco
        na = novo(next(y for x, y in rem_master if x < a < y)); aparadas.append(c['id'])
    if nb is None:                       # terminava dentro do buraco
        nb = novo(next(x for x, y in rem_master if x < b < y)); aparadas.append(c['id'])
    c['ini'], c['dur'] = round(na, 2), round(max(0.5, nb - na), 2)
    if 'batidas' in c:
        # a batida pode vir como numero solto ou como par [instante, rotulo]
        novas = []
        for x in c['batidas']:
            if isinstance(x, (int, float)):
                t = novo(x)
                if t is not None:
                    novas.append(t)
            elif isinstance(x, dict):
                k = next((k for k in ('t', 'instante', 'ini', 'master') if k in x), None)
                t = novo(x[k]) if k else None
                if t is not None:
                    x[k] = t; novas.append(x)
            elif isinstance(x, (list, tuple)) and x and isinstance(x[0], (int, float)):
                t = novo(x[0])
                if t is not None:
                    novas.append([t] + list(x[1:]))
            else:
                novas.append(x)
        c['batidas'] = novas
    cenas.append(c)

# ---- fecha buraco e sobreposicao que a remocao possa ter aberto ----
cenas.sort(key=lambda x: x['ini'])
for i in range(len(cenas) - 1):
    cenas[i]['dur'] = round(cenas[i + 1]['ini'] - cenas[i]['ini'], 2)

mapa['cenas'] = cenas
mapa['remover'] = rem_corte
mapa['remover_unidade'] = 'corte'
json.dump(mapa, open(f'{W}/mapa.json', 'w'), ensure_ascii=False, indent=1)

fim = cenas[-1]['ini'] + cenas[-1]['dur']
print(f'removidos {sum(b-a for a,b in rem_master):.2f}s em {len(rem_master)} trecho(s)')
print(f'remover convertido para tempo de corte: {rem_corte}')
print(f'cenas: {len(cenas)}  apagadas: {apagadas or "nenhuma"}  aparadas: {sorted(set(aparadas)) or "nenhuma"}')
print(f'novo fim do master: {fim:.2f}')
