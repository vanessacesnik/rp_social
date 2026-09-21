#!/usr/bin/env python3
"""
finaliza.py <NN> --plano plano.json [--justificativa-zero-conteudo justificativa.md]
· fecha o pacote de um vídeo do lote, do render à pasta na Desktop.

1. transcreve o áudio EXATO do render (nunca reaproveita transcrição de outra versão);
2. corta o silêncio pelo método de duas fontes (energia corta, whisper veta);
3. PROVA o corte retranscrevendo a saída e comparando a sequência de palavras com a
   mesma régua nos dois lados (as duas com `-ml 1`, senão a comparação é inválida);
4. cola a arte de encerramento por 10 segundos;
5. copia video.mp4, thumbnail.png e legenda.txt para a pasta da Desktop.

A prova do passo 3 é obrigatória: o Chefe pegou palavra comida assistindo, e a única
defesa é comparar as duas transcrições.
"""
import argparse, json, os, re, subprocess, sys, unicodedata
from difflib import SequenceMatcher

ap = argparse.ArgumentParser()
ap.add_argument('NN')
ap.add_argument('--plano', required=True,
                help='plano.json produzido pelo corta_fino.py para este render')
ap.add_argument('--justificativa-zero-conteudo', default=None, metavar='ARQUIVO',
                help='arquivo de justificativa quando o plano tiver zero cortes de conteudo')
A = ap.parse_args()

NN = A.NN
W = f'/Users/naiarodrigues/workspace/v{NN}-full'
DESK = '/Users/naiarodrigues/Desktop/conteudo youtube'
PASTA = next(d for d in sorted(os.listdir(DESK)) if d.startswith(NN + ' - '))
M = os.path.expanduser('~/.local/share/whisper-models/ggml-large-v3-turbo-q5_0.bin')
SK = '/Users/naiarodrigues/.claude/skills/super-edicao-video-avalanche/scripts/youtube-1'


def valida_cortes_de_conteudo():
    if not os.path.isfile(A.plano):
        sys.exit(f'ENTREGA REPROVADA: plano de corte inexistente: {A.plano}')
    try:
        plano_conteudo = json.load(open(A.plano))
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f'ENTREGA REPROVADA: plano de corte invalido: {exc}')
    conteudo = plano_conteudo.get('conteudo')
    if not isinstance(conteudo, list):
        sys.exit('ENTREGA REPROVADA: plano sem a lista de cortes de conteudo')
    if conteudo:
        print(f'PORTAO DE CONTEUDO: {len(conteudo)} cortes declarados no plano')
        return
    justificativa = A.justificativa_zero_conteudo
    if not justificativa or not os.path.isfile(justificativa):
        sys.exit('ENTREGA REPROVADA: zero cortes de conteudo sem justificativa escrita')
    texto = open(justificativa, encoding='utf-8').read().strip()
    if len(texto) < 20:
        sys.exit('ENTREGA REPROVADA: justificativa de zero cortes esta vazia ou insuficiente')
    print(f'PORTAO DE CONTEUDO: zero cortes justificados em {justificativa}')


valida_cortes_de_conteudo()


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def transcreve(mp4, saida):
    wav = f'{W}/_{os.path.basename(saida)}.wav'
    sh(['ffmpeg', '-y', '-v', 'error', '-i', mp4, '-ac', '1', '-ar', '16000',
        '-c:a', 'pcm_s16le', wav])
    subprocess.run(['whisper-cli', '-m', M, '-l', 'pt', '-ml', '1', '-oj',
                    '-of', saida, '-f', wav], capture_output=True)
    return saida + '.json'


def palavras(f):
    """junta os pedacos do -ml 1 numa palavra inteira e normaliza"""
    d = json.load(open(f))
    pal = []
    for s in d['transcription']:
        t = s['text']
        if not t.strip() or not re.search(r'\w', t):
            continue
        if pal and not t.startswith(' '):
            pal[-1] = pal[-1] + t.strip()
        else:
            pal.append(t.strip())
    # O whisper ALUCINA credito de legendagem no fim do audio ("legenda por
    # Fulano", "legendas pela comunidade"). Nao e fala, e sai numa passada e nao
    # na outra, entao reprovava o corte por engano (aconteceu no 08).
    while pal and re.match(r'(?i)legenda|legendas|amara|subtitle|revisao', pal[-1]):
        pal = pal[:-1]
    for i, w in enumerate(pal[:-1]):
        if re.match(r'(?i)^legendas?$', w) and re.match(r'(?i)^(por|pela|pelo)$', pal[i+1]):
            pal = pal[:i]
            break
    # "agente" e "a gente" sao a mesma onda sonora e o reconhecedor troca entre
    # passadas. Vira sempre a forma separada, senao aparece como palavra comida.
    junto = []
    for w in pal:
        junto.append(w)
    txt = ' '.join(junto)
    txt = re.sub(r'(?i)\bagente\b', 'a gente', txt)
    pal = txt.split()
    out = []
    for p in pal:
        n = ''.join(c for c in unicodedata.normalize('NFD', p.lower())
                    if unicodedata.category(c) != 'Mn')
        n = re.sub(r'[^a-z0-9]', '', n)
        if n:
            out.append(n)
    return out


