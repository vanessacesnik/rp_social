#!/usr/bin/env python3
"""
build.py · monta proj/index.html a partir de esqueleto.html + blocos/*.html

Determinístico e idempotente: pode rodar quantas vezes quiser, sempre a partir das
fontes. Foi escrito porque um agente reescreveu o bloco C depois do merge manual e
todos os consertos aplicados direto no index teriam que ser recolados na mão.

O que ele resolve, cada um por causa de um defeito real:

1. ORDEM. As cenas dos blocos entram ordenadas por tempo, não por nome de arquivo.
2. WRAPPER DE SAÍDA. Fade de saída aplicado no próprio elemento de cena briga com o
   motor, que já gerencia a visibilidade do clip. O `check` reprova. Cada cena com
   saída ganha um invólucro interno, o tween é redirecionado para ele, e entra um
   desligamento explícito no fim exato da cena.
3. BURACO DE PAINEL PRETO. Se o fade termina antes do fim da cena, sobra painel vazio.
   Toda saída é atrasada para terminar no instante do corte.
4. TRANSBORDO DE FOTO. Zoom lento em foto com `cover` transborda de propósito, então
   a foto é marcada como transbordo intencional para não poluir o relatório.
5. AUDITORIA. No fim confere saldo de div, profundidade no ponto da coluna (o erro que
   fez a gravação sumir do vídeo inteiro no T2 e no T3), sobreposição e travessão.
"""
import re, os, sys, json

W = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
# cenas de FOTO saem do mapa.json (zoom com cover transborda de proposito)
FOTOS = [c['id'] for c in json.load(open(f'{W}/mapa.json'))['cenas'] if c.get('tipo') == 'imagem'] \
        if os.path.exists(f'{W}/mapa.json') else []
FOLGA_MAX = 0.05                        # buraco tolerado entre o fim do fade e o fim da cena

esq = open(f'{W}/esqueleto.html', encoding='utf-8').read()

# ---------- 1. junta os blocos, ordenando por tempo ----------
cenas, js = [], []
for f in sorted(os.listdir(f'{W}/blocos')):
    if not f.endswith('.html'):
        continue
    s = open(f'{W}/blocos/{f}', encoding='utf-8').read()
    if '<!--JS-->' not in s:
        sys.exit(f'ERRO: {f} sem a marca <!--JS-->')
    h, j = s.split('<!--JS-->')
    h = h.replace('<!--HTML-->', '').strip()
    for m in re.finditer(r'(<div id="(c\d+)" class="clip livre" data-start="([\d.]+)".*?)'
                         r'(?=\n<div id="c\d+" class="clip livre"|\Z)', h, re.S):
        cenas.append((float(m.group(3)), m.group(2), m.group(1).rstrip()))
    js.append(f'/* ==== {f} ==== */\n' + j.strip())
cenas.sort()
s = esq.replace('<!--CENAS-->', '\n\n'.join(c[2] for c in cenas)) \
       .replace('<!--JS-->', '\n\n'.join(js))

# ---------- 1b. o CSS de cada bloco ----------
# 05/08/2026. Com a biblioteca de componentes cada bloco traz classes proprias (fluxo,
# contador, barras, linha do tempo). Elas moram em `blocos/<LETRA>.css`, com prefixo por
# bloco para dois blocos nao colidirem, e entram no fim do <style> do esqueleto.
extra = []
for f in sorted(os.listdir(f'{W}/blocos')):
    if f.endswith('.css'):
        extra.append(f'/* ==== {f} ==== */\n' + open(f'{W}/blocos/{f}', encoding='utf-8').read().strip())
if extra:
    if '</style>' not in s:
        sys.exit('ERRO: o esqueleto nao tem </style> para receber o CSS dos blocos')
    s = s.replace('</style>', '\n' + '\n\n'.join(extra) + '\n    </style>', 1)
    print(f'css dos blocos: {len(extra)} arquivo(s), {sum(len(e) for e in extra)} caracteres')

clips = {c: (float(a), float(a) + float(d)) for c, a, d in
         re.findall(r'<div id="(c\w+)" class="clip livre" data-start="([\d.]+)" data-duration="([\d.]+)"', s)}

