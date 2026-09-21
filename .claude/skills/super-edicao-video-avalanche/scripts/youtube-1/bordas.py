#!/usr/bin/env python3
"""
bordas.py · encosta qualquer borda de corte no SILÊNCIO MEDIDO, nunca no que o whisper diz.

POR QUE ESTE ARQUIVO EXISTE (05/08/2026, depois de o Chefe assistir 40 segundos do 07 e
achar quatro palavras partidas no meio). O `corta_fino.py` ganhou trava de energia e ficou
correto. O `prepara.py`, que é o PRIMEIRO corte do pipeline, nunca ganhou: ele recorta o
gancho e os trechos mortos usando tempo de palavra do whisper, e o whisper ENCURTA o fim da
palavra. Medido nos catorze entregues: 36 palavras decepadas, quase todas na abertura, e a
pior caía de -18 dB direto para -56 em 6 milissegundos, que é vogal cortada ao meio.

A regra é uma só e vale para o pipeline inteiro: NENHUM corte acontece em cima de som. Toda
borda é empurrada para dentro do silêncio mais próximo antes de virar comando de ffmpeg.

DOIS LIMIARES, herdados do corte fino, e é o que impede comer sílaba:
  -45 dB  acha o silêncio (o que dá para cortar)
  -58 dB  acha a CAUDA da palavra (o que não se pode tocar)
Consoante final de "mais", "então", "faz" tem energia baixa e morreria com um limiar só.

GUARDA ASSIMÉTRICA. 0,06s antes da palavra e 0,20s depois, porque o problema é sempre na
cauda: é ali que a consoante mora e é ali que o Chefe percebe o corte.

Quem chama recebe também um RELATÓRIO de quanto cada borda andou, para a prova ir junto.
"""
import os, subprocess, tempfile
import numpy as np

HOP = 0.010
SR = 16000
PISO_FALA = -45.0
PISO_CAUDA = -58.0
GUARDA_ANTES = 0.06
GUARDA_DEPOIS = 0.20


def envelope(video):
    """dB por quadro de 10ms do áudio inteiro."""
    raw = tempfile.mktemp(suffix='.raw')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video,
                    '-ac', '1', '-ar', str(SR), '-f', 's16le', raw], check=True)
    a = np.fromfile(raw, dtype=np.int16).astype(np.float32) / 32768
    os.unlink(raw)
    w = int(SR * HOP)
    n = len(a) // w
    return 20 * np.log10(np.sqrt(np.maximum((a[:n * w].reshape(n, w) ** 2).mean(1), 1e-12)))


def silencios(db, minimo=0.10):
    """Blocos de silêncio de verdade, já descontada a cauda das palavras das pontas.

    O bloco começa depois de a palavra anterior descer abaixo do piso de cauda e termina
    antes de a próxima subir, com as guardas aplicadas. Um bloco que sobra menor que
    `minimo` some: não dá para cortar dentro dele sem encostar em som.
    """
    q = db < PISO_FALA
    d = np.diff(np.concatenate(([0], q.view(np.int8), [0])))
    out = []
    for i0, i1 in zip(np.where(d == 1)[0], np.where(d == -1)[0]):
        k = i0
        while k < i1 and db[k] > PISO_CAUDA:
            k += 1
        c0 = k * HOP + GUARDA_DEPOIS
        k = i1 - 1
        while k > i0 and db[k] > PISO_CAUDA:
            k -= 1
        c1 = (k + 1) * HOP - GUARDA_ANTES
        if c1 - c0 >= minimo:
            out.append((c0, c1))
    return out


def encosta(t, blocos, dur, alcance=2.0):
    """Move `t` para dentro do silêncio mais próximo. Devolve (novo_t, deslocamento, ok).

    Se `t` já cai dentro de um bloco, não anda. Se não, procura o bloco mais próximo dentro
    de `alcance` segundos e vai para a borda dele que estiver do lado de `t`, o que é o
    menor deslocamento possível que ainda tira o corte de cima do som. Sem bloco por perto,
    devolve ok=False: quem chamou tem que gritar, porque cortar ali quebra palavra.
    """
    t = max(0.0, min(dur, t))
    for x, y in blocos:
        if x <= t <= y:
            return t, 0.0, True
    melhor, dist = None, 1e9
    for x, y in blocos:
        for c in (x, y, (x + y) / 2):
            if abs(c - t) < dist:
                melhor, dist = c, abs(c - t)
    if melhor is None or dist > alcance:
        return t, 0.0, False
    return melhor, melhor - t, True


def ajusta(pares, blocos, dur, rotulo='corte'):
    """Encosta as duas bordas de cada par [x, y]. Devolve (pares_novos, relatorio)."""
    novos, rel = [], []
    for x, y in pares:
        nx, dx, okx = encosta(x, blocos, dur)
        ny, dy, oky = encosta(y, blocos, dur)
        if ny <= nx:
            ny = nx + max(0.05, y - x)
            oky = False
        novos.append((nx, ny))
        rel.append({'rotulo': rotulo, 'de': [round(x, 3), round(y, 3)],
                    'para': [round(nx, 3), round(ny, 3)],
                    'andou': [round(dx, 3), round(dy, 3)], 'ok': bool(okx and oky)})
    return novos, rel


def confere(video, cortes, dur, nome='arquivo'):
    """Prova, DEPOIS de cortar: nenhuma borda pode ter som dos dois lados.

    Recebe os instantes de emenda no arquivo JÁ CORTADO. Uma emenda limpa tem silêncio de
    pelo menos um dos lados; som com corpo dos dois lados é palavra partida.
    """
    db = envelope(video)
    ruins = []
    for t in cortes:
        i = int(t / HOP)
        ant = db[max(0, i - 6):i]
        dep = db[i:i + 6]
        ma = float(ant.max()) if len(ant) else -99.0
        md = float(dep.max()) if len(dep) else -99.0
        if ma > -40 and md > -40:
            ruins.append((round(t, 2), round(ma, 1), round(md, 1)))
    print(f'   prova de borda em {nome}: {len(cortes)} emenda(s), '
          f'{len(ruins)} com som dos dois lados' + (f'  {ruins}' if ruins else '  ok'))
    return ruins
