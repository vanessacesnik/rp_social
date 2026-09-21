#!/usr/bin/env python3
"""
audita_2s.py - prova que a tela nunca passa 2 segundos sem movimento.

Amostra so o PAINEL da apresentacao (nao a coluna da gravacao, que se move sozinha)
a 2 quadros por segundo, compara cada amostra com a anterior e acusa qualquer janela
de 2 segundos ou mais sem movimento perceptivel, com o tempo exato.

Uso:  python3 audita_2s.py <video.mp4> [painel_w painel_h painel_x painel_y]
      padrao do modelo YouTube 1: 1252 1016 32 32
"""
import subprocess, numpy as np, os, glob, shutil, sys
from PIL import Image

V = sys.argv[1]
W,H,X,Y = (int(a) for a in (sys.argv[2:6] if len(sys.argv)>=6 else (1252,1016,32,32)))
D = '/tmp/audita2s_frames'
shutil.rmtree(D, ignore_errors=True); os.makedirs(D)

subprocess.run(['ffmpeg','-y','-v','error','-i',V,
  '-vf', f'crop={W}:{H}:{X}:{Y},fps=2,scale=313:254', '-q:v','3', f'{D}/f%05d.jpg'], check=True)

fs = sorted(glob.glob(f'{D}/*.jpg'))
print('amostras:', len(fs), '(2 fps)   duracao: %.1fs' % (len(fs)/2))

prev=None; parado=0; gaps=[]
for i,f in enumerate(fs):
    a = np.asarray(Image.open(f).convert('L'), dtype=np.int16)
    if prev is not None:
        frac = float((np.abs(a-prev) > 8).mean())     # fracao de pixels que mudaram
        if frac < 0.0004:
            parado += 1
        else:
            if parado >= 4: gaps.append(((i-parado)/2.0, parado/2.0))
            parado = 0
    prev = a
if parado >= 4: gaps.append(((len(fs)-parado)/2.0, parado/2.0))

if gaps:
    print('REPROVADO - %d janelas de 2s ou mais sem movimento no painel:' % len(gaps))
    for t,d in gaps: print('   t=%.1fs parado por %.1fs' % (t,d))
    sys.exit(1)
print('APROVADO - nenhuma janela de 2s sem movimento no painel, nos %.1fs' % (len(fs)/2))
