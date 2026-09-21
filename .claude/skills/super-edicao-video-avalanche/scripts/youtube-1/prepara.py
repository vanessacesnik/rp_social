#!/usr/bin/env python3
"""
prepara.py <NN> <A|B> · monta master, esqueleto e assets de um vídeo do lote.

Lê `gancho.json` e `mapa.json` (produzidos pelo diretor) e deixa o projeto pronto para
os agentes de bloco. Faz, nesta ordem:

1. remove do corte os trechos de tela morta pedidos em `mapa.json.remover`;
2. recorta o gancho e cola na frente, gerando o master;
3. separa vídeo e áudio para os assets do HyperFrames;
4. escreve o esqueleto com a paleta escura e a montagem certa (A à direita, B à esquerda).

Sempre confere a duração dos QUATRO elementos de tempo (root, chrome, vídeo, áudio):
esquecer um deles apagou a coluna da gravação no T1 e comeu treze segundos de fala.
"""
import json, os, re, subprocess, sys

NN = sys.argv[1]
MONT = sys.argv[2].upper() if len(sys.argv) > 2 else 'A'
W = f'/Users/naiarodrigues/workspace/v{NN}-full'
DESK = '/Users/naiarodrigues/Desktop/conteudo youtube'
PASTA = next(d for d in sorted(os.listdir(DESK)) if d.startswith(NN + ' - '))
BRUTO = f'{DESK}/{PASTA}/bruto.mp4'
S = '/private/tmp/claude-501/-Users-naiarodrigues/5c602817-d2f5-42d4-b075-0ad4e659359b/scratchpad/live2'


def dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)


def enc(entrada, saida, ss=None, t=None, crf='18'):
    cmd = ['ffmpeg', '-y', '-v', 'error']
    if ss is not None:
        cmd += ['-ss', f'{ss:.3f}']
    cmd += ['-i', entrada]
    if t is not None:
        cmd += ['-t', f'{t:.3f}']
    cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', crf, '-pix_fmt', 'yuv420p',
            '-r', '30', '-c:a', 'aac', '-b:a', '192k', saida]
    subprocess.run(cmd, check=True)


mapa = json.load(open(f'{W}/mapa.json'))
gan = json.load(open(f'{W}/gancho.json'))
os.makedirs(f'{W}/proj/assets', exist_ok=True)
os.makedirs(f'{W}/blocos', exist_ok=True)

# ---------- 0. TRAVA DE BORDA ----------
# 05/08/2026. O Chefe assistiu 40 segundos do 07 e achou quatro palavras partidas ao meio.
# Rastreado: as quedas abruptas ja existiam no master, antes do HyperFrames e antes do corte
# fino. Nasciam AQUI, porque este passo cortava o gancho e a tela morta no tempo de palavra
# do whisper, e o whisper encurta o fim da palavra. Medido nos catorze: 36 palavras decepadas.
# Agora toda borda encosta no silencio medido por energia antes de virar comando de ffmpeg.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bordas

DB_BRUTO = bordas.envelope(BRUTO)
SIL_BRUTO = bordas.silencios(DB_BRUTO)
DUR_BRUTO = dur(BRUTO)
print(f'{len(SIL_BRUTO)} bloco(s) de silencio medido no bruto de {DUR_BRUTO:.1f}s')

# ---------- 1. tira a tela morta ----------
fonte = BRUTO
rem_pedido = mapa.get('remover') or []
rem, relatorio = bordas.ajusta([tuple(r) for r in rem_pedido], SIL_BRUTO, DUR_BRUTO, 'remover')
for r in relatorio:
    if r['andou'] != [0.0, 0.0] or not r['ok']:
        print(f"   borda {r['de']} -> {r['para']}  andou {r['andou']}"
              + ('' if r['ok'] else '   <<< SEM SILENCIO POR PERTO, VAI QUEBRAR PALAVRA'))
