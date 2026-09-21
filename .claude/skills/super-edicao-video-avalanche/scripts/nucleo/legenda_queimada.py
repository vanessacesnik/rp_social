#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LEGENDA QUEIMADA, FRASE POR FRASE (nucleo da super-edicao-video-avalanche).

Ordem do Chefe em 14/09/2026: "eu prefiro a legenda frase por frase e nao palavra por palavra".
O padrao passou a ser `--modo frase`: blocos curtos de ate 6 palavras numa linha so, quebrados
na pausa da fala (gap > 0,45s) ou quando a linha nao cabe em 90% da largura. Cada frase fica na
tela do inicio da primeira palavra ate o fim da ultima. Palavra de impacto continua em vermelho
DENTRO da frase. `--modo palavra` mantem o comportamento antigo (uma palavra por vez).

Ordem do Chefe em 25/07/2026: "a legenda deve ser queimada SEMPRE acima da faixa hyperframe,
colada na faixa, isso deve ser padrao na skill". Vale para todo modelo que tenha faixa embaixo
(sanduiche, faixa hyperframe, b-roll no rodape, VSL) e para o talking-head puro, onde a ancora
passa a ser a base do quadro.

Padrao visual (o que o Chefe aprovou em 2026-07-18):
  - UMA palavra por vez, na caixa original da fala (sem forcar caixa alta).
  - Bricolage Grotesque, instancia "96pt ExtraBold".
  - Creme #efe6da; palavras-chave em vermelho alaranjado #f5411f (mira 15 a 20%, nunca frase inteira;
    passar a lista em --destaques, numero e valor entram sozinhos).
  - Sombra desfocada + stroke escuro, para ler sobre qualquer fundo.
  - Tamanho ~120px caindo ate caber em 90% da largura.

Ancoragem: a BASE da palavra fica `--folga` pixels ACIMA do topo da faixa (`--faixa-y`), ou seja,
colada nela. Nao se centraliza no meio do quadro: o objetivo e o bloco de texto encostar na faixa.

Uso:
  python3 legenda_queimada.py --words corpo_words.json --out build/legenda.mov \\
      --dur 76.63 [--faixa-y 1080] [--folga 26] [--w 1080] [--h 1920] [--fps 30] \\
      [--destaques "IA,agente,vender"]

Saida: .mov ProRes 4444 com alpha, pronto para um unico overlay sobre o video montado.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CREME = (0xEF, 0xE6, 0xDA, 255)
VERM = (0xF5, 0x41, 0x1F, 255)   # vermelho alaranjado, ordem do Chefe 14/09/2026
SOMBRA = (0, 0, 0, 205)
STROKE = (10, 6, 4, 255)


def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())


