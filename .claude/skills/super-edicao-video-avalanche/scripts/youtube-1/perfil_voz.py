#!/usr/bin/env python3
"""
perfil_voz.py video.mp4 palavras.json saida.json [--cauda 10]

Separa a voz do Chefe da voz de OUTRAS PESSOAS na chamada, por timbre e não por volume.

POR QUE (05/08/2026). A live inteira foi um Zoom com outras pessoas. O primeiro método
marcava "invasão" por nível de áudio, e isso confunde duas coisas diferentes: ele
falando baixo, e outra pessoa entrando. Ordem do Chefe: "vc deve sim identificar essas
invasões mas sem cortar falas minhas importantes".

COMO SEPARA. Para cada fala mede três coisas que dependem de QUEM fala, não de quão
alto:
  f0        altura da voz (frequência fundamental, por autocorrelação)
  centroide onde a energia do espectro se concentra (timbre claro ou escuro)
  rolloff   até onde o espectro vai antes de morrer

A voz dele é a MODA: ele fala a maior parte do tempo. O perfil dele sai da mediana
dessas três medidas ponderada pela duração. Cada fala recebe uma distância até esse
perfil, normalizada pela dispersão das próprias falas dele.

O QUE ENTREGA. Um JSON com, por fala, o tempo, o texto, as medidas, a distância e o
veredito `dele` ou `outra_voz`. Quem decide o que fazer com isso é o editor: pergunta
de aluno que ele responde em seguida FICA (senão a resposta fica sem pergunta), e
vazamento sem relação com a aula SAI, junto com a espera dele até mutar.
"""
import argparse, json, os, re, subprocess, tempfile
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('video'); ap.add_argument('words'); ap.add_argument('saida')
ap.add_argument('--cauda', type=float, default=10.0)
ap.add_argument('--pausa', type=float, default=0.6)
A = ap.parse_args()

SR = 16000
raw = tempfile.mktemp(suffix='.raw')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', A.video,
                '-ac', '1', '-ar', str(SR), '-f', 's16le', raw], check=True)
a = np.fromfile(raw, dtype=np.int16).astype(np.float32) / 32768
os.unlink(raw)
DUR = len(a) / SR

d = json.load(open(A.words))
brutas = [(s['text'], s['offsets']['from'] / 1000, s['offsets']['to'] / 1000)
          for s in d['transcription'] if s['text'].strip() and re.search(r'\w', s['text'])]
pal = []
for w, x, y in brutas:
    if pal and not w.startswith(' '):
        pal[-1] = (pal[-1][0] + w.strip(), pal[-1][1], y)
    else:
        pal.append((w.strip(), x, y))

falas, cur, ini = [], [], pal[0][1]
for i, (w, x, y) in enumerate(pal):
    cur.append(w)
    prox = pal[i + 1][1] if i + 1 < len(pal) else DUR
    if prox - y >= A.pausa or len(cur) >= 26:
        falas.append([ini, y, ' '.join(cur), round(prox - y, 2)])
        cur = []
        ini = prox
if cur:
    falas.append([ini, pal[-1][2], ' '.join(cur), 0.0])


def medidas(x, y):
    """f0 mediana, centroide e rolloff das janelas com voz"""
    s = a[int(x * SR):int(y * SR)]
    if len(s) < SR // 4:
        return None
    W = int(0.040 * SR)                     # 40ms
    H = int(0.020 * SR)
    f0s, cents, rolls = [], [], []
    jan = np.hanning(W)
    for i in range(0, len(s) - W, H):
        seg = s[i:i + W]
        if np.sqrt((seg ** 2).mean()) < 10 ** (-45 / 20):
            continue
        seg = seg * jan
        # f0 por autocorrelacao, faixa de voz humana 70 a 320 Hz
        ac = np.correlate(seg, seg, 'full')[W - 1:]
        lo, hi = SR // 320, SR // 70
        if hi >= len(ac):
            continue
        pico = lo + int(np.argmax(ac[lo:hi]))
        if ac[pico] > 0.30 * ac[0]:
            f0s.append(SR / pico)
        # espectro
        mag = np.abs(np.fft.rfft(seg))
        frq = np.fft.rfftfreq(W, 1 / SR)
        tot = mag.sum()
        if tot > 0:
            cents.append(float((mag * frq).sum() / tot))
            acum = np.cumsum(mag)
            rolls.append(float(frq[int(np.searchsorted(acum, 0.85 * tot))]))
    if len(cents) < 5:
        return None
    return (float(np.median(f0s)) if len(f0s) >= 3 else float('nan'),
            float(np.median(cents)), float(np.median(rolls)))


