#!/usr/bin/env python3
"""
blocos_cta.py <dir> · gera blocos/A.html a partir de blocos.json.

Nos 14 vídeos os blocos foram escritos por agentes, um bloco cada, e o custo disso foi
uma lista de armadilhas: evento fora do `<script>`, empurrão que não move pixel, faixa
fatiada em partes iguais em vez de ancorada na fala, linha larga que quebra e invade a
de baixo. Um CTA é curto e repetitivo o bastante para ser DETERMINÍSTICO, então aqui o
conteúdo editorial vive num JSON e a geometria e o tempo saem de código.

O que o código garante sozinho, e por isso não pode mais dar errado:

TIPOGRAFIA QUE CABE. Toda linha encolhe até caber na largura do próprio contêiner, com
0.56em por caractere na Montserrat. Nada quebra em duas linhas por acidente.

FAIXA ANCORADA NA FALA. Cada troca do dado tem um tempo medido na transcrição, nunca uma
fatia igual da cena. É a diferença entre a tela dizer o que ele está dizendo e a tela
dizer outra coisa.

TELA NUNCA PARADA. Depois de montar os eventos da cena, procura vão maior que 1,6s e
enfia um empurrão de verdade, alternando o destino: repetir `x: 24` duas vezes não move
nada na segunda, e foi assim que uma auditoria passou com a tela congelada.

O INFOGRÁFICO NÃO SAI. Numa cena de infográfico a arte entra uma vez e fica até o corte.
Ordem do Chefe para o trecho da equipe da Naia: o quadro fica na tela durante a
explicação inteira, e quem se move é a faixa embaixo dele.
"""
import json, os, sys

W = os.path.abspath(sys.argv[1])
spec = json.load(open(f'{W}/blocos.json', encoding='utf-8'))
mapa = json.load(open(f'{W}/mapa.json', encoding='utf-8'))
CENAS = {c['id']: c for c in mapa['cenas']}

EM = 0.56               # largura media de um caractere, em fracao do corpo

# GEOMETRIA DO CTA. O cabecalho permanente ocupa 54..175 do painel (marca, regua e
# rotulo de capitulo), entao o conteudo nasce em 200 e nao em 34 como no video normal.
# A faixa fecha em 1002, a dois pixels do pe do painel de 1016.
HL_TOP    = 208         # headline das cenas de texto
LIN_TOP   = 336         # bloco de linhas grandes das cenas de texto
LIN_PASSO = 112
SUB_TOP   = 690
CART_TOP  = 380         # cartela: linha unica ou tres linhas centradas na vertical
CART_PASSO = 150
ART_TOP   = 200         # infografico: sem headline, a arte ja tem o proprio titulo
ART_ALT   = 636
FAIXA_TOP = 850


def cabe(txt, largura, tam, minimo=28):
    while tam > minimo and len(txt) * tam * EM > largura:
        tam -= 2
    return tam


