#!/usr/bin/env python3
"""
insere_cta.py video.mp4 cta.mp4 saida.mp4 [--cauda 10] [--margem 90] [--janela 75]

Enfia o CTA no MEIO de um vídeo pronto, num ponto que não parte um raciocínio.

POR QUE ISTO NÃO É "CORTAR NUMA PAUSA" (05/08/2026). A primeira versão escolhia a pausa
de áudio mais próxima do meio, e no vídeo 07 ela caiu em 216,78s, dentro da frase: o
vídeo dizia "só que aí, na semana seguinte" e o CTA entrava ali, no respiro entre o
adjunto e o verbo. Depois do corte fino todas as pausas ficaram curtas e parecidas, então
DURAÇÃO DE SILÊNCIO NÃO DISTINGUE respiro de fim de frase. Quem distingue é o texto.

COMO ESCOLHE, nesta ordem:
  1. transcreve a faixa em volta do meio e recolhe os FINS DE FRASE, que são os fins de
     segmento terminados em ponto, interrogação ou exclamação;
  2. mede o silêncio de verdade pela energia do áudio, a 10ms;
  3. cruza os dois: um candidato é um silêncio que encosta num fim de frase;
  4. entre os candidatos ganha o mais perto do meio, com um bônus pequeno para o silêncio
     mais largo (a distância vale mais que a largura, ao contrário da primeira versão).

Se o cruzamento não achar nada, o programa PARA em vez de cair no critério antigo: entrar
no lugar errado é pior que não entrar, e a mensagem diz exatamente o que faltou.

REGRAS DO PONTO
  · nunca nos primeiros `margem` segundos: quem chegou agora ainda está decidindo ficar.
  · nunca nos últimos `margem` segundos nem dentro da arte de encerramento.

O corte é seco, no fundo do silêncio, e o áudio recebe 40ms de rampa dos dois lados de
cada emenda, para o caso em que a pausa ainda carrega uma respiração.
"""
import argparse, json, os, re, subprocess, tempfile
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('video'); ap.add_argument('cta'); ap.add_argument('saida')
ap.add_argument('--cauda', type=float, default=10.0, help='arte de encerramento, intocavel')
ap.add_argument('--margem', type=float, default=90.0, help='zona morta no comeco e no fim')
ap.add_argument('--janela', type=float, default=110.0, help='faixa transcrita em volta do meio')
ap.add_argument('--piso', type=float, default=-45.0, help='dB abaixo do qual e silencio')
ap.add_argument('--min', type=float, default=0.22, help='silencio minimo aceitavel')
ap.add_argument('--modelo', default=os.path.expanduser(
    '~/.local/share/whisper-models/ggml-large-v3-turbo-q5_0.bin'))
A = ap.parse_args()

HOP = 0.010
SR = 16000


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)


D = dur(A.video)
DC = dur(A.cta)
meio = D / 2

# ---------- 1. fins de frase em volta do meio ----------
ini_j = max(A.margem, meio - A.janela)
fim_j = min(D - A.cauda - A.margem, meio + A.janela)
wav = tempfile.mktemp(suffix='.wav')
out = tempfile.mktemp()
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{ini_j:.2f}', '-i', A.video,
                '-t', f'{fim_j-ini_j:.2f}', '-ac', '1', '-ar', str(SR), wav], check=True)
# PALAVRA A PALAVRA, nao segmento. O segmento do whisper e longo e quase nunca termina
# em pontuacao: no 07 foram 14 segmentos e UM so terminava frase, e esse um era uma
# pergunta retorica ("por que gente?") seguida da resposta, o pior lugar para interromper.
# Com `-ml 1` a pontuacao vem colada na palavra e o fim de frase fica no tempo exato.
subprocess.run(['whisper-cli', '-m', A.modelo, '-l', 'pt', '-ml', '1', '-oj', '-of', out,
                '-f', wav], capture_output=True)
segs = json.load(open(out + '.json'))['transcription']
os.unlink(out + '.json')
os.unlink(wav)

brutas = [(x['text'], x['offsets']['from'] / 1000, x['offsets']['to'] / 1000)
          for x in segs if x['text'].strip()]
pal = []
for t, x, y in brutas:
    if pal and not t.startswith(' '):
        pal[-1] = (pal[-1][0] + t.strip(), pal[-1][1], y)
    else:
        pal.append((t.strip(), x, y))

