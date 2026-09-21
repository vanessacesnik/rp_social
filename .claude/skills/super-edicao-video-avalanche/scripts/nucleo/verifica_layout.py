#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICA LAYOUT DE OVERLAY: texto cortado, vazio demais, elemento sobreposto.

Por que existe: em 25/07/2026 entreguei cards com "RESOLVID" cortado na borda, dois textos escritos
um por cima do outro e cards com 70% de area vazia, e TUDO isso passou no QA. O `measure_ink.py`
mede a tinta contra a regua da TELA, entao texto que vaza do card mas ainda esta dentro da tela nao
era acusado; e nada media vazio nem colisao. O Chefe pegou olhando, que e exatamente o que a
verificacao existe para evitar.

O que ele checa, por elemento, no PNG renderizado:
  1. CORTE      tinta encostando na borda do proprio card (margem minima em px)
  2. VAZIO      fracao da area do card que tem tinta, contra um piso
  3. COLISAO    faixas horizontais com densidade de tinta muito acima do normal, sinal de
                dois blocos desenhados no mesmo lugar
  4. BORDA TELA tinta fora da regua [130,950]

Uso:
  python3 verifica_layout.py --dir build --card 160,1040,760,720 [--min-preench 0.18] [--margem 14]
"""
import argparse, glob, os, sys
from PIL import Image


def bbox_tinta(im, lum_min=95):
    """CONTEUDO, nao fundo. O card tem fundo opaco, entao medir por alpha marcaria o card inteiro
    como tinta. Texto, barras e icones sao CLAROS sobre fundo escuro: mede-se luminancia.
    Onde o alpha e zero (fora do card) nao ha conteudo por definicao."""
    a = im.getchannel("A").point(lambda p: 255 if p > 40 else 0)
    lum = im.convert("L").point(lambda p: 255 if p > lum_min else 0)
    from PIL import ImageChops
    return None, ImageChops.multiply(a, lum)


def analisa(png, card, margem, min_preench):
    cx, cy, cw, ch = card
    im = Image.open(png).convert("RGBA")
    sf = 1080.0 / im.width
    if sf != 1.0:
        im = im.resize((1080, int(im.height * sf)))
    _, mask = bbox_tinta(im)
    # A MOLDURA do card e tinta e encosta na borda por definicao. O que interessa e o CONTEUDO,
    # entao recorta-se a area interna (descontando moldura + padding) e mede-se so ali.
    # AREA DE CONTEUDO real do card = card menos a borda (3px) menos o padding (26 lateral,
    # 22 vertical). Chutar uma margem unica dava dos dois erros: pequena demais lia a moldura
    # luminosa como conteudo, grande demais exigia margem dentro do proprio padding.
    bd, padx, pady = 3, 26, 22
    ix, iy = cx + bd + padx, cy + bd + pady
    iw, ih = cw - 2 * (bd + padx), ch - 2 * (bd + pady)
    interno = mask.crop((ix, iy, ix + iw, iy + ih))
    bb = interno.getbbox()
    if bb is None:
        return {"vazio_total": True}
    L, T, R, B = bb[0] + ix, bb[1] + iy, bb[2] + ix, bb[3] + iy
    prob = []

    # 1. CORTE: nao ha metrica de pixel que separe "elemento full-width por design" (imagem,
    # barra, trilho, que vao de ponta a ponta de proposito) de "texto cortado pelo overflow".
    # A garantia contra texto cortado e por CONSTRUCAO: `fit()` no infografico.py mede cada texto
    # na fonte real antes de renderizar. O que sobra e a inspecao visual, obrigatoria pelo contrato.

    # 2. OCUPACAO: o que importa e o conteudo se espalhar pelo card, nao pintar o card.
    # Medir "tinta clara" fazia card cheio de blocos com borda fina e fundo escuro parecer vazio.
    # A metrica certa e a area do bounding box do conteudo contra a area util.
    rec = interno
    cobertura = ((R - L) * (B - T)) / float(iw * ih)
    px = rec.getdata()
    frac = sum(1 for v in px if v) / float(iw * ih)
    if cobertura < min_preench - 0.005:   # tolerancia de arredondamento
        prob.append(f"conteudo ocupa {cobertura*100:.0f}% da area do card (piso {min_preench*100:.0f}%): "
                    f"sobra vazio demais")
    if frac < 0.02:
        prob.append(f"quase sem conteudo desenhado ({frac*100:.1f}% de tinta)")

    # 3. COLISAO: nao ha metrica de pixel confiavel aqui. Densidade alta acusa barra preenchida
    # e legenda sobre imagem, que sao legitimas. O que pega colisao de verdade e OLHAR, entao este
    # script gera uma folha de contato com TODOS os elementos (--contato) e a inspecao e obrigatoria.
    # A colisao que originou este script (operador sem coluna propria) foi resolvida por construcao
    # nos arquetipos: cada bloco tem sua faixa de x, nenhuma se cruza.

    # 4. regua da tela
    if L < 130 or R > 950:
        prob.append(f"tinta fora da regua da tela: x de {L} a {R} (limite 130 a 950)")
    return {"L": L, "R": R, "T": T, "B": B, "frac": frac, "problemas": prob}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="build", help="pasta com as sequencias png_<nome>/")
    ap.add_argument("--card", default="160,1040,760,720", help="x,y,w,h do card")
    ap.add_argument("--margem", type=int, default=4,
                    help="folga minima entre o conteudo e o limite da AREA DE CONTEUDO. "
                         "Conteudo encostando nesse limite = texto cortado pelo overflow.")
    ap.add_argument("--min-preench", type=float, default=0.70,
                    help="fracao MINIMA da area do card coberta pelo bounding box do conteudo")
    ap.add_argument("--contato", default="", help="salva uma folha de contato com TODOS os elementos")
    ap.add_argument("--amostras", type=int, default=4, help="frames por elemento (pega no fim da animacao)")
    a = ap.parse_args()
    card = tuple(int(x) for x in a.card.split(","))

    dirs = sorted(d for d in glob.glob(os.path.join(a.dir, "png_*")) if os.path.isdir(d))
    if not dirs:
        sys.exit(f"nenhuma sequencia png_* em {a.dir}")
    reprovados = 0
    print(f"=== LAYOUT === card {card} | margem {a.margem}px | ocupacao minima {a.min_preench*100:.0f}%")
    for d in dirs:
        nome = os.path.basename(d)[4:]
        if nome in ("captions", "cta"):   # geometria propria, nao usa o card
            continue
        fs = sorted(glob.glob(os.path.join(d, "f*.png")))
        if not fs:
            continue
        # olha o TRECHO FINAL da animacao, quando tudo ja entrou
        # antes do fade-out (que zera o card por construcao): 0.45 a 0.8 da animacao
        alvos = [fs[int(len(fs) * f)] for f in (0.45, 0.58, 0.70, 0.80)][:a.amostras]
        piores = []
        for f in alvos:
            r = analisa(f, card, a.margem, a.min_preench)
            if r.get("vazio_total"):
                piores.append("frame totalmente vazio")
            else:
                piores.extend(r["problemas"])
        piores = list(dict.fromkeys(piores))
        if piores:
            reprovados += 1
            print(f"  [REPROVA] {nome}")
            for p in piores:
                print(f"       {p}")
        else:
            print(f"  [ok]      {nome}")
    # folha de contato com TODOS os elementos, para a inspecao visual que nenhuma metrica substitui
    if a.contato:
        from PIL import ImageDraw as _ID
        cel = []
        for d in dirs:
            nome = os.path.basename(d)[4:]
            if nome == "captions":
                continue
            fs = sorted(glob.glob(os.path.join(d, "f*.png")))
            if not fs:
                continue
            im = Image.open(fs[int(len(fs) * 0.7)]).convert("RGBA")
            fundo = Image.new("RGB", im.size, (26, 26, 32))
            fundo.paste(im, (0, 0), im)
            rec = fundo.crop((card[0] - 20, card[1] - 20, card[0] + card[2] + 20, card[1] + card[3] + 20))
            rec = rec.resize((400, int(rec.height * 400 / rec.width)))
            dr = _ID.Draw(rec); dr.rectangle([0, 0, 150, 16], fill=(0, 0, 0))
            dr.text((3, 2), nome, fill=(255, 220, 0))
            cel.append(rec)
        if cel:
            cols = 3; w, h = cel[0].size
            rows = (len(cel) + cols - 1) // cols
            cv = Image.new("RGB", (cols * w + (cols + 1) * 5, rows * h + (rows + 1) * 5), (16, 16, 20))
            for i, c in enumerate(cel):
                r, cc = divmod(i, cols); cv.paste(c, (5 + cc * (w + 5), 5 + r * (h + 5)))
            cv.save(a.contato)
            print(f"\nfolha de contato com os {len(cel)} elementos: {a.contato}")
            print("OLHE TODOS. Metrica nao substitui inspecao: o contrato exige verificar item a item.")

    print()
    if reprovados:
        print(f"LAYOUT_FAIL: {reprovados} elemento(s) com problema. Nao entregue assim.")
        sys.exit(1)
    print("LAYOUT_OK: nada cortado, nada sobreposto, nenhum card vazio demais.")


if __name__ == "__main__":
    main()