def carrega(path):
    d = json.load(open(path, encoding="utf-8"))
    ws = []
    if isinstance(d, dict) and d.get("segments"):
        for s in d["segments"]:
            ws.extend(s.get("words") or [])
    elif isinstance(d, dict) and d.get("words"):
        ws = d["words"]
    elif isinstance(d, list):
        ws = d
    out = []
    for w in ws:
        tok = (w.get("word") or w.get("text") or "").strip()
        if tok and w.get("start") is not None:
            out.append({"w": tok, "s": float(w["start"]), "e": float(w["end"])})
    out.sort(key=lambda x: x["s"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--w", type=int, default=1080)
    ap.add_argument("--h", type=int, default=1920)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--faixa-y", type=int, default=1080,
                    help="topo da faixa (strip/b-roll). A legenda fica colada ACIMA disso.")
    ap.add_argument("--folga", type=int, default=26, help="px entre a base da palavra e a faixa")
    ap.add_argument("--tam-max", type=int, default=120)
    ap.add_argument("--tam-min", type=int, default=68)
    ap.add_argument("--destaques", default="", help="palavras extras em vermelho, separadas por virgula")
    # A fonte vive em assets/, nao em scripts/. Na unificacao as pastas se separaram e o caminho
    # relativo herdado do script antigo (que morava junto da fonte) parou de existir.
    ap.add_argument("--fonte", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    "..", "..", "assets", "broll-veo-rodape",
                                                    "fonts", "BricolageGrotesque-var.ttf"))
    ap.add_argument("--correcoes", default="", help="de:para,de:para para corrigir o whisper na tela")
    ap.add_argument("--modo", choices=["frase", "palavra"], default="frase",
                    help="frase (padrao desde 14/09/2026) ou palavra (uma por vez)")
    ap.add_argument("--max-palavras", type=int, default=6, help="modo frase: palavras por bloco")
    ap.add_argument("--gap-frase", type=float, default=0.45, help="modo frase: pausa que fecha o bloco (s)")
    ap.add_argument("--tam-max-frase", type=int, default=78)
    ap.add_argument("--tam-min-frase", type=int, default=54)
    a = ap.parse_args()

    extras = {norm(x) for x in a.destaques.split(",") if x.strip()}
    corr = {}
    for par in a.correcoes.split(","):
        if ":" in par:
            k, v = par.split(":", 1); corr[norm(k)] = v.strip()

    if not os.path.isfile(a.fonte):
        sys.exit(f"LEGENDA_FAIL: fonte nao encontrada em {a.fonte}. Passe --fonte com o caminho da "
                 f"BricolageGrotesque-var.ttf.")
    palavras = carrega(a.words)
    if not palavras:
        sys.exit("LEGENDA_FAIL: nenhuma palavra na transcricao")

    def destaque(tok):
        """Impacto: numero, valor, ou termo da lista. Mira 15 a 20% das palavras."""
        n = norm(tok)
        return bool(re.search(r"\d", tok)) or "$" in tok or n in extras

    cache_f = {}

    def fonte(px):
        if px not in cache_f:
            f = ImageFont.truetype(a.fonte, px)
            try:
                f.set_variation_by_name("96pt ExtraBold")
            except Exception:
                pass
            cache_f[px] = f
        return cache_f[px]

    lim = int(a.w * 0.90)

    def desenha(texto):
        px = a.tam_max
        while px > a.tam_min:
            bb = fonte(px).getbbox(texto, stroke_width=3)
            if bb[2] - bb[0] <= lim:
                break
            px -= 2
        f = fonte(px)
        img = Image.new("RGBA", (a.w, a.h), (0, 0, 0, 0))
        base = a.faixa_y - a.folga          # a BASE do texto encosta na faixa
        sh = Image.new("RGBA", (a.w, a.h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((a.w // 2, base + 7), texto, font=f, fill=SOMBRA,
                                anchor="ms", stroke_width=4, stroke_fill=SOMBRA)
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(7)))
        ImageDraw.Draw(img).text((a.w // 2, base), texto, font=f,
                                 fill=VERM if destaque(texto) else CREME,
                                 anchor="ms", stroke_width=3, stroke_fill=STROKE)
        return img

    def desenha_frase(toks):
        """Uma linha com varias palavras, cada uma com sua cor (impacto em vermelho)."""
        texto = " ".join(toks)
        px = a.tam_max_frase
        while px > a.tam_min_frase:
            bb = fonte(px).getbbox(texto, stroke_width=3)
            if bb[2] - bb[0] <= lim:
                break
            px -= 2
        f = fonte(px)
        esp = f.getlength(" ")
        largs = [f.getlength(t) for t in toks]
        total = sum(largs) + esp * (len(toks) - 1)
        x0 = (a.w - total) / 2
        base = a.faixa_y - a.folga
        img = Image.new("RGBA", (a.w, a.h), (0, 0, 0, 0))
        sh = Image.new("RGBA", (a.w, a.h), (0, 0, 0, 0))
        dsh = ImageDraw.Draw(sh)
        x = x0
        for t, lg in zip(toks, largs):
            dsh.text((x, base + 7), t, font=f, fill=SOMBRA, anchor="ls", stroke_width=4, stroke_fill=SOMBRA)
            x += lg + esp
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(7)))
        d = ImageDraw.Draw(img)
        x = x0
        for t, lg in zip(toks, largs):
            d.text((x, base), t, font=f, fill=VERM if destaque(t) else CREME,
                   anchor="ls", stroke_width=3, stroke_fill=STROKE)
            x += lg + esp
        return img

    def cabe(toks):
        return fonte(a.tam_min_frase).getbbox(" ".join(toks), stroke_width=3)[2] <= lim

    def monta_frases(pal):
        """Blocos de ate --max-palavras, fechados em pausa > --gap-frase ou quando a linha estoura."""
        frases, atual = [], []
        for w in pal:
            tok = corr.get(norm(w["w"]), w["w"])
            if atual:
                gap = w["s"] - atual[-1]["e"]
                if gap > a.gap_frase or len(atual) >= a.max_palavras or not cabe([x["t"] for x in atual] + [tok]):
                    frases.append(atual); atual = []
            atual.append({"t": tok, "s": w["s"], "e": w["e"]})
        if atual:
            frases.append(atual)
        return [{"toks": tuple(x["t"] for x in fr), "s": fr[0]["s"], "e": fr[-1]["e"]} for fr in frases]

    tmp = tempfile.mkdtemp(prefix="legenda_")
    branco = os.path.join(tmp, "_vazio.png")
    Image.new("RGBA", (a.w, a.h), (0, 0, 0, 0)).save(branco)
    feitos, n_destaque = {}, 0

    def png_de(texto):
        nonlocal n_destaque
        if texto not in feitos:
            p = os.path.join(tmp, "tok_%04d.png" % len(feitos))
            (desenha_frase(list(texto)) if isinstance(texto, tuple) else desenha(texto)).save(p)
            feitos[texto] = p
            if isinstance(texto, tuple):
                n_destaque += sum(1 for t in texto if destaque(t))
            elif destaque(texto):
                n_destaque += 1
        return feitos[texto]

    # emenda vao curto entre palavras para a legenda nao piscar
    for i in range(len(palavras) - 1):
        if 0 <= palavras[i + 1]["s"] - palavras[i]["e"] < 0.12:
            palavras[i]["e"] = palavras[i + 1]["s"]

    nframes = int(round(a.dur * a.fps))
    if a.modo == "frase":
        frases = monta_frases(palavras)
        # frase segura ate a proxima entrar (vao curto), sem piscar
        for i in range(len(frases) - 1):
            if 0 <= frases[i + 1]["s"] - frases[i]["e"] < 0.35:
                frases[i]["e"] = frases[i + 1]["s"]
        palavras = [{"w": fr["toks"], "s": fr["s"], "e": fr["e"]} for fr in frases]
    idx = 0
    for fi in range(nframes):
        t = (fi + 0.5) / a.fps
        while idx < len(palavras) and palavras[idx]["e"] <= t:
            idx += 1
        ativo = None
        if idx < len(palavras) and palavras[idx]["s"] <= t < palavras[idx]["e"]:
            ativo = palavras[idx]["w"]
        if ativo and isinstance(ativo, tuple):
            texto = ativo
        elif ativo:
            n = norm(ativo)
            texto = corr.get(n, ativo)
        else:
            texto = None
        dst = os.path.join(tmp, "f%05d.png" % fi)
        os.link(png_de(texto) if texto else branco, dst)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    r = subprocess.run(["ffmpeg", "-y", "-framerate", str(a.fps), "-start_number", "0",
                        "-i", os.path.join(tmp, "f%05d.png"), "-c:v", "prores_ks",
                        "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-qscale:v", "8", a.out],
                       capture_output=True, text=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if r.returncode != 0:
        sys.exit("LEGENDA_FAIL no encode:\n" + r.stderr[-600:])
    pct = 100.0 * n_destaque / max(1, sum(len(k) if isinstance(k, tuple) else 1 for k in feitos))
    print(f"=== LEGENDA === modo {a.modo}: {len(palavras)} blocos, {len(feitos)} tokens distintos, "
          f"{nframes} frames")
    print(f"  base do texto em y={a.faixa_y - a.folga} (colada na faixa que comeca em {a.faixa_y})")
    print(f"  destaque em vermelho: {n_destaque} tokens ({pct:.0f}%, alvo 15 a 20%)")
    print(f"  saida: {a.out}")


if __name__ == "__main__":
    main()
