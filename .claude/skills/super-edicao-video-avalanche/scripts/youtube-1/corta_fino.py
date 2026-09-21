#!/usr/bin/env python3
"""
corta_fino.py entrada.mp4 saida.mp4 --words palavras.json --conteudo cortes.json
              [--cauda 10] [--min 0.22]

Corte de silêncio de VERDADE, mais o corte de conteúdo, num passe só.

POR QUE ESTA VERSÃO EXISTE (05/08/2026). O `corta_silencio.py` deixava passar pausa de
até 9 segundos dentro do vídeo. A causa não era o limiar, era o VETO: ele olhava o
intervalo que o whisper declara para cada palavra, e o whisper ESTICA esse intervalo
por cima da pausa. No vídeo 05 ele jurava que a palavra "ou" durava 4,48 segundos e
que "mais" durava 4,07. Cada uma dessas palavras blindava vários segundos de silêncio.
Resultado medido nos catorze entregues: de 3,9% a 26,7% do vídeo era silêncio.

O QUE MUDA. A extensão real de cada palavra passa a sair da ENERGIA, não do que o
whisper declara. Dentro da janela que o whisper aponta, procuramos onde o áudio de
fato está acima do piso, e é ESSE pedaço que fica protegido. O silêncio em volta vira
cortável, mesmo estando "dentro" da palavra segundo o whisper.

DOIS LIMIARES, e é isso que impede comer sílaba:
  -45 dB  acha o silêncio (o que dá para cortar)
  -58 dB  acha a CAUDA da palavra (o que não se pode tocar)
Consoante final de "mais", "então", "faz" tem energia baixa e morreria com um limiar
só. Com o limiar sensível para a cauda, a última sílaba fica protegida.

GUARDA ASSIMÉTRICA. 0,06s antes da palavra e 0,20s depois, porque o problema é sempre
na cauda: é ali que a consoante mora e é ali que o Chefe percebe o corte comendo a
última sílaba.

A CAUDA DO ARQUIVO (a arte de encerramento) fica intocada: passe `--cauda 10`.
"""
import argparse, json, os, re, subprocess, sys, tempfile
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('entrada'); ap.add_argument('saida')
ap.add_argument('--words', required=True, help='json do whisper -ml 1 -oj do MESMO audio')
ap.add_argument('--conteudo', required=True,
                help='json obrigatorio [{ini,fim,tipo,texto}] de repeticao/dispensavel')
ap.add_argument('--cauda', type=float, default=0.0, help='segundos no fim que NAO podem ser tocados')
ap.add_argument('--min', type=float, default=0.22, help='pausa minima para valer o corte')
ap.add_argument('--piso-fala', type=float, default=-45.0)
ap.add_argument('--piso-cauda', type=float, default=-58.0)
ap.add_argument('--guarda-antes', type=float, default=0.06)
ap.add_argument('--guarda-depois', type=float, default=0.20)
ap.add_argument('--plano', default=None)
A = ap.parse_args()

HOP = 0.010                                   # 10ms, fino o bastante para achar sílaba

# ---------- envelope ----------
raw = tempfile.mktemp(suffix='.raw')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', A.entrada,
                '-ac', '1', '-ar', '16000', '-f', 's16le', raw], check=True)
a = np.fromfile(raw, dtype=np.int16).astype(np.float32) / 32768
os.unlink(raw)
SR = 16000
win = int(SR * HOP)
n = len(a) // win
DUR = len(a) / SR
env = np.sqrt(np.maximum((a[:n * win].reshape(n, win) ** 2).mean(1), 1e-12))
db = 20 * np.log10(env)
t = np.arange(n) * HOP

fala = db > A.piso_fala          # onde tem fala audivel
cauda = db > A.piso_cauda        # onde ainda tem resquicio de fala (consoante final)

# ---------- silencio: SO energia, o whisper nao opina ----------
# A VERDADE QUE DESTRAVOU ISSO (05/08/2026): se um trecho nao tem energia, nao pode
# haver palavra nele. Entao o whisper nao precisa autorizar corte de silencio, ele so
# serve para o corte de CONTEUDO. A tentativa anterior perguntava ao whisper onde a
# palavra comeca e acaba, e ele agrupa "para" com cinco segundos de pausa junto, o que
# blindava a pausa inteira. Medido no 05: 88% do arquivo ficava protegido e sobravam
# 71 segundos de pausa acima de 1 segundo.
#
# O unico risco real e cortar a CAUDA da palavra anterior (consoante final, energia
# baixa) ou o ATAQUE da proxima. Por isso a guarda nao e fixa: ela anda para dentro do
# silencio enquanto o sinal ainda esta decaindo acima do piso de cauda.
def idx(x):
    return int(min(max(x, 0.0) / HOP, n - 1))


