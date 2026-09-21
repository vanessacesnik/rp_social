#!/usr/bin/env python3
"""
infografico_cheio.py <dir> · faz o infográfico OCUPAR O PAINEL, em vez de ficar espremido.

POR QUE (05/08/2026). O Chefe mandou um print do CTA 1 e a lição foi direta: "seria muito
melhor o infográfico estar maior, ocupando mais espaço na tela, do que ter lá em cima aquele
Avalanche IA aplicada a negócios e a equipe da Naia. Esse título não é necessário, porque no
próprio infográfico já tem a equipe que trabalha por você".

Ele está certo por dois motivos. O infográfico é a peça mais cara da cena e estava ocupando
1166x574 de um painel de 1252x1016, pouco mais da metade. E o rótulo em cima REPETIA, em corpo
pequeno e ilegível, o título que a arte já carrega em corpo grande.

A REGRA, que vale para todo o modelo daqui em diante: numa cena de infográfico a arte vai de
ponta a ponta do painel, o cabeçalho da marca e o rótulo de capítulo SOMEM, e a única coisa que
divide a tela com ela é a faixa de dados do rodapé, que não é repetição, é a narração viva do
que ele está falando naquele segundo.

O que este programa faz, direto nos blocos já escritos:
  1. troca a classe da arte por `img-area cheia`, que ocupa os 1252 de largura e centraliza
     verticalmente no espaço acima da faixa;
  2. apaga da cena o carimbo, a headline e o subtítulo, junto com os tweens deles, porque a
     arte já é o título;
  3. no CTA, onde o cabeçalho é permanente, apaga a marca e o rótulo durante a cena e devolve
     os dois depois.
"""
import json, os, re, shutil, sys

W = os.path.abspath(sys.argv[1])
mapa = json.load(open(f'{W}/mapa.json', encoding='utf-8'))
ALVO = {c['id']: c for c in mapa['cenas'] if c.get('tipo') in ('infografico', 'imagem')}
if not ALVO:
    print('nenhuma cena de arte neste projeto')
    raise SystemExit(0)


def funde_janelas(cenas, tolerancia=0.02):
    """Une cenas de arte contiguas para a marca nao reaparecer entre elas."""
    janelas = []
    for c in sorted(cenas, key=lambda x: (x['ini'], x['id'])):
        ini = float(c['ini'])
        fim = ini + float(c['dur'])
        if janelas and ini <= janelas[-1][1] + tolerancia:
            janelas[-1][1] = max(janelas[-1][1], fim)
            janelas[-1][2].append(c['id'])
        else:
            janelas.append([ini, fim, [c['id']]])
    return janelas


JANELAS_ARTE = funde_janelas(ALVO.values())

CSS = """
/* ---------- infografico de ponta a ponta (05/08/2026) ----------
   O painel tem 1252x1016 e a faixa de dados fecha em 1002 comecando em 850. Sobram 850px de
   altura para a arte. A arte e 1252x690, entao ela cabe na largura INTEIRA do painel e fica
   centrada na vertical: (850-690)/2 = 80. Sem margem lateral, sem moldura, sem titulo em cima.
   `contain` continua, porque infografico cortado reprova a entrega. */
.img-area.cheia { left: 0; top: 80px; width: 1252px; height: 690px; background: #0F172A;
  border: 0; border-radius: 0; }
.img-area.cheia img { width: 1252px; height: 690px; object-fit: contain; display: block; }
"""

# ---------- 1. os blocos ----------
tot_art, tot_lixo, tot_ev = 0, 0, 0
for f in sorted(os.listdir(f'{W}/blocos')):
    if not f.endswith('.html'):
        continue
    p = f'{W}/blocos/{f}'
    if not os.path.exists(p + '.antescheio'):
        shutil.copy(p, p + '.antescheio')
    s = open(p, encoding='utf-8').read()
    mortos = []

    for cid in ALVO:
        # a arte ocupa o painel
        # Os agentes nomearam a div de arte de jeitos diferentes e alguns nem deram ID a ela.
        # O casamento parte do clip da cena e troca a PRIMEIRA `img-area` dentro dele.
        s, n = re.subn(
            r'(<div id="%s" class="clip livre"[^>]*>.*?<div(?: id="[^"]+")? class="img-area)[^"]*(")' % cid,
            lambda mo: mo.group(1) + ' cheia' + mo.group(2), s, count=1, flags=re.S)
        tot_art += n
        # carimbo, headline e subtitulo saem da cena: a arte ja e o titulo
        for suf in ('beat', 'hl', 'tit', 'sub'):
            alvo = f'{cid}-{suf}'
            novo, k = re.subn(r'\n\s*<div id="%s"[^>]*>.*?</div>\s*(?=\n)' % alvo, '', s, flags=re.S)
            if k:
                s = novo
                mortos.append(alvo)
                tot_lixo += k
        # carimbo sem id proprio (o `.beat` solto que alguns blocos escreveram)
        s = re.sub(r'(<div id="%s" class="clip livre"[^>]*>)\s*<div class="beat">.*?</div>' % cid,
                   r'\1', s, flags=re.S)

    # os tweens dos elementos apagados iriam para o vazio e o motor reclama
    linhas = []
    for l in s.split('\n'):
        seletor_beat_morto = any(f'#{cid} .beat' in l for cid in ALVO)
        if seletor_beat_morto or any(f'#{m}"' in l or f'#{m} ' in l or f'"{m}"' in l for m in mortos):
            tot_ev += 1
            continue
        linhas.append(l)
    s = '\n'.join(linhas)
    open(p, 'w', encoding='utf-8').write(s)

