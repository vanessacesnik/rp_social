#!/usr/bin/env python3
"""gen_thumb.py · thumbnail nova do lote kimi, no idioma visual da que ja existe.

Uso:
    python3 gen_thumb.py <saida.png> <ref.png> <"LINHA 1"> <"LINHA 2"> [<"LINHA 3">] [--acento "#4FD8EF"]

A referencia e a thumb do mesmo video no lote anterior: o `refs` do gpt-image-2 e o que
segura o rosto, o traco e a energia. A linha 1 sai na cor de acento e bem maior; as outras
em branco creme.

REGRAS QUE NAO SE NEGOCIAM (batem com o manual):
  · sem acento nenhum no texto, porque o modelo derruba acento em palavra teimosa
  · fundo de COR SOLIDA, uma forma geometrica solida atras, zero gradiente
  · rota OAuth obrigatoria; se voltar `api-paga`, para e avisa
  · corte final exato em 1280x720
"""
import os, sys

sys.path.insert(0, os.path.expanduser('~/naia-agent/scripts'))
from naia_image import gerar
from PIL import Image

args = [a for a in sys.argv[1:] if not a.startswith('--')]
acento = '#4FD8EF'
if '--acento' in sys.argv:
    acento = sys.argv[sys.argv.index('--acento') + 1]

saida, ref, linhas = args[0], args[1], args[2:]
if len(linhas) < 2:
    sys.exit('precisa de pelo menos duas linhas de texto')

txt = f'linha 1, em {acento}, bem maior que o resto: "{linhas[0]}"\n'
txt += f'linha 2, em branco creme: "{linhas[1]}"\n'
if len(linhas) > 2:
    txt += f'linha 3, em branco creme, menor: "{linhas[2]}"\n'

PROMPT = f"""Thumbnail de YouTube 16:9, ilustracao vetorial de alto contraste, mesmo idioma visual da imagem de referencia (mesmo homem, mesmo tratamento de traco e sombra, mesma energia).

HOMEM: careca, barba grossa preta com fios brancos no queixo, pele negra retinta, camiseta preta. Expressao forte de quem esta revelando algo. Ocupa o lado DIREITO do quadro, do peito para cima, recorte com contorno branco grosso separando do fundo.

FUNDO: cor solida unica, azul petroleo bem escuro (#0F172A), com UMA forma geometrica solida em {acento} atras dele. Sem gradiente nenhum, sem textura, sem brilho.

TEXTO no lado ESQUERDO, empilhado, alinhado a esquerda, tipografia display pesadissima condensada, com contorno escuro grosso:
{txt}
Ortografia exatamente como escrita acima, sem acento nenhum, sem pontuacao, sem emoji, sem travessao. Nada de gradiente. Nada de marca alheia. Texto todo dentro do quadro, com margem de respiro, nunca encostando na borda nem no homem."""

raw = saida.replace('.png', '_raw.png')
r = gerar(PROMPT, raw, size="1536x1024", quality="high", refs=[ref], timeout=900,
          allow_paid_fallback=False)
print("rota:", r.get("rota"))
if r.get("rota") != "oauth":
    sys.exit("ROTA ERRADA, o OAuth caiu e estaria gastando credito do Chefe")

im = Image.open(raw).convert("RGB")
w, h = im.size
alvo = 1280 / 720
if w / h > alvo:
    nw = int(h * alvo)
    im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
else:
    nh = int(w / alvo)
    im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
im.resize((1280, 720), Image.LANCZOS).save(saida)
print("thumb:", saida)