# ---------- 2. wrapper interno para as saidas ----------
alvos = sorted(set(re.findall(r'tl\.to\(\s*"#(c\w+)"\s*,\s*\{[^}]*opacity:\s*0', s)))
feitos = []
for cid in alvos:
    if cid not in clips:
        continue
    m = re.search(r'(<div id="%s" class="clip livre"[^>]*>)(.*?)(\n</div>)' % cid, s, re.S)
    if not m:
        sys.exit(f'ERRO: nao achei o corpo da cena {cid}')
    s = (s[:m.start()]
         + f'{m.group(1)}\n  <div id="{cid}-in" style="position:absolute; left:0; top:0; '
           f'width:1252px; height:1016px">{m.group(2)}\n  </div>{m.group(3)}'
         + s[m.end():])
    # so o alvo exato "#cNN", nunca "#cNN .algo" nem "#cNN-x"
    s = re.sub(r'(tl\.(?:to|fromTo|set)\(\s*)"#%s"(\s*,)' % cid, r'\1"#%s-in"\2' % cid, s)
    feitos.append(cid)

# ---------- 3. saida tem que TERMINAR no fim da cena ----------
atrasos = []
def atrasa(m):
    cid, corpo, dur, t = m.group(1), m.group(2), float(m.group(3)), float(m.group(4))
    fim = clips[cid][1]
    folga = fim - (t + dur)
    if folga <= FOLGA_MAX:
        return m.group(0)
    novo = round(fim - dur, 2)
    atrasos.append((cid, t, novo, round(folga, 2)))
    return f'tl.to("#{cid}-in", {{{corpo}}}, {novo:.2f})'
s = re.sub(r'tl\.to\(\s*"#(c\w+)-in"\s*,\s*\{([^}]*opacity:\s*0[^}]*duration:\s*([\d.]+)[^}]*)\}\s*,\s*([\d.]+)\)',
           atrasa, s)

# ---------- 4. desligamento explicito no fim exato ----------
kill = '\n'.join('tl.set("#%s-in", { opacity: 0 }, %.2f);' % (c, clips[c][1]) for c in feitos)
s = s.replace('      window.__timelines["main"] = tl;',
              '// desligamento das saidas: o motor gerencia o clip, o fade mora no wrapper\n'
              + kill + '\n\n      window.__timelines["main"] = tl;')

# ---------- 5. foto transborda de proposito ----------
for cid in FOTOS:
    s = re.sub(r'(<img id="%s-img")(?! data-layout-allow-overflow)' % cid,
               r'\1 data-layout-allow-overflow', s, count=1)

open(f'{W}/proj/index.html', 'w', encoding='utf-8').write(s)

# ---------- 6. auditoria ----------
corpo = s[s.index('<body>'):]
saldo = corpo.count('<div') - corpo.count('</div>')
prof = 0
for m in re.finditer(r'<div\b|</div>', s[s.index('<body>'):s.index('<div id="coluna">')]):
    prof += 1 if m.group(0) == '<div' else -1
cl = re.findall(r'<div id="(c\w+)" class="clip[^"]*" data-start="([\d.]+)" data-duration="([\d.]+)"', s)
sobre = [cl[i][0] for i in range(len(cl) - 1)
         if float(cl[i][1]) + float(cl[i][2]) > float(cl[i + 1][1]) + 0.02]

print(f'cenas: {len(cenas)}   ordem: {" ".join(c[1] for c in cenas)}')
print(f'wrappers: {len(feitos)}   saidas atrasadas: {len(atrasos)}')
for c, a, b, g in atrasos:
    print(f'   {c}: {a:.2f} -> {b:.2f}  (fechava {g:.2f}s cedo demais)')
print(f'saldo de div: {saldo:+d}   profundidade na coluna: {prof} (tem que ser 1)')
print(f'clips: {len(cl)}   fim: {max(float(a)+float(d) for _,a,d in cl):.2f}')
orfas = [l for l in s[s.index('</html>'):].split(chr(10)) if l.strip().startswith('tl.')] if '</html>' in s else []
print(f'sobreposicao: {sobre or "nenhuma"}   travessao: {s.count(chr(8212))}   eventos fora do script: {len(orfas)}')
if saldo or prof != 1 or sobre or s.count(chr(8212)) or orfas:
    sys.exit('AUDITORIA REPROVOU')
print('build ok')
