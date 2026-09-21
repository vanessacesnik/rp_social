#!/usr/bin/env python3
"""
prova_emendas.py cortado.mp4 plano.json saida.txt

Prova que cada EMENDA do corte ficou natural, ouvindo o arquivo final.

POR QUE. A prova geométrica garante uma coisa só: que nenhum corte encostou em som,
ou seja, que nenhuma palavra foi partida. Ela não diz nada sobre o SENTIDO. Depois de
tirar frase inteira, o risco deixa de ser a palavra picotada e passa a ser o salto de
raciocínio: duas metades que não conversam, ou a mesma palavra colada em si mesma.

COMO PROVA. Calcula onde cada corte caiu no arquivo NOVO (a soma dos pedaços que
ficaram antes dele), recorta oito segundos em volta de cada emenda e transcreve esse
pedaço isolado. O texto que sai é a costura como o espectador vai ouvir. Sai também a
duração do vão, para pegar emenda com respiro curto demais.

O que reprova, e precisa de olho humano na lista:
  · palavra repetida em cima da emenda ("o site o site")
  · frase que muda de assunto sem conectivo
  · emenda dentro de uma palavra que o corte geométrico não pegou por arredondamento
"""
import argparse, json, os, re, subprocess, tempfile

ap = argparse.ArgumentParser()
ap.add_argument('cortado'); ap.add_argument('plano'); ap.add_argument('saida')
ap.add_argument('--janela', type=float, default=4.0)
ap.add_argument('--modelo', default=os.path.expanduser(
    '~/.local/share/whisper-models/ggml-large-v3-turbo-q5_0.bin'))
A = ap.parse_args()

p = json.load(open(A.plano))
keeps = p['keeps']
cortes = sorted([tuple(x[:2]) for x in p['silencio']] + [tuple(x[:2]) for x in p['conteudo']])
tipo = {}
for x in p['conteudo']:
    tipo[round(x[0], 2)] = x[2] if len(x) > 2 else 'CONTEUDO'

# posicao de cada emenda no arquivo NOVO
acum, emendas = 0.0, []
for i, (a, b) in enumerate(keeps):
    acum += b - a
    if i < len(keeps) - 1:
        vao = cortes[i][1] - cortes[i][0] if i < len(cortes) else 0
        emendas.append((round(acum, 2), round(keeps[i][1], 2), round(keeps[i + 1][0], 2)))

# so as emendas de CONTEUDO e as de silencio grande merecem transcricao
alvo = [e for e in emendas if (e[2] - e[1]) >= 1.2]
L = [f'# PROVA DE EMENDA · {os.path.basename(A.cortado)}',
     f'# {len(emendas)} emendas no total, {len(alvo)} com vao de 1,2s ou mais (transcritas)',
     '# formato: [tempo no arquivo NOVO] vao removido · o que se ouve em volta', '']
for t, x, y in alvo:
    ini = max(0.0, t - A.janela)
    wav = tempfile.mktemp(suffix='.wav')
    out = tempfile.mktemp()
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{ini:.2f}', '-i', A.cortado,
                    '-t', f'{A.janela*2:.2f}', '-ac', '1', '-ar', '16000', wav], check=True)
    subprocess.run(['whisper-cli', '-m', A.modelo, '-l', 'pt', '-oj', '-of', out, '-f', wav],
                   capture_output=True)
    txt = ''
    if os.path.exists(out + '.json'):
        d = json.load(open(out + '.json'))
        txt = ' '.join(s['text'].strip() for s in d['transcription']).strip()
        os.unlink(out + '.json')
    os.unlink(wav)
    # repeticao colada na emenda: mesma palavra duas vezes seguidas
    pl = [w.lower() for w in re.findall(r'\w+', txt)]
    dobra = [pl[i] for i in range(len(pl) - 1) if pl[i] == pl[i + 1] and len(pl[i]) > 2]
    marca = f'   <<< PALAVRA DOBRADA: {dobra}' if dobra else ''
    L.append(f'[{t:7.2f}] tirou {y-x:5.2f}s ({x:.2f} a {y:.2f} do original){marca}')
    L.append(f'          "{txt}"')
    L.append('')

open(A.saida, 'w', encoding='utf-8').write('\n'.join(L))
print(f'{len(emendas)} emendas, {len(alvo)} transcritas para conferencia')
print(f'palavra dobrada em cima da emenda: '
      f'{sum(1 for l in L if "PALAVRA DOBRADA" in l)} caso(s)')
print('escrito:', A.saida)