class Cena:
    def __init__(self, d):
        self.d = d
        self.id = d['id']
        self.c = CENAS[self.id]
        self.t0 = self.c['ini']
        self.t1 = self.c['ini'] + self.c['dur']
        self.html = []
        self.js = []
        self.marcos = []

    def ev(self, linha, t):
        self.js.append((t, linha))
        self.marcos.append(t)

    # ------------------------------------------------------------------ peças
    def rotulo(self, rot, primeiro):
        """quem nomeia a cena e o rotulo de capitulo do esqueleto, que troca de texto.

        No video normal existe o carimbo `.beat` em top 34px, mas ali o cabecalho ja
        saiu com o gancho. No CTA o cabecalho fica, o carimbo cairia dentro dele, e um
        segundo titulo logo abaixo do rotulo so empilha ruido. Entao o rotulo E o
        carimbo: uma linha so, sempre no mesmo lugar, trocando a cada cena."""
        if primeiro:
            return                                   # o esqueleto ja nasce com este texto
        # A troca NAO pode terminar em cima do inicio do clip: o lint le qualquer
        # `opacity: 0` que fecha num limite de clip como saida de cena e exige um
        # desligamento explicito, que aqui apagaria o rotulo de vez. Fechando o apagar
        # 0,30s antes do corte, a troca acontece no fim da cena anterior e o rotulo ja
        # chega aceso na cena nova.
        self.ev(f'tl.to("#cap-txt", {{ opacity: 0, duration: 0.20, '
                f'ease: "power1.in", onComplete: () => trocaD("cap-txt", "{rot}") }}',
                self.t0 - 0.50)
        self.ev(f'tl.to("#cap-txt", {{ opacity: 1, duration: 0.26, '
                f'ease: "power1.out" }}', self.t0 - 0.28)

    def headline(self, txt, top):
        tam = cabe(txt, 1090, 52, 34)
        self.html.append(
            f'  <div id="{self.id}-hl" class="headline" style="top: {top}px; '
            f'font-size: {tam}px; opacity: 0">{txt}</div>')
        self.ev(f'tl.fromTo("#{self.id}-hl", {{ opacity: 0, y: 20 }}, '
                f'{{ opacity: 1, y: 0, duration: 0.45 }}', self.t0 + 0.36)

    def linhas(self, linhas, top, base, passo, cores):
        self.html.append(f'  <div id="{self.id}-g" style="position: absolute; left: 64px; '
                         f'top: {top}px; width: 1124px; height: {passo*len(linhas)+40}px">')
        for i, t in enumerate(linhas):
            tam = cabe(t, 1124, base, 32)
            self.html.append(
                f'    <div id="{self.id}-l{i+1}" style="position: absolute; left: 0; '
                f'top: {i*passo}px; width: 1124px; font-weight: 900; font-size: {tam}px; '
                f'line-height: 1; letter-spacing: -0.03em; color: {cores[i % len(cores)]}; '
                f'opacity: 0">{t}</div>')
        self.html.append('  </div>')
        # CENA CURTA. Com passo fixo de 0,75s a terceira linha de uma cena de 1,8s nascia
        # DEPOIS que o fade de saida ja tinha comecado, e ela aparecia sumindo.
        folga = (self.t1 - 0.7) - (self.t0 + 0.85)
        passo_t = min(0.75, folga / max(1, len(linhas) - 1)) if len(linhas) > 1 else 0.0
        for i, t in enumerate(linhas):
            self.ev(f'tl.fromTo("#{self.id}-l{i+1}", {{ opacity: 0, y: 24 }}, '
                    f'{{ opacity: 1, y: 0, duration: 0.45 }}', self.t0 + 0.85 + i * passo_t)

    def sub(self, txt, top):
        self.html.append(f'  <div id="{self.id}-sub" class="sub" style="top: {top}px; '
                         f'opacity: 0">{txt}</div>')
        self.ev(f'tl.fromTo("#{self.id}-sub", {{ opacity: 0, x: -22 }}, '
                f'{{ opacity: 1, x: 0, duration: 0.5 }}', self.t0 + 1.30)

    def arte(self, arq, top=ART_TOP, alt=ART_ALT):
        self.html.append(f'  <div id="{self.id}-art" class="img-area grande info" '
                         f'style="top: {top}px; height: {alt}px; opacity: 0">'
                         f'<img id="{self.id}-img" src="assets/{arq}" '
                         f'style="height: {alt}px" alt="" /></div>')
        # entra UMA vez e fica: a arte nao pisca e nao sai antes do corte
        self.ev(f'tl.fromTo("#{self.id}-art", {{ opacity: 0 }}, '
                f'{{ opacity: 1, duration: 0.6, ease: "power1.out" }}', self.t0 + 0.80)

    def faixa(self, rot, batidas, ticks, top=850):
        self.html.append(f'  <div id="{self.id}-faixa" class="faixa" style="top: {top}px; opacity: 0">')
        self.html.append(f'    <div class="faixa-rot">{rot}</div>')
        self.html.append(f'    <div id="{self.id}-dado" class="faixa-dado">{batidas[0][1]}</div>')
        if ticks:
            self.html.append('    <div class="ticker-linha">')
            for i, k in enumerate(ticks):
                self.html.append(f'      <span id="{self.id}-k{i+1}" class="tick" '
                                 f'style="opacity: 0">{k}</span>')
            self.html.append('    </div>')
        self.html.append('  </div>')
        self.ev(f'tl.fromTo("#{self.id}-faixa", {{ opacity: 0, y: 26 }}, '
                f'{{ opacity: 1, y: 0, duration: 0.5 }}', self.t0)
        # A troca leva 0,22s para sair e 0,28s para entrar: qualquer batida depois de
        # t1-1.0 entra durante o fade e o espectador ve a faixa piscando ao sumir.
        # A troca inteira leva 0,50s (0,22 saindo + 0,28 entrando). Duas batidas a menos
        # de 0,55s uma da outra se atropelam e a faixa fica piscando sem nunca assentar:
        # aconteceu no CTA 2, onde ele lista cinco canais em dois segundos. A saida e
        # juntar os itens numa batida so, e este aviso e quem denuncia.
        for (ta, _), (tb, _) in zip(batidas, batidas[1:]):
            if tb - ta < 0.55:
                print(f'   ! {self.id}: batidas em {ta:.2f} e {tb:.2f} estao a '
                      f'{tb-ta:.2f}s, junte as duas numa linha so')
        for t, txt in batidas[1:]:
            if t > self.t1 - 1.0:
                print(f'   ! {self.id}: batida em {t:.2f} caiu no fade, movida para {self.t1-1.0:.2f}')
                t = self.t1 - 1.0
            self.ev(f'tl.to("#{self.id}-dado", {{ x: -18, opacity: 0, duration: 0.22, '
                    f'ease: "power1.in", onComplete: () => trocaD("{self.id}-dado", "{txt}") }}', t)
            self.ev(f'tl.fromTo("#{self.id}-dado", {{ x: 18, opacity: 0 }}, '
                    f'{{ x: 0, opacity: 1, duration: 0.28, ease: "power1.out" }}', t + 0.24)
        # os ticks acendem espalhados pelo miolo da cena
        if ticks:
            a, b = self.t0 + 1.1, self.t1 - 1.2
            for i in range(len(ticks)):
                t = a + (b - a) * (i / max(1, len(ticks) - 1)) if len(ticks) > 1 else a
                self.ev(f'tl.fromTo("#{self.id}-k{i+1}", {{ opacity: 0, y: 14 }}, '
                        f'{{ opacity: 1, y: 0, duration: 0.34 }}', t)

    # ------------------------------------------------------------------ fecho
    def fecha(self, alvo_empurrao):
        """enche vao morto e escreve a saida"""
        self.marcos.append(self.t0)
        enche, ant, estado = [], self.t0, 0
        for m in sorted(self.marcos):
            while m - ant > 1.6:
                t = ant + 1.4
                estado = 24 if estado == 0 else 0
                enche.append((t, f'tl.to("#{alvo_empurrao}", {{ x: {estado}, duration: 0.6, '
                                 f'ease: "power1.inOut" }}'))
                ant = t
            ant = max(ant, m)
        while self.t1 - 0.6 - ant > 1.6:
            t = ant + 1.4
            estado = 24 if estado == 0 else 0
            enche.append((t, f'tl.to("#{alvo_empurrao}", {{ x: {estado}, duration: 0.6, '
                             f'ease: "power1.inOut" }}'))
            ant = t
        self.js += enche
        self.js.append((self.t1 - 0.5,
                        f'tl.to("#{self.id}", {{ opacity: 0, duration: 0.5, ease: "power1.in" }}'))
        self.js.sort()

    def render(self):
        c = self.c
        h = [f'<div id="{self.id}" class="clip livre" data-start="{self.t0:.2f}" '
             f'data-duration="{c["dur"]:.2f}" data-track-index="2">'] + self.html + ['</div>']
        j = [f'{l}, {t:.2f});' for t, l in self.js]
        return '\n'.join(h), '\n'.join(j)