if rem:
    partes, cur, n = [], 0.0, dur(BRUTO)
    for a, b in rem:
        if a > cur:
            partes.append((cur, a))
        cur = b
    if cur < n:
        partes.append((cur, n))
    # pedaco de fracao de segundo (sobra do ultimo trecho removido) carrega timestamp
    # quebrado e o concat com -c copy infla o arquivo inteiro: no 13 um rabo de 0,01s
    # transformou 595s em 1710s. Fora qualquer parte abaixo de 0,25s.
    curtos = [(a, b) for a, b in partes if b - a < 0.25]
    partes = [(a, b) for a, b in partes if b - a >= 0.25]
    if curtos:
        print(f'descartados {len(curtos)} pedaco(s) menor(es) que 0,25s: '
              + ', '.join(f'{a:.2f}..{b:.2f}' for a, b in curtos))
    arqs = []
    for i, (a, b) in enumerate(partes):
        p = f'{S}/p{NN}_{i}.mp4'
        enc(BRUTO, p, ss=a, t=b - a)
        arqs.append(p)
    lst = f'{S}/l{NN}.txt'
    open(lst, 'w').write('\n'.join(f"file '{p}'" for p in arqs))
    fonte = f'{W}/corte_limpo.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0',
                    '-i', lst, '-c', 'copy', fonte], check=True)
    print(f'tela morta removida: {sum(b-a for a,b in rem):.1f}s em {len(rem)} trecho(s)')

# ---------- 2. gancho na frente ----------
# ARMADILHA: o diretor mede o gancho no corte ORIGINAL, mas aqui a fonte ja esta limpa.
# Sem mapear, o gancho sai de outro lugar do video (aconteceu no 06, em 04/08/2026).
def para_limpo(t):
    desc = 0.0
    for a, b in rem:
        if t >= b:
            desc += b - a
        elif t > a:
            raise SystemExit(f'ERRO: o gancho ({t:.2f}s) cai dentro de um trecho removido')
    return t - desc

gi, gf = para_limpo(gan['ini']), para_limpo(gan['fim'])
if rem:
    print(f"gancho mapeado: {gan['ini']:.2f}..{gan['fim']:.2f} no original  ->  {gi:.2f}..{gf:.2f} no corte limpo")

# O GANCHO E O PIOR CASO. Ele e um recorte de duas bordas, sai na frente de tudo e e o
# primeiro som que o espectador ouve: palavra partida ali estraga o video em dois segundos.
# As duas bordas encostam no silencio do arquivo de onde o gancho vai SAIR.
DB_FONTE = DB_BRUTO if fonte == BRUTO else bordas.envelope(fonte)
SIL_FONTE = SIL_BRUTO if fonte == BRUTO else bordas.silencios(DB_FONTE)
D_FONTE = dur(fonte)
gi2, dgi, oki = bordas.encosta(gi, SIL_FONTE, D_FONTE)
gf2, dgf, okf = bordas.encosta(gf, SIL_FONTE, D_FONTE)
if (dgi, dgf) != (0.0, 0.0):
    print(f'gancho encostado no silencio: {gi:.2f}..{gf:.2f} -> {gi2:.2f}..{gf2:.2f} '
          f'(andou {dgi:+.2f} e {dgf:+.2f})')
if not (oki and okf):
    print('   <<< ATENCAO: uma das bordas do gancho nao achou silencio em 2s')
gi, gf = gi2, gf2
enc(fonte, f'{W}/gancho.mp4', ss=gi, t=gf - gi, crf='17')
lst = f'{W}/lista.txt'
open(lst, 'w').write(f"file '{W}/gancho.mp4'\nfile '{fonte}'\n")
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0',
                '-i', lst, '-c', 'copy', f'{W}/master.mp4'], check=True)

subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{W}/master.mp4', '-an', '-c:v', 'copy',
                f'{W}/proj/assets/chefe.mp4'], check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{W}/master.mp4', '-vn', '-c:a', 'copy',
                f'{W}/proj/assets/chefe.m4a'], check=True)

DM = dur(f'{W}/master.mp4')
DG = dur(f'{W}/gancho.mp4')
# o clip do gancho tem que terminar exatamente onde a cena 2 comeca, senao o motor
# acusa sobreposicao de clip na mesma trilha (aconteceu no 06, por 0,02s)
prox = next((c['ini'] for c in mapa['cenas'] if c.get('tipo') != 'gancho'), None)
if prox and abs(DG - prox) < 0.5:
    DG = prox
print(f'gancho {DG:.2f}s   master {DM:.2f}s ({DM//60:.0f}:{DM%60:05.2f})')

