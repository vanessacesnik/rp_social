#!/usr/bin/env python3
"""
emenda_encerramento.py video.mp4 [--cauda 10] [--saida arquivo.mp4]

Tira o PRETO que fica entre o fim do conteúdo e a arte de encerramento.

POR QUE (05/08/2026). O Chefe assistiu o 07 e disse que "o final trava meio estranho,
faltou a imagem do fim". A arte estava lá e o arquivo estava tecnicamente limpo (30
quadros por segundo constantes, zero salto de tempo). O que existe é outra coisa: a
última cena do HyperFrames termina com fade, então os últimos quadros antes do card são
quase pretos. O conteúdo apaga, fica um instante de nada, e só então entra a arte. Isso
lê como travada, principalmente depois do corte fino, que deixou o vídeo mais rápido e
fez o buraco parecer maior.

O CONSERTO não é devolver o pedaço cortado, é tirar o preto: o card entra enquanto ainda
há imagem na tela. O programa mede o brilho médio dos quadros que antecedem o card,
acha onde o fade começa a cair abaixo de 80% do brilho de regime, e remove daquele ponto
até o card.

Preserva a arte de encerramento inteira e não toca no áudio do conteúdo, porque o fade
de vídeo não tem correspondente no áudio (a fala já terminou antes).
"""
import argparse, os, subprocess, tempfile
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('video')
ap.add_argument('--cauda', type=float, default=10.0)
ap.add_argument('--saida', default=None)
ap.add_argument('--queda', type=float, default=0.80, help='fracao do brilho de regime')
A = ap.parse_args()


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)


def brilho(p, t):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', p, '-frames:v', '1',
                        '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True)
    a = np.frombuffer(r.stdout, dtype=np.uint8)
    return float(a.mean()) if len(a) else 0.0


D = dur(A.video)
card = D - A.cauda

# brilho de regime: media dos quadros de 3 a 1,5s antes do card
regime = np.mean([brilho(A.video, card - t) for t in (3.0, 2.5, 2.0, 1.5)])
alvo = regime * A.queda

# anda para tras a partir do card ate achar quadro acima do alvo
corte = card
t = card - 0.033
while t > card - 2.5:
    if brilho(A.video, t) >= alvo:
        corte = t + 0.033
        break
    t -= 0.033

preto = card - corte
print(f'brilho de regime {regime:.0f}  ·  alvo {alvo:.0f}')
print(f'preto antes do card: {preto:.2f}s  (de {corte:.2f} a {card:.2f})')

if preto < 0.08:
    print('nada a tirar, o card ja entra com imagem na tela')
    raise SystemExit(0)

saida = A.saida or (os.path.splitext(A.video)[0] + '_emendado.mp4')
f = tempfile.mktemp(suffix='.txt')
open(f, 'w').write(
    f'[0:v]trim=0:{corte:.3f},setpts=PTS-STARTPTS[v0];'
    f'[0:a]atrim=0:{corte:.3f},asetpts=PTS-STARTPTS[a0];'
    f'[0:v]trim={card:.3f}:{D:.3f},setpts=PTS-STARTPTS[v1];'
    f'[0:a]atrim={card:.3f}:{D:.3f},asetpts=PTS-STARTPTS[a1];'
    f'[v0][a0][v1][a1]concat=n=2:v=1:a=1[vo][ao]')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', A.video, '-filter_complex_script', f,
                '-map', '[vo]', '-map', '[ao]', '-c:v', 'libx264', '-preset', 'medium',
                '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', saida], check=True)
os.unlink(f)
print(f'escrito: {saida}   ({D:.2f}s -> {dur(saida):.2f}s)')