q = db < A.piso_fala
dd = np.diff(np.concatenate(([0], q.view(np.int8), [0])))
ini = np.where(dd == 1)[0]
fim = np.where(dd == -1)[0]

limite_t = DUR - A.cauda
silencio, recusados = [], []
for i0, i1 in zip(ini, fim):
    s0, s1 = i0 * HOP, i1 * HOP
    if s1 > limite_t:
        s1 = limite_t
    if s1 - s0 < A.min:
        continue
    # anda para a direita enquanto a cauda da palavra anterior ainda soa
    k = i0
    while k < i1 and db[k] > A.piso_cauda:
        k += 1
    c0 = k * HOP + A.guarda_depois
    # anda para a esquerda enquanto o ataque da proxima ja soa
    k = i1 - 1
    while k > i0 and db[k] > A.piso_cauda:
        k -= 1
    c1 = (k + 1) * HOP - A.guarda_antes
    c1 = min(c1, limite_t)
    if c1 - c0 >= A.min:
        silencio.append((round(c0, 3), round(c1, 3)))
    else:
        recusados.append((round(s0, 2), round(s1, 2), 'sobrou menos que o minimo depois das guardas'))

# as palavras ainda sao lidas, mas so para o corte de CONTEUDO e para a prova
d = json.load(open(A.words))
brutas = [(x['text'], x['offsets']['from'] / 1000, x['offsets']['to'] / 1000)
          for x in d['transcription'] if x['text'].strip() and re.search(r'\w', x['text'])]
pal = []
for w, x, y in brutas:
    if pal and not w.startswith(' '):
        pal[-1] = (pal[-1][0] + w.strip(), pal[-1][1], y)
    else:
        pal.append((w.strip(), x, y))
uni = []
esticadas = 0

# ---------- blocos de fala definidos pelo SILENCIO medido ----------
# POR QUE (05/08/2026, terceira tentativa e a que funciona). As duas primeiras usaram
# o intervalo entre palavras do whisper como fronteira de fala. Isso nao serve: whisper
# separa palavra sem que exista silencio no audio, e cortar ali quebra a frase (no 05
# sobrou "tiras na vida", metade de "tirando quem ja construiu um funil de vendas").
#
# A fronteira confiavel e o SILENCIO MEDIDO. Definimos os blocos como o que existe
# ENTRE duas pausas reais de energia. Cortar um bloco inteiro pousa nas duas pausas que
# o cercam, por construcao, e nao existe borda dentro de fala.
PAUSA_MIN = 0.35
pausas = []
for i0, i1 in zip(ini, fim):
    if (i1 - i0) * HOP >= PAUSA_MIN:
        pausas.append((i0 * HOP, i1 * HOP))

blocos = []
ant = 0.0
for pa, pb in pausas:
    if pa > ant + 0.3:
        blocos.append((ant, pa))
    ant = pb
if ant < DUR:
    blocos.append((ant, DUR))

texto_de = {}
for b0, b1 in blocos:
    texto_de[(b0, b1)] = ' '.join(w for w, x, y in pal if b0 - 0.2 <= x and y <= b1 + 0.2)

recusados_conteudo = []


def bloco_de_falas(x, y):
    """blocos SUBSTANCIALMENTE dentro de [x, y].

    Exigir so que o miolo caia dentro deixa o corte guloso: um bloco de 28 segundos
    entrava inteiro por causa de um pedido de 8. No 05 isso INVERTEU um sentido, comendo
    o "eu nao estou falando" de "eu nao estou falando que voce nao vai mais usar
    plataformas". Agora o bloco so entra se 70% dele estiver dentro do pedido.
    """
    dentro = []
    for b0, b1 in blocos:
        inter = max(0.0, min(b1, y + 0.4) - max(b0, x - 0.4))
        if inter >= 0.70 * (b1 - b0):
            dentro.append((b0, b1))
    if not dentro:
        return None
    return dentro[0][0], dentro[-1][1]