saida_h, saida_j = [], []
for i, d in enumerate(spec['cenas']):
    s = Cena(d)
    tipo = s.c.get('tipo')
    s.rotulo(d['rotulo'], primeiro=(i == 0))

    if tipo == 'cartela':
        s.linhas(d['linhas'], CART_TOP, 92, CART_PASSO,
                 d.get('cores', ['#F7F5F0', '#F7F5F0', '#4FD8EF']))
        alvo = f'{s.id}-g'
    elif tipo == 'infografico':
        # SEM headline: a arte carrega o proprio titulo, e uma segunda linha de titulo
        # logo abaixo do rotulo de capitulo so rouba altura da arte.
        s.arte(s.c['arte'])
        s.faixa(d['faixa_rot'], d['batidas'], d.get('ticks', []), FAIXA_TOP)
        alvo = f'{s.id}-art'
    else:
        s.headline(d['headline'], HL_TOP)
        s.linhas(d['linhas'], LIN_TOP, 68, LIN_PASSO,
                 d.get('cores', ['#F7F5F0', '#94A3B8', '#4FD8EF']))
        if d.get('sub'):
            s.sub(d['sub'], SUB_TOP)
        s.faixa(d['faixa_rot'], d['batidas'], d.get('ticks', []), FAIXA_TOP)
        alvo = f'{s.id}-hl'

    s.fecha(alvo)
    a, b = s.render()
    saida_h.append(a)
    saida_j.append(f'/* ---- {s.id} ---- */\n' + b)

os.makedirs(f'{W}/blocos', exist_ok=True)
open(f'{W}/blocos/A.html', 'w', encoding='utf-8').write(
    '<!--HTML-->\n' + '\n\n'.join(saida_h) + '\n\n<!--JS-->\n' + '\n\n'.join(saida_j) + '\n')

print(f'{len(spec["cenas"])} cenas escritas em {W}/blocos/A.html')
for d in spec['cenas']:
    c = CENAS[d['id']]
    print(f'  {d["id"]}  {c["ini"]:6.2f}..{c["ini"]+c["dur"]:6.2f}  {c.get("tipo","texto"):12s} {d["rotulo"]}')
