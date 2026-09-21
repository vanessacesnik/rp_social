#!/usr/bin/env python3
"""
acha_dispensavel.py --words palavras.json [--offset 0] [--min-seg 2.5]

Lê a transcrição com tempo por palavra e PROPÕE trechos que dá para tirar de um corte
para YouTube, em três famílias:

  REPETICAO   ele repete a mesma ideia com as mesmas palavras. Ordem do Chefe (04/08/2026):
              "eu sou muito repetitivo porque isso torna a didática melhor, mas pro corte
              falou uma vez acabou". Corta a repetição, mantém a primeira ocorrência.
  DIVAGACAO   parêntese que ele abre no meio da aula e que não pertence ao assunto:
              comer na live, comentário sobre o chat, piada solta, recado para uma
              pessoa específica, quebra da quarta parede.
  INTERACAO   pergunta ao chat que não tem resposta no vídeo, chamada de levantar a mão,
              espera por resposta. Serve na live, não serve no corte.

Não corta nada: escreve o plano em JSON e imprime o relatório para auditoria.
"""
import json, re, sys, unicodedata, argparse

ap = argparse.ArgumentParser()
ap.add_argument('--words', required=True)
ap.add_argument('--offset', type=float, default=0.0, help='subtrai dos tempos (ex: duracao do gancho)')
ap.add_argument('--min-seg', type=float, default=2.5, help='trecho menor que isso nao compensa cortar')
ap.add_argument('--out', default=None)
A = ap.parse_args()


def norm(t):
    t = unicodedata.normalize('NFD', t.lower())
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', t)


d = json.load(open(A.words))
W = []
for s in d['transcription']:
    w = s['text'].strip()
    if w and re.search(r'\w', w):
        W.append((s['text'], s['offsets']['from']/1000.0 - A.offset, s['offsets']['to']/1000.0 - A.offset))
W = [(w, a, b) for w, a, b in W if a >= 0]

# o whisper com -ml 1 quebra palavra em pedaços: o token que NAO comeca com espaco
# e continuacao do anterior. E o unico criterio confiavel: tempo colado nao serve,
# porque a fala corrida tambem vem colada.
palavras = []
for w, a, b in W:
    if palavras and not w.startswith(' '):
        p, pa, pb = palavras[-1]
        palavras[-1] = (p + w.strip(), pa, b)
    else:
        palavras.append((w.strip(), a, b))

txt = [norm(p) for p, _, _ in palavras]
cand = []

# ---------- 1. REPETICAO: n-grama que reaparece perto ----------
N = 6
vistos = {}
for i in range(len(txt) - N):
    chave = ' '.join(txt[i:i+N])
    if len(chave) < 24:
        continue
    if chave in vistos:
        j = vistos[chave]
        if 0 < palavras[i][1] - palavras[j][2] < 90:      # reaparece em ate 90s
            # estende enquanto continuar igual
            k = 0
            while i+N+k < len(txt) and j+N+k < i and txt[i+N+k] == txt[j+N+k]:
                k += 1
            ini, fim = palavras[i][1], palavras[i+N+k-1][2]
            if fim - ini >= A.min_seg:
                cand.append(dict(tipo='REPETICAO', ini=round(ini, 2), fim=round(fim, 2),
                                 dur=round(fim-ini, 2),
                                 texto=' '.join(p for p, _, _ in palavras[i:i+N+k]),
                                 motivo='ja tinha dito isso em %.1fs' % palavras[j][1]))
    else:
        vistos[chave] = i

# ---------- 2. DIVAGACAO e INTERACAO por marcador ----------
MARCAS = [
 ('DIVAGACAO', r'\b(pizza|comendo|comer|lanche|almo[cç]|jantar|cerveja|caf[eé] aqui)\b',
  'comentario sobre comer durante a live'),
 ('DIVAGACAO', r'\b(desculpa|foi mal|perd[aã]o) (a[ií]|gente|pessoal)\b', 'desculpa solta'),
 ('DIVAGACAO', r'\b(t[oô] com fome|que sem gra[cç]a|isso foi f[oô]da|nossa que)\b',
  'comentario pessoal fora do assunto'),
 ('DIVAGACAO', r'\b(errei|corta essa|corta as|esquece|recome[cç]a|deixa eu refazer|pera[ií])\b',
  'quebra da quarta parede'),
 ('INTERACAO', r'\b(levanta a m[aã]o|fala no chat|responde no chat|comigo no chat|quem [eé] que j[aá])\b',
  'pergunta ao chat sem resposta no corte'),
 ('INTERACAO', r'\b(t[aá]o me ouvindo|voc[eê]s t[aã]o ouvindo|t[aá] me ouvindo|beleza\?|posso avan[cç]ar)\b',
  'checagem de audio ou de acompanhamento'),
]
frase_ini = 0
for i, (p, a, b) in enumerate(palavras):
    if p and p[0].isupper() and i > 0:
        frase_ini = i
    for tipo, rx, motivo in MARCAS:
        janela = ' '.join(x[0] for x in palavras[max(0, i-3):i+8]).lower()
        if re.search(rx, janela):
            j = i
            while j+1 < len(palavras) and not (palavras[j+1][0][:1].isupper() and j > i+4):
                j += 1
                if palavras[j][2] - palavras[frase_ini][1] > 30:
                    break
            ini, fim = palavras[frase_ini][1], palavras[j][2]
            if fim - ini >= A.min_seg:
                cand.append(dict(tipo=tipo, ini=round(ini, 2), fim=round(fim, 2),
                                 dur=round(fim-ini, 2),
                                 texto=' '.join(x[0] for x in palavras[frase_ini:j+1])[:260],
                                 motivo=motivo))
            break

# ---------- dedup e ordenacao ----------
cand.sort(key=lambda c: c['ini'])
limpo = []
for c in cand:
    if limpo and c['ini'] < limpo[-1]['fim']:
        if c['fim'] > limpo[-1]['fim']:
            limpo[-1]['fim'] = c['fim']
            limpo[-1]['dur'] = round(limpo[-1]['fim'] - limpo[-1]['ini'], 2)
        continue
    limpo.append(c)

print(f'{len(limpo)} candidatos  ·  {sum(c["dur"] for c in limpo):.1f}s no total\n')
for c in limpo:
    print(f'[{c["tipo"]}] {c["ini"]:7.2f} a {c["fim"]:7.2f}  ({c["dur"]:5.1f}s)  {c["motivo"]}')
    print(f'    "{c["texto"][:170]}"')
if A.out:
    json.dump(limpo, open(A.out, 'w'), ensure_ascii=False, indent=1)
    print('\nplano em', A.out)