# ---------- 2. o CSS ----------
esq = f'{W}/esqueleto.html'
s = open(esq, encoding='utf-8').read()
if '.img-area.cheia' not in s:
    s = s.replace('</style>', CSS + '    </style>', 1)

# Uma nova execucao substitui o bloco gerado anteriormente em vez de duplicar tweens.
s = re.sub(
    r'\n// a marca sai enquanto o infografico ocupa o painel\n.*?(?=\n\s*window\.__timelines\["main"\] = tl;)',
    '\n', s, flags=re.S)

# ---------- 3. no CTA o cabecalho e permanente, entao ele sai durante a cena ----------
if 'RECADO' in s or os.path.basename(W).startswith('cta'):
    ev = []
    for a, b, ids in JANELAS_ARTE:
        # A MARCA sai por opacidade, e nao ha ninguem disputando esse alvo. O apagar fecha
        # 0,30s ANTES do corte porque o lint le qualquer `opacity: 0` que termina num limite
        # de clip como saida de cena e exige um desligamento explicito, que aqui apagaria a
        # marca de vez.
        if len(ids) > 1:
            ev.append(f'// cenas de arte contiguas {", ".join(ids)}: uma unica janela')
        ev.append(f'tl.to(cabecalho, {{ opacity: 0, duration: 0.30, ease: "quart.in" }}, {a-0.60:.2f});')
        ev.append(f'tl.to(cabecalho, {{ opacity: 1, duration: 0.40, ease: "quart.out" }}, {b+0.20:.2f});')
    marca = '      window.__timelines["main"] = tl;'
    s = s.replace(marca, '// a marca sai enquanto o infografico ocupa o painel\n'
                  + '\n'.join(ev) + '\n\n' + marca, 1)
    print(f'marca recolhida em {len(ALVO)} cena(s) de arte, {len(JANELAS_ARTE)} janela(s)')

    # O ROTULO DE CAPITULO E OUTRA HISTORIA. O bloco reacende ele a cada troca de cena, com
    # tween proprio, e ganha de qualquer fade meu porque vem depois na timeline. Brigar por
    # opacidade nao resolve. Entao o texto dele VIRA VAZIO na cena de arte: sem texto nao ha
    # o que aparecer, independente de opacidade, e some o defeito que o Chefe apontou de o
    # rotulo repetir em corpo pequeno o titulo que a arte ja carrega em corpo grande.
    for f in sorted(os.listdir(f'{W}/blocos')):
        if not f.endswith('.html'):
            continue
        q = f'{W}/blocos/{f}'
        t = open(q, encoding='utf-8').read()
        n = 0
        for cid, c in sorted(ALVO.items()):
            ini = c['ini']
            def _vazia(mo, _ini=ini):
                # so a troca que cai na janela desta cena de arte
                inst = float(mo.group(2))
                return (mo.group(0).replace(mo.group(1), '""')
                        if _ini - 1.2 <= inst <= _ini + 0.2 else mo.group(0))
            t, k = re.subn(r'trocaD\("cap-txt", ("[^"]*")\)[^;]*?, ([\d.]+)\);', _vazia, t)
            n += k
        open(q, 'w', encoding='utf-8').write(t)
    print('rotulo de capitulo esvaziado nas cenas de arte')

open(esq, 'w', encoding='utf-8').write(s)
print(f'{len(ALVO)} cena(s) de arte  ·  {tot_art} arte(s) em tela cheia  ·  '
      f'{tot_lixo} titulo(s) repetido(s) apagado(s)  ·  {tot_ev} evento(s) orfao(s) removido(s)')