# ---------- 2b. o mapa de deslocamento ----------
# Encostar as bordas no silencio muda a duracao do gancho e a dos trechos removidos, e com
# isso TODA cena do mapa anda alguns centesimos. Sem este arquivo eu teria que reancorar 14
# linhas do tempo na mao. Com ele, `remapeia.py` converte tempo do master ANTIGO para o
# master NOVO exatamente, porque o deslocamento e conhecido em cada ponto.
json.dump({'gancho_pedido': [gan['ini'], gan['fim']],
           'gancho_aplicado': [round(gi, 3), round(gf, 3)],
           'gancho_dur': round(DG, 3),
           'remover_pedido': [[round(a, 3), round(b, 3)] for a, b in
                              [tuple(r) for r in rem_pedido]],
           'remover_aplicado': [[round(a, 3), round(b, 3)] for a, b in rem],
           'master_dur': round(DM, 3)},
          open(f'{W}/remap.json', 'w'), indent=1)

# ---------- 2c. a prova ----------
# Emenda no master NOVO: o fim do gancho, e cada juncao dos trechos removidos deslocada
# pela duracao do gancho. Nenhuma delas pode ter som com corpo dos dois lados.
emendas = [DG]
acum = DG
_cur = 0.0
for a, b in rem:
    if a > _cur:
        acum += a - _cur
        emendas.append(round(acum, 3))
    _cur = b
bordas.confere(f'{W}/master.mp4', emendas, DM, f'master do {NN}')

# ---------- 3. esqueleto ----------
css = open(f'{S}/css_escuro_B.html' if MONT == 'B' else f'{S}/css_escuro.html').read()
for f in ['hyperframes.json', 'package.json', 'meta.json']:
    subprocess.run(['cp', f'/Users/naiarodrigues/workspace/t1-full/proj/{f}', f'{W}/proj/{f}'])
subprocess.run(['cp', '-r', '/Users/naiarodrigues/workspace/t1-full/proj/assets/fonts',
                f'{W}/proj/assets/'])

L = gan['linhas']
tam = [66, 112, 66, 66][:len(L)]
# linha larga demais QUEBRA em duas e invade a de baixo (aconteceu no 07 com
# "3 MIL NO CHECKOUT" em 112px). Encolhe ate caber em uma linha de 1124px.
# 0.62em por caractere e a media da Montserrat Black em caixa alta.
for i, t in enumerate(L):
    while tam[i] > 44 and len(t) * tam[i] * 0.62 > 1100:
        tam[i] -= 4
cor = ['#F7F5F0', '#F5402E', '#F7F5F0', '#F7F5F0'][:len(L)]
# cada linha reserva 1.18x o proprio corpo, senao o glifo de 112px invade a linha de baixo
alt, y = [], 0
for t in tam:
    alt.append(y); y += int(t * 1.60)
divs = '\n'.join(
    f'    <div id="cG-l{i+1}" style="position:absolute; left:0; top:{alt[i]}px; width:1124px; '
    f'font-weight:900; font-size:{tam[i]}px; line-height:1; letter-spacing:-0.032em; '
    f'color:{cor[i]}">{t}</div>' for i, t in enumerate(L))
# as linhas entram espalhadas pelo gancho inteiro, nao amontoadas no primeiro segundo:
# no 07 as tres linhas fechavam em 1,7s e o proximo evento so vinha em 4,7s, abrindo
# uma janela de 2,5s parada que reprovou a auditoria.
passo = min(0.85, max(0.45, (DG * 0.42) / max(1, len(L))))
ev = '\n'.join(f'tl.fromTo("#cG-l{i+1}", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, '
               f'duration: 0.45 }}, {0.10 + i*passo:.2f});' for i in range(len(L)))
# e um empurrao no meio de qualquer vao maior que 1,6s dentro do gancho
marcos = sorted([0.10 + i*passo + 0.45 for i in range(len(L))] +
                [DG*0.34+0.5, DG*0.48+0.5, DG*0.53+0.6, DG*0.66, DG*0.76+0.9, DG-0.5])