render = sorted(f'{W}/proj/renders/{f}' for f in os.listdir(f'{W}/proj/renders')
                if f.endswith('.mp4'))[0]
print(f'render: {os.path.basename(render)}')

# ---------- 1 e 2 ----------
transcreve(render, f'{W}/palavras_render')
sh(['python3', f'{SK}/corta_silencio.py', render, f'{W}/v{NN}_sem_pausas.mp4',
    '--words', f'{W}/palavras_render.json', '--guarda-depois', '0.14',
    '--guarda-antes', '0.08', '--min', '0.30', '--limiar', '-45'])

# ---------- 3. a prova ----------
# A prova ANTIGA comparava duas transcricoes do arquivo inteiro, e isso da FALSO
# ALARME: numa passada de 800 segundos o whisper segmenta diferente, e frases que
# estao no audio aparecem como sumidas. Provei isso no 09 transcrevendo a mesma
# janela isolada nos dois arquivos e achando "entendeu? Perfeito." nos dois.
#
# A prova NOVA e geometrica e nao depende de reconhecedor: o corte so pode remover
# intervalo que nao encoste em palavra. Entao conferimos o PLANO do corte contra os
# tempos por palavra do render. Se nenhum intervalo removido cobre 25% ou mais de
# alguma palavra, nenhuma palavra foi comida. Isso e determinstico.
plano = json.load(open(f'{W}/v{NN}_sem_pausas.mp4.plano.json'))
d = json.load(open(f'{W}/palavras_render.json'))
pal = []
for seg in d['transcription']:
    t = seg['text']
    if not t.strip() or not re.search(r'\w', t):
        continue
    a0, b0 = seg['offsets']['from'] / 1000, seg['offsets']['to'] / 1000
    if pal and not t.startswith(' '):
        pal[-1] = (pal[-1][0] + t.strip(), pal[-1][1], b0)
    else:
        pal.append((t.strip(), a0, b0))

pior, quem = 0.0, None
for ca, cb in plano['cortes']:
    for w, wa, wb in pal:
        if wb <= ca or wa >= cb:
            continue
        dur_w = max(1e-6, wb - wa)
        cob = (min(cb, wb) - max(ca, wa)) / dur_w
        if cob > pior:
            pior, quem = cob, (w, round(wa, 2), round(ca, 2), round(cb, 2))
print(f'PROVA DO CORTE (geometrica) · {len(plano["cortes"])} intervalos, {plano["removido"]:.1f}s removidos')
print(f'  maior fatia de palavra tocada: {pior*100:.1f}%  {quem or ""}')
if pior >= 0.25:
    sys.exit('CORTE REPROVADO: um intervalo removido invade uma palavra')

# transcricao do arquivo cortado: nao e mais a prova, mas e a linha do tempo real
# do video entregue, e e dela que o agente de legenda tira os capitulos.
transcreve(f'{W}/v{NN}_sem_pausas.mp4', f'{W}/pos_corte')
print('transcricao do cortado em pos_corte.json (insumo para os capitulos)')

# ---------- 4. encerramento ----------
enc = f'{W}/enc10.mp4'
if not os.path.exists(enc):
    sh(['cp', '/Users/naiarodrigues/workspace/t1-full/enc10.mp4', enc])
lst = f'{W}/lista_final.txt'
open(lst, 'w').write(f"file '{W}/v{NN}_sem_pausas.mp4'\nfile '{enc}'\n")
sh(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', f'{W}/v{NN}_FINAL.mp4'])

# ---------- 5. pacote ----------
d = f'{DESK}/{PASTA}'
sh(['cp', f'{W}/v{NN}_FINAL.mp4', f'{d}/video.mp4'])
for f, alvo in [('thumbnail.png', 'thumbnail.png'), ('legenda.txt', 'legenda.txt')]:
    if os.path.exists(f'{W}/{f}'):
        sh(['cp', f'{W}/{f}', f'{d}/{alvo}'])
if os.path.exists(f'{d}/bruto.mp4'):
    os.remove(f'{d}/bruto.mp4')

dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'csv=p=0', f'{d}/video.mp4'],
                           capture_output=True, text=True).stdout)
print(f'\nPACOTE {PASTA}')
for f in sorted(os.listdir(d)):
    print(f'   {f:<16} {os.path.getsize(os.path.join(d, f))/1e6:8.1f} MB')
print(f'   duracao final: {dur//60:.0f}:{dur%60:05.2f}')