# PONTO FINAL VALE MAIS QUE INTERROGACAO. Uma pergunta quase sempre e seguida da propria
# resposta, entao interromper ali deixa a pergunta pendurada. O ponto ganha bonus.
frases = []
for i, (t, x, y) in enumerate(pal):
    if not t or t[-1] not in '.!?' or i + 1 >= len(pal):
        continue
    ctx = ' '.join(w for w, _, _ in pal[max(0, i - 9):i + 1])
    # O VAO, nao o instante. O silencio que interessa e o que fica ENTRE a palavra que
    # fecha a frase e a que abre a proxima. Ancorar so no fim da palavra deixava o
    # casamento pegar o silencio ANTERIOR a ela, porque o whisper adianta o fim: no 07
    # o retorno vinha com um "Certo?" solto, que era a ultima palavra da frase anterior.
    frases.append((ini_j + y, ini_j + pal[i + 1][1], ctx, 0.0 if t[-1] == '.' else 6.0))
print(f'{len(pal)} palavras transcritas entre {ini_j:.0f}s e {fim_j:.0f}s, '
      f'{len(frases)} fins de frase ({sum(1 for f in frases if f[2] == 0)} com ponto final)')

# ---------- 2. silencio medido ----------
raw = tempfile.mktemp(suffix='.raw')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', A.video, '-ac', '1', '-ar', str(SR),
                '-f', 's16le', raw], check=True)
a = np.fromfile(raw, dtype=np.int16).astype(np.float32) / 32768
os.unlink(raw)
w = int(SR * HOP)
n = len(a) // w
db = 20 * np.log10(np.sqrt(np.maximum((a[:n * w].reshape(n, w) ** 2).mean(1), 1e-12)))
q = db < A.piso
d = np.diff(np.concatenate(([0], q.view(np.int8), [0])))
blocos = [(i0 * HOP, i1 * HOP) for i0, i1 in zip(np.where(d == 1)[0], np.where(d == -1)[0])
          if i1 * HOP - i0 * HOP >= A.min]

# ---------- 3. cruzamento ----------
cand = []
for tf0, tf1, txt, pena in frases:
    for x, y in blocos:
        # O bloco de silencio tem que COMECAR depois que a frase fechou e ANTES de a
        # proxima abrir. Isso sozinho descarta o respiro que existe no meio da frase e o
        # silencio anterior a ultima palavra, que era o defeito da versao passada.
        if not (tf0 - 0.20 <= x <= tf1 + 0.20):
            continue
        # corte no FIM do silencio, 60ms antes de a fala voltar: tudo que veio antes fica
        # garantidamente na primeira metade.
        t = y - 0.06
        if not (A.margem <= t <= D - A.cauda - A.margem):
            continue
        cand.append((abs(t - meio) - 2.0 * (y - x) + pena, t, y - x, txt[-70:]))
        break
if not cand:
    raise SystemExit(
        f'ERRO: nenhum fim de frase coincide com silencio entre {A.margem:.0f}s e '
        f'{D-A.cauda-A.margem:.0f}s. Aumente --janela ou baixe --min.')
cand.sort()
_, corte, larg, frase = cand[0]

print(f'video {D:.2f}s  ·  meio em {meio:.2f}s  ·  {len(cand)} fins de frase com silencio')
print(f'entrada: {corte:.2f}s  ({abs(corte-meio):.1f}s do meio, silencio de {larg:.2f}s)')
print(f'   ultima frase antes do CTA: "{frase}"')
print(f'CTA de {DC:.2f}s  ->  saida de {D+DC:.2f}s')

f = tempfile.mktemp(suffix='.txt')
open(f, 'w').write(
    f'[0:v]trim=0:{corte:.3f},setpts=PTS-STARTPTS[v0];'
    f'[0:a]atrim=0:{corte:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={max(0,corte-0.04):.3f}:d=0.04[a0];'
    f'[1:v]setpts=PTS-STARTPTS[v1];'
    f'[1:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st={max(0,DC-0.04):.3f}:d=0.04[a1];'
    f'[0:v]trim={corte:.3f}:{D:.3f},setpts=PTS-STARTPTS[v2];'
    f'[0:a]atrim={corte:.3f}:{D:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.04[a2];'
    f'[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[vo][ao]')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', A.video, '-i', A.cta,
                '-filter_complex_script', f, '-map', '[vo]', '-map', '[ao]',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
                A.saida], check=True)
os.unlink(f)

DS = dur(A.saida)
print(f'escrito: {A.saida}   {DS:.2f}s  (esperado {D+DC:.2f}s, diferenca {DS-D-DC:+.2f}s)')
print(f'ENTRADA_CTA={corte:.2f}  SAIDA_CTA={corte+DC:.2f}')
