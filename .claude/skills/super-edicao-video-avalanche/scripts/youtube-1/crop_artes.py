#!/usr/bin/env python3
"""Leva as artes 1536x1024 do gpt-image-2 para os 1252x690 uteis do painel escuro.

Herdado inteiro do v11-full/crop_artes.py: so os caminhos mudam, mais a forma
`saida=origem` para regerar uma peca com sufixo sem renomear arquivo na mao.

Regra de ouro: NUNCA comer texto.
  INFOGRAFICO  -> mede a caixa de conteudo, corta so a margem vazia (repartida entre topo
                  e rodape), calibra o fundo para exatamente #0F172A e completa a proporcao
                  com barra lateral da MESMA cor de fundo, o que e invisivel no painel.
  FOTO         -> tira as barras chapadas que o modelo desenhou em cima e embaixo e recorta
                  a largura pelo centro ate a proporcao. Se sobrar altura (o modelo nao
                  desenhou barra chapada nenhuma), corta a ALTURA pelo centro em vez de
                  esmagar a foto no resize.
"""
import os, sys
import numpy as np
from PIL import Image

# Versao generica para a skill: os dois diretorios vem por variavel de ambiente, para o
# mesmo recorte servir a qualquer projeto do lote (video ou CTA) sem copia editada.
RAW = os.environ.get("ARTES_RAW") or os.path.expanduser("~/workspace/v13-full/artes_raw")
OUT = os.environ.get("ARTES_OUT") or os.path.expanduser("~/workspace/v13-full/proj/assets")
W, H = 1252, 690
RATIO = W / H
FUNDO = (15, 23, 42)          # #0F172A, o fundo do painel


def _bbox_conteudo(a, tol=14):   # 14 pega ate a faixa #1B2438 sem texto, que so difere 14 do fundo
    """Linhas que tem alguma variacao horizontal = linhas com conteudo."""
    spread = (a.max(axis=1) - a.min(axis=1)).max(axis=1)
    idx = np.where(spread > tol)[0]
    return int(idx.min()), int(idx.max())


def _faixa_foto(a, tol=3.0):
    """Descarta as barras chapadas (desvio horizontal quase zero) do topo e do rodape."""
    std = a.astype(float).std(axis=1).max(axis=1)
    idx = np.where(std >= tol)[0]
    return int(idx.min()), int(idx.max())


def _calibra_fundo(a):
    """Sobe o fundo do modelo (fica em torno de #020C1D) ate bater #0F172A na borda."""
    anel = np.concatenate([a[:4].reshape(-1, 3), a[-4:].reshape(-1, 3),
                           a[:, :4].reshape(-1, 3), a[:, -4:].reshape(-1, 3)])
    base = np.median(anel, axis=0)
    delta = np.array(FUNDO) - base
    return np.clip(a + delta, 0, 255).astype(np.uint8), base, delta


def processa(nome, origem=None):
    src = os.path.join(RAW, (origem or nome) + ".png")
    a = np.asarray(Image.open(src).convert("RGB")).astype(int)
    h, w, _ = a.shape
    info = nome.startswith("info_")
    nota = ""

    if info:
        a, base, delta = _calibra_fundo(a)
        a = a.astype(int)
        y0, y1 = _bbox_conteudo(a)
        y0 = max(0, y0 - 8); y1 = min(h - 1, y1 + 8)
        alt_min = y1 - y0 + 1
        alvo_h = int(round(w / RATIO))
        if alvo_h >= alt_min:                       # cabe: corte repartido topo/rodape
            sobra = alvo_h - alt_min
            t = max(0, min(h - alvo_h, y0 - sobra // 2))
            rec = a[t:t + alvo_h, :, :]
        else:
            # Conteudo mais alto que o alvo: corta so o vazio E devolve uma folga de
            # respiro com a PROPRIA cor de fundo, em cima e embaixo. Sem isso, a linha
            # de rodape e o sapato do personagem nascem colados na borda da arte.
            rec = a[y0:y1 + 1, :, :]
            mar = max(20, int(round(0.035 * rec.shape[0])))
            rec = np.concatenate([
                np.full((mar, w, 3), FUNDO, dtype=int), rec,
                np.full((mar, w, 3), FUNDO, dtype=int)], axis=0)
            nota = f"folga de fundo {mar}px em cima e embaixo, "
        rh, rw, _ = rec.shape
        larg_alvo = int(round(rh * RATIO))
        if larg_alvo > rw:                          # completa com o proprio fundo
            pad = larg_alvo - rw
            esq = pad // 2
            tela = np.zeros((rh, larg_alvo, 3), dtype=np.uint8)
            tela[:, :] = FUNDO
            tela[:, esq:esq + rw] = rec
            rec = tela
            nota += f"fundo {tuple(int(x) for x in base)} -> #0F172A, barra lateral {esq}px cada lado"
        else:
            corte = (rw - larg_alvo) // 2
            rec = rec[:, corte:corte + larg_alvo]
            nota += f"fundo {tuple(int(x) for x in base)} -> #0F172A, corte lateral {corte}px"
        caixa = f"linhas {y0}..{y1}"
    else:
        y0, y1 = _faixa_foto(a)
        rec = a[y0:y1 + 1, :, :]
        rh, rw, _ = rec.shape
        larg_alvo = int(round(rh * RATIO))
        if larg_alvo <= rw:
            corte = (rw - larg_alvo) // 2
            rec = rec[:, corte:corte + larg_alvo]
            nota = f"corte lateral {corte}px cada lado"
        else:
            alt_alvo = int(round(rw / RATIO))
            t = (rh - alt_alvo) // 2
            rec = rec[t:t + alt_alvo, :, :]
            nota = f"corte de altura {t}px em cima e {rh - alt_alvo - t}px embaixo"
        caixa = f"faixa da foto {y0}..{y1}"

    im = Image.fromarray(np.clip(rec, 0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)

    if info:
        # O LANCZOS reamostra a borda e pode deixar o fundo 1 nivel fora do alvo.
        # Aqui o anel da SAIDA e travado em #0F172A. Quem ja esta no alvo nao muda.
        f = np.asarray(im).astype(int)
        anel2 = np.concatenate([f[:8, :8].reshape(-1, 3), f[:8, -8:].reshape(-1, 3),
                                f[-8:, :8].reshape(-1, 3), f[-8:, -8:].reshape(-1, 3)])
        d2 = np.array(FUNDO) - np.median(anel2, axis=0)
        if np.any(d2):
            f = np.clip(f + d2, 0, 255)
            nota += f", trava final do anel {tuple(int(x) for x in d2)}"
        perto = np.abs(f - np.array(FUNDO)).max(axis=2) <= 1
        f[perto] = FUNDO
        nota += f", dither do fundo achatado em {round(perto.mean() * 100, 1)}% da area"
        im = Image.fromarray(f.astype(np.uint8))
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, nome + ".png")
    im.save(dst, "PNG")
    print(f"[crop] {nome}: {w}x{h} · {caixa} · {nota} -> {W}x{H}")
    return dst


if __name__ == "__main__":
    alvos = sys.argv[1:] or sorted(f[:-4] for f in os.listdir(RAW) if f.endswith(".png"))
    for n in alvos:
        if "=" in n:
            saida, origem = n.split("=", 1)
            processa(saida, origem)
        else:
            processa(n)