for f in falas:
    m = medidas(f[0], f[1])
    f.append(m)

val = [(f, f[4]) for f in falas if f[4] and not np.isnan(f[4][0]) and f[1] < DUR - A.cauda]
if not val:
    raise SystemExit('ERRO: nenhuma fala mensuravel')

# perfil DELE: mediana ponderada pela duracao (ele fala a maior parte do tempo)
peso = np.array([f[1] - f[0] for f, _ in val])
M = np.array([m for _, m in val])
ordem = np.argsort(M[:, 0])
acum = np.cumsum(peso[ordem])
perfil = np.array([M[ordem][np.searchsorted(acum, acum[-1] / 2)][0],
                   np.median(M[:, 1]), np.median(M[:, 2])])
# dispersao robusta
disp = np.array([np.median(np.abs(M[:, i] - perfil[i])) * 1.4826 or 1.0 for i in range(3)])
disp = np.maximum(disp, [6.0, 120.0, 200.0])       # piso, senao ruido vira sinal

# DURACAO MINIMA PARA CLASSIFICAR. Fragmento curto nao tem ciclos suficientes para
# medir altura de voz, e vira falso positivo: no 05 apareceram "Sim sim" e "RD Station"
# marcados como outra pessoa, que sao ele. Abaixo de 1,5s o veredito e 'indefinido' e
# o editor decide pelo texto, nunca pelo numero.
MIN_CLASSIFICAR = 1.5
for f in falas:
    if not f[4] or np.isnan(f[4][0]) or (f[1] - f[0]) < MIN_CLASSIFICAR:
        f.append(None)
        f.append('curto_demais' if f[4] else 'indefinido')
        continue
    z = np.abs(np.array(f[4]) - perfil) / disp
    dist = float(np.sqrt((z ** 2).mean()))
    f.append(round(dist, 2))
    f.append('outra_voz' if dist >= 2.2 else 'dele')

out = [{'ini': round(f[0], 2), 'fim': round(f[1], 2), 'texto': f[2], 'pausa_depois': f[3],
        'f0': None if not f[4] else round(f[4][0], 1),
        'centroide': None if not f[4] else round(f[4][1]),
        'rolloff': None if not f[4] else round(f[4][2]),
        'distancia': f[5], 'quem': f[6]}
       for f in falas if f[1] < DUR - A.cauda]
json.dump({'perfil_dele': {'f0': round(perfil[0], 1), 'centroide': round(perfil[1]),
                           'rolloff': round(perfil[2])},
           'dispersao': [round(x, 1) for x in disp], 'falas': out},
          open(A.saida, 'w'), ensure_ascii=False, indent=1)

n_out = sum(1 for o in out if o['quem'] == 'outra_voz')
print(f'perfil dele: f0 {perfil[0]:.0f} Hz  centroide {perfil[1]:.0f} Hz  rolloff {perfil[2]:.0f} Hz')
print(f'{len(out)} falas  ·  {n_out} classificadas como OUTRA VOZ  ·  {len(out)-n_out} dele')
print('(falas abaixo de 1,5s ficam como curto_demais: nao da para medir altura de voz)')
for o in out:
    if o['quem'] == 'outra_voz':
        print(f'   [{o["ini"]:7.2f}-{o["fim"]:7.2f}] d={o["distancia"]:.1f} f0={o["f0"]}  {o["texto"][:70]}')