enche, ant = [], 0.0
for m in marcos:
    while m - ant > 1.6:
        t = ant + 1.4
        enche.append(f'tl.to("#cG-g1", {{ x: {24 if len(enche)%2==0 else 0}, duration: 0.6, ease: "power1.inOut" }}, {t:.2f});')
        ant = t
    ant = max(ant, m)
ev += ('\n' + '\n'.join(enche) if enche else '')

corpo = f'''<body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DM+0.03:.2f}" data-width="1920" data-height="1080">
      <div id="painel">
        <div id="chrome-fixo" class="clip" data-start="0" data-duration="{DM:.2f}" data-track-index="3">
          <div class="cab">
            <div class="marca-a">A</div>
            <div>
              <div class="marca-nome">Avalanche</div>
              <div class="marca-kicker">IA APLICADA A NEGÓCIOS</div>
            </div>
          </div>
          <div class="regua"></div>
          <div class="rod">AVALANCHE &middot; MAPA DO EPISÓDIO</div>
        </div>
        <div id="rotulo-capitulo" class="clip capitulo" data-start="0" data-duration="{DM:.2f}" data-track-index="1">{mapa.get('capitulo', mapa['video'].split(' - ')[-1].upper())}</div>

<div id="cG" class="clip livre" data-start="0.00" data-duration="{DG:.2f}" data-track-index="2">
  <div id="cG-g1" style="position:absolute; left:64px; top:206px; width:1124px; height:420px">
{divs}
  </div>
  <div id="cG-sub" class="sub" style="top: 616px">{gan.get('sub','')}</div>
  <div id="cG-faixa" class="faixa" style="top: 720px">
    <div class="faixa-rot">{gan.get('faixa_rot','O QUE ESTE VÍDEO MOSTRA')}</div>
    <div id="cG-dado" class="faixa-dado">{gan.get('faixa','')}</div>
  </div>
</div>
<!--CENAS-->
      </div>

      <div id="coluna">
        <video id="video-chefe" class="clip" src="assets/chefe.mp4" data-start="0" data-duration="{DM:.2f}" data-track-index="0" muted></video>
      </div>
      <audio id="audio-chefe" src="assets/chefe.m4a" data-start="0" data-duration="{DM:.2f}"></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      const fmt = (n) => Math.round(n).toLocaleString("pt-BR");
      const trocaD = (id, txt) => {{ document.getElementById(id).textContent = txt; }};

{ev}
tl.fromTo("#cG-sub", {{ opacity: 0, x: -22 }}, {{ opacity: 1, x: 0, duration: 0.5 }}, {DG*0.34:.2f});
tl.fromTo("#cG-faixa", {{ opacity: 0, y: 26 }}, {{ opacity: 1, y: 0, duration: 0.5 }}, {DG*0.48:.2f});
tl.fromTo("#cG-dado", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.6 }}, {DG*0.53:.2f});
tl.to("#cG-l2", {{ scale: 1.045, duration: 0.9, ease: "power1.inOut", transformOrigin: "0% 50%" }}, {DG*0.66:.2f});
tl.to("#cG-l2", {{ scale: 1.0, duration: 0.9, ease: "power1.inOut" }}, {DG*0.76:.2f});
tl.to("#cG", {{ opacity: 0, duration: 0.5, ease: "power1.in" }}, {DG-0.5:.2f});
<!--JS-->

// a marca so aparece na cena do gancho e sai, liberando a tela inteira
const cabecalho = ["#chrome-fixo .cab", "#chrome-fixo .regua", "#chrome-fixo .rod", "#rotulo-capitulo"];
tl.set(cabecalho, {{ opacity: 0 }}, 0);
tl.to(cabecalho, {{ opacity: 1, duration: 0.5, ease: "power1.out" }}, 0.20);
tl.to(cabecalho, {{ opacity: 0, duration: 0.6, ease: "power1.inOut" }}, {DG-0.7:.2f});

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
open(f'{W}/esqueleto.html', 'w', encoding='utf-8').write(css + '\n' + corpo)

# ---------- 4. as quatro duracoes conferidas ----------
s = open(f'{W}/esqueleto.html', encoding='utf-8').read()
achou = re.findall(r'data-duration="([\d.]+)"', s)
print(f'montagem {MONT}  ·  duracoes no esqueleto: {achou}')
print(f'esqueleto pronto: {W}/esqueleto.html')
