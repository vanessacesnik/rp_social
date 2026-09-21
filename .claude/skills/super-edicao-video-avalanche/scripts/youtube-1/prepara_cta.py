#!/usr/bin/env python3
"""
prepara_cta.py <cta1|cta2> <A|B> <gravacao.MOV> [--refaz] · master, esqueleto e assets.

Um CTA é uma peça de 60 a 90 segundos que entra NO MEIO dos vídeos do canal. Herda a
identidade do youtube-1 inteira (painel escuro, coluna da gravação, faixa, infográfico),
com quatro diferenças que vêm de ser inserção e não vídeo:

1. NÃO TEM GANCHO. Gancho existe para segurar quem acabou de chegar; no meio do vídeo
   ele só atrasa a mensagem. A cena 1 já é fala.
2. O CABEÇALHO FICA A PEÇA INTEIRA. No vídeo normal a marca sai junto com o gancho para
   liberar a tela; aqui ela é o sinal de que isto é um recado do canal, não o assunto.
3. NÃO TEM RODAPÉ E NÃO TEM O CARIMBO DE CENA. O rodapé `.rod` mora no pé do painel e a
   faixa de dados fica exatamente em cima dele: com o cabeçalho permanente os dois brigam
   e o `check` reprova por texto encoberto. E o carimbo `.beat` nasce em `top: 34px`,
   dentro do cabeçalho. Quem nomeia a cena aqui é o rótulo de capítulo, que troca de
   texto a cada cena.
4. A FONTE É GRAVAÇÃO DE CELULAR NA VERTICAL, não a live. Vem em 2160x3840 com matriz de
   rotação no contêiner. O ffmpeg aplica a rotação sozinho ao recodificar, mas o Dolby
   Vision em HEVC precisa ir para h264 yuv420p senão o motor do HyperFrames não abre.

IDEMPOTENTE NO MASTER. Rodar de novo para consertar o esqueleto não pode custar minutos
de recodificação, e a gravação de origem some do Downloads assim que o Chefe limpa a
pasta. O master convertido passa a ser a fonte da verdade: só é refeito com `--refaz`.
"""
import json, os, re, subprocess, sys

NOME = sys.argv[1]
MONT = sys.argv[2].upper() if len(sys.argv) > 2 else 'A'
FONTE = sys.argv[3] if len(sys.argv) > 3 else ''
W = f'/Users/naiarodrigues/workspace/{NOME}-full'
S = ('/private/tmp/claude-501/-Users-naiarodrigues/'
     '5c602817-d2f5-42d4-b075-0ad4e659359b/scratchpad/live2')


def dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)


mapa = json.load(open(f'{W}/mapa.json'))
os.makedirs(f'{W}/proj/assets', exist_ok=True)
os.makedirs(f'{W}/blocos', exist_ok=True)

# ---------- 1. master ----------
if os.path.exists(f'{W}/master.mp4') and '--refaz' not in sys.argv:
    print(f'master ja existe, mantido: {W}/master.mp4')
else:
    if not os.path.exists(FONTE):
        raise SystemExit(f'ERRO: a gravacao de origem sumiu ({FONTE}) e nao ha master')
    # 1080 de largura sobra: a coluna exibe 572px. Mais que isso so engorda o arquivo.
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', FONTE,
                    '-vf', 'scale=1080:-2', '-c:v', 'libx264', '-preset', 'medium',
                    '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
                    f'{W}/master.mp4'], check=True)

for saida, flag, cod in [('chefe.mp4', '-an', ['-c:v', 'copy']),
                         ('chefe.m4a', '-vn', ['-c:a', 'copy'])]:
    if not os.path.exists(f'{W}/proj/assets/{saida}') or '--refaz' in sys.argv:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{W}/master.mp4', flag]
                       + cod + [f'{W}/proj/assets/{saida}'], check=True)

DM = dur(f'{W}/master.mp4')
r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                    '-show_entries', 'stream=width,height', '-of', 'csv=p=0',
                    f'{W}/master.mp4'], capture_output=True, text=True).stdout.strip()
print(f'master {DM:.2f}s  ·  {r}  (a coluna exibe 572x1016)')

c = mapa['cenas']
fim = c[-1]['ini'] + c[-1]['dur']
if fim > DM + 0.05:
    raise SystemExit(f'ERRO: o mapa termina em {fim:.2f}s mas o master tem {DM:.2f}s')

# ---------- 2. esqueleto ----------
css = open(f'{S}/css_escuro_B.html' if MONT == 'B' else f'{S}/css_escuro.html').read()
for f in ['hyperframes.json', 'package.json', 'meta.json']:
    subprocess.run(['cp', f'/Users/naiarodrigues/workspace/t1-full/proj/{f}', f'{W}/proj/{f}'])
subprocess.run(['cp', '-r', '/Users/naiarodrigues/workspace/t1-full/proj/assets/fonts',
                f'{W}/proj/assets/'])

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
        </div>
        <div id="rotulo-capitulo" class="clip capitulo" data-start="0" data-duration="{DM:.2f}" data-track-index="1"><span id="cap-txt">{mapa['capitulo']}</span></div>
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

<!--JS-->

// no CTA a marca NAO sai: ela e o sinal de que isto e um recado do canal.
// o rotulo troca de texto a cada cena, entao o tween vai no SPAN interno `#cap-txt`:
// o motor gerencia a visibilidade do proprio clip, e animar opacidade nele reprova o
// `check` com gsap_exit_missing_hard_kill em toda troca de cena.
const cabecalho = ["#chrome-fixo .cab", "#chrome-fixo .regua"];
tl.set(cabecalho, {{ opacity: 0 }}, 0);
tl.set("#cap-txt", {{ opacity: 0 }}, 0);
tl.to(cabecalho, {{ opacity: 1, duration: 0.5, ease: "power1.out" }}, 0.15);
tl.to("#cap-txt", {{ opacity: 1, duration: 0.5, ease: "power1.out" }}, 0.15);
tl.to(cabecalho, {{ opacity: 0, duration: 0.5, ease: "power1.inOut" }}, {DM-0.6:.2f});
tl.to("#cap-txt", {{ opacity: 0, duration: 0.5, ease: "power1.inOut" }}, {DM-0.6:.2f});

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
open(f'{W}/esqueleto.html', 'w', encoding='utf-8').write(css + '\n' + corpo)

s = open(f'{W}/esqueleto.html', encoding='utf-8').read()
print(f'montagem {MONT}  ·  duracoes no esqueleto: {re.findall(r"data-duration=.([0-9.]+).", s)}')
print(f'esqueleto pronto: {W}/esqueleto.html')