# ---------- corte de conteudo, aparado pelas mesmas protecoes ----------
conteudo = []
if A.conteudo:
    for c in json.load(open(A.conteudo)):
        x, y = float(c['ini']), float(c['fim'])
        if y > limite_t:
            continue
        # REGRA QUE IMPEDE FRASE QUEBRADA (05/08/2026). Nao basta encostar o corte no
        # silencio mais proximo: se a borda cair no meio de uma frase, a emenda vira
        # salto. Aconteceu no 05, onde sobrou "eu vou ate sequer saibam o que e
        # automacao". Agora toda borda de corte de CONTEUDO tem que pousar numa PAUSA
        # DE VERDADE, ou seja, num vao de silencio com pelo menos `pausa_min`. Se nao
        # houver pausa perto, o corte e RECUSADO, nao aproximado.
        bl = bloco_de_falas(x, y)
        if bl is None:
            recusados_conteudo.append((round(x, 2), round(y, 2), c.get('tipo', ''),
                                       'nao cobre nenhuma fala inteira'))
            continue
        b0, b1 = bl
        # O BLOCO PRECISA ESTAR CERCADO DE PAUSA. Mas o tempo que o whisper da para a
        # primeira e a ultima palavra e impreciso em algumas decimas, entao nao se pode
        # exigir silencio no frame exato: procura-se a PAUSA que termina logo antes do
        # bloco e a que comeca logo depois, com tolerancia. Sem as duas, o corte e
        # recusado, porque a borda cairia dentro de fala e a emenda quebraria (no 05
        # isso deixou "tiras na vida", que era o meio de "tirando quem ja construiu um
        # funil de vendas na vida").
        # o bloco JA nasce cercado de pausa, entao a borda so recebe a guarda
        c0 = max(0.0, b0 - PAUSA_MIN + A.guarda_depois)
        c1 = min(b1 + PAUSA_MIN - A.guarda_antes, limite_t)
        if c1 - c0 < 0.4:
            recusados_conteudo.append((round(b0, 2), round(b1, 2), c.get('tipo', ''),
                                       'sobrou menos de 0,4s depois das guardas'))
            continue
        # TRAVA DE EXAGERO: nunca cortar muito mais do que o editor pediu
        pedido = y - x
        if (c1 - c0) > pedido * 1.35 + 1.5:
            recusados_conteudo.append((round(c0, 2), round(c1, 2), c.get('tipo', ''),
                                       f'bloco de {c1-c0:.1f}s para um pedido de {pedido:.1f}s'))
            continue
        conteudo.append((round(c0, 3), round(c1, 3), c.get('tipo', ''), c.get('texto', '')[:60]))

todos = sorted([(x, y) for x, y in silencio] + [(x, y) for x, y, _, _ in conteudo])
juntos = []
for x, y in todos:
    if juntos and x <= juntos[-1][1] + 0.02:
        juntos[-1][1] = max(juntos[-1][1], y)
    else:
        juntos.append([x, y])

keeps, cur = [], 0.0
for x, y in juntos:
    if x > cur:
        keeps.append((round(cur, 3), round(x, 3)))
    cur = y
if cur < DUR:
    keeps.append((round(cur, 3), round(DUR, 3)))
keeps = [(x, y) for x, y in keeps if y - x > 0.05]

rem_s = sum(y - x for x, y in silencio)
rem_c = sum(y - x for x, y, _, _ in conteudo)
print(f'palavras: {len(pal)}   pausas recusadas pelas guardas: {len(recusados)}')
print(f'silencio cortado: {len(silencio)} trechos, {rem_s:.1f}s')
print(f'conteudo cortado: {len(conteudo)} trechos, {rem_c:.1f}s')
print(f'conteudo RECUSADO por nao pousar em pausa: {len(recusados_conteudo)}')
for r in recusados_conteudo:
    print(f'   {r[0]:.2f}-{r[1]:.2f} {r[2]}: {r[3]}')
print(f'antes {DUR:.1f}s  ->  depois {DUR-rem_s-rem_c:.1f}s  ({(DUR-rem_s-rem_c)/60:.1f} min)')

if A.plano:
    json.dump({'silencio': silencio, 'conteudo': conteudo, 'keeps': keeps,
               'dur': DUR, 'recusados': recusados,
               'recusados_conteudo': recusados_conteudo}, open(A.plano, 'w'))

v = ''.join(f'[0:v]trim={x}:{y},setpts=PTS-STARTPTS[v{i}];'
            f'[0:a]atrim={x}:{y},asetpts=PTS-STARTPTS[a{i}];'
            for i, (x, y) in enumerate(keeps))
cc = ''.join(f'[v{i}][a{i}]' for i in range(len(keeps))) + f'concat=n={len(keeps)}:v=1:a=1[vo][ao]'
f = tempfile.mktemp(suffix='.txt')
open(f, 'w').write(v + cc)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', A.entrada, '-filter_complex_script', f,
                '-map', '[vo]', '-map', '[ao]', '-c:v', 'libx264', '-preset', 'medium',
                '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30',
                '-c:a', 'aac', '-b:a', '192k', A.saida], check=True)
os.unlink(f)
print('escrito:', A.saida)
