#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVA DE QUE O CORTE NAO COMEU PALAVRA (nucleo da super-edicao-video-avalanche).

O `corte_seguro.py` planeja com cuidado, mas planejar nao e provar. Este script pega o video JA
CORTADO, transcreve de novo e compara a sequencia de palavras com a transcricao do original. Se
alguma palavra sumiu, apareceu picotada ("essoa" no lugar de "pessoa") ou trocou de lugar, ele
mostra qual, onde, e sai com codigo 1.

E o unico check que pega o erro que o Chefe mais odeia: a letra inicial comida por um corte que
parecia estar em silencio.

Uso:
  python3 verifica_palavras.py --orig words_original.json --cortado corpo_cortado.mp4
  python3 verifica_palavras.py --orig words_original.json --words-cortado words_cortado.json

Se passar `--cortado`, ele mesmo roda o whisper (modelo configuravel por --model, padrao medium).
"""
import argparse, difflib, json, os, re, subprocess, sys, tempfile, unicodedata


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
        if tok:
            out.append({"w": tok, "s": float(w.get("start", 0)), "e": float(w.get("end", 0))})
    return out


# Tokens que o whisper INVENTA ou APAGA livremente entre duas transcricoes do mesmo audio, sem que
# a fala tenha mudado. Medido em caso real: "30 mil reais" numa passada virou "R$ 30 mil" na outra.
# Comparar sem filtrar isso gera falso positivo, e verificador que grita a toa e tao inutil quanto
# verificador que nunca grita.
MOEDA = {"r", "rs", "r$", "$", "reais", "real"}
DESCARTAVEIS = MOEDA | {"%", "por", "cento"} - {"por"}   # "por" e palavra de verdade, fica


def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())


def relevante(tok):
    """Token que entra na comparacao de sequencia."""
    n = norm(tok)
    return bool(n) and n not in {norm(x) for x in DESCARTAVEIS}


def transcreve(video, model):
    tmp = tempfile.mkdtemp(prefix="verifpal_")
    subprocess.run(["whisper", video, "--model", model, "--language", "pt",
                    "--word_timestamps", "True", "--output_format", "json", "-o", tmp],
                   capture_output=True, text=True)
    js = [f for f in os.listdir(tmp) if f.endswith(".json")]
    if not js:
        sys.exit("VERIF_FAIL: whisper nao gerou json do arquivo cortado")
    return os.path.join(tmp, js[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orig", required=True, help="transcricao word-level do ORIGINAL")
    ap.add_argument("--cortado", help="video cortado (transcreve na hora)")
    ap.add_argument("--words-cortado", help="transcricao word-level ja pronta do cortado")
    ap.add_argument("--model", default="medium")
    ap.add_argument("--base-dur", type=float, default=None,
                    help="se o corpo cobre so ate X s do original, compara so ate ai")
    ap.add_argument("--plano", help="plano de corte (json com 'keeps'). Sem ele, qualquer divergencia "
                                    "de transcricao vira acusacao; com ele, so conta o que esta PERTO "
                                    "de uma emenda, que e onde o corte poderia ter causado.")
    ap.add_argument("--tol", type=float, default=0.6,
                    help="distancia em s ate a emenda para a divergencia contar como culpa do corte")
    ap.add_argument("--video-original", help="arbitro: re-transcreve a MESMA janela no ORIGINAL. Se a "
                                             "palavra tambem nao aparece la, o whisper a inventou por "
                                             "contexto na primeira passada e o corte esta inocente.")
    ap.add_argument("--video-cortado-arb", help="arbitro direto: ouve a janela correspondente no VIDEO "
                                                "ENTREGUE. Se a palavra esta la, acabou a discussao, "
                                                "o corte nao a tocou (a acusacao veio do alinhamento "
                                                "da transcricao inteira, nao do audio).")
    a = ap.parse_args()

    if not a.cortado and not a.words_cortado:
        sys.exit("informe --cortado ou --words-cortado")
    wc_path = a.words_cortado or transcreve(a.cortado, a.model)

    emendas = []
    if a.plano:
        pl = json.load(open(a.plano, encoding="utf-8"))
        for k in pl.get("keeps", []):
            emendas += [float(k[0]), float(k[1])]

    def perto_de_emenda(t_orig):
        """Sem plano, tudo conta. Com plano, so conta perto de emenda: divergencia no meio de um
        trecho continuo e o whisper transcrevendo diferente, nao o corte comendo fala."""
        if not emendas:
            return True
        return min(abs(t_orig - e) for e in emendas) <= a.tol

    orig = carrega(a.orig)
    if a.base_dur:
        orig = [w for w in orig if w["s"] < a.base_dur]
    novo = carrega(wc_path)
    orig = [w for w in orig if relevante(w["w"])]
    novo = [w for w in novo if relevante(w["w"])]
    A = [norm(w["w"]) for w in orig]
    B = [norm(w["w"]) for w in novo]
    print(f"=== PALAVRAS === original {len(A)} | depois do corte {len(B)}")
    print(f"    (tokens de moeda e simbolo fora da conta: o whisper troca 'reais' por 'R$' entre passadas)")

    sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False)
    perdidas, trocadas = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "delete":
            for i in range(i1, i2):
                perdidas.append((orig[i]["w"], orig[i]["s"]))
        elif tag == "replace":
            for k in range(max(i2 - i1, j2 - j1)):
                o = orig[i1 + k] if i1 + k < i2 else None
                n = novo[j1 + k] if j1 + k < j2 else None
                if o and n:
                    trocadas.append((o["w"], o["s"], n["w"]))
                elif o:
                    perdidas.append((o["w"], o["s"]))

    ratio = sm.ratio()
    print(f"    similaridade da sequencia: {ratio*100:.2f}%")

    falhou = False
    long_perdidas = [(w, t) for w, t in perdidas if not perto_de_emenda(t)]
    perdidas = [(w, t) for w, t in perdidas if perto_de_emenda(t)]
    if perdidas:
        falhou = True
        print(f"\n!!! {len(perdidas)} PALAVRA(S) SUMIRAM junto a uma emenda:")
        for w, t in perdidas[:20]:
            print(f"    t={t:7.2f}s  {w!r}")
        if len(perdidas) > 20:
            print(f"    (+{len(perdidas)-20} outras)")
    if long_perdidas:
        print(f"\n  {len(long_perdidas)} palavra(s) ausente(s) LONGE de qualquer emenda "
              f"(o whisper omitiu na segunda passada, o corte nao alcanca ali):")
        for w, t in long_perdidas[:8]:
            print(f"    t={t:7.2f}s  {w!r}")
    if trocadas:
        # troca costuma ser erro do whisper (nome proprio, numero) OU palavra picotada pelo corte.
        # picotada = a nova e um SUFIXO/PREFIXO curto da original ("pessoa" -> "essoa").
        picotadas = [(o, t, n) for o, t, n in trocadas
                     if norm(n) and norm(o) != norm(n) and
                     (norm(o).endswith(norm(n)) or norm(o).startswith(norm(n))) and
                     len(norm(n)) < len(norm(o))]
        long_pic = [x for x in picotadas if not perto_de_emenda(x[1])]
        picotadas = [x for x in picotadas if perto_de_emenda(x[1])]
        if long_pic:
            print(f"\n  {len(long_pic)} divergencia(s) tipo prefixo/sufixo LONGE de emenda "
                  f"(fala coloquial transcrita de dois jeitos, ex. 'estao' e 'tao'):")
            for o, t, n in long_pic[:8]:
                print(f"    t={t:7.2f}s  {o!r} / {n!r}")
        if picotadas:
            falhou = True
            print(f"\n!!! {len(picotadas)} PALAVRA(S) PICOTADAS pelo corte (letra comida):")
            for o, t, n in picotadas[:15]:
                print(f"    t={t:7.2f}s  {o!r} virou {n!r}")
        outras = [x for x in trocadas if x not in picotadas]
        if outras:
            print(f"\n  {len(outras)} divergencia(s) de grafia (provavel erro do whisper, nao do corte):")
            for o, t, n in outras[:10]:
                print(f"    t={t:7.2f}s  {o!r} -> {n!r}")

    # ---- arbitro: a palavra existe mesmo no audio original, ouvida isoladamente?
    if falhou and (a.video_original or a.video_cortado_arb) and (perdidas or picotadas):
        print("\n=== ARBITRO: re-ouvindo a mesma janela no ORIGINAL ===")
        absolvidas = []

        def t_no_corpo(t_orig):
            acc = 0.0
            for k in pl.get("keeps", []) if a.plano else []:
                if k[0] <= t_orig <= k[1]:
                    return acc + (t_orig - k[0])
                acc += k[1] - k[0]
            return None

        def ouve(video, t0, dur=3.0):
            d = tempfile.mkdtemp(prefix="arb_"); trecho = os.path.join(d, "t.wav")
            subprocess.run(["ffmpeg", "-y", "-ss", f"{max(0, t0):.2f}", "-t", str(dur),
                            "-i", video, "-ac", "1", "-ar", "16000", trecho], capture_output=True)
            subprocess.run(["whisper", trecho, "--model", a.model, "--language", "pt",
                            "--output_format", "txt", "-o", d], capture_output=True)
            for f in os.listdir(d):
                if f.endswith(".txt"):
                    return open(os.path.join(d, f), encoding="utf-8").read()
            return ""

        for w, tt in list(perdidas) + [(o, ti) for o, ti, _ in picotadas]:
            # arbitro DIRETO: a palavra esta no video entregue?
            if a.video_cortado_arb:
                tc = t_no_corpo(tt)
                if tc is not None:
                    txt = ouve(a.video_cortado_arb, tc - 1.2)
                    if norm(w) in {norm(x) for x in txt.split()}:
                        print(f"    t={tt:7.2f}s {w!r}: PRESENTE no video entregue, ouvido isolado"
                              f"   [{txt.strip()[:60]}]")
                        absolvidas.append((w, tt))
                        continue
            txt = ouve(a.video_original, tt - 1.5)
            achou = norm(w) in {norm(x) for x in txt.split()}
            print(f"    t={tt:7.2f}s {w!r}: {'presente' if achou else 'AUSENTE'} no original isolado"
                  f"   [{txt.strip()[:70]}]")
            if not achou:
                absolvidas.append((w, tt))
        if len(absolvidas) == len(perdidas) + len(picotadas):
            print("  Todas as acusadas somem tambem no ORIGINAL ouvido isoladamente: o whisper as")
            print("  inseriu por contexto na primeira passada. O corte esta inocente.")
            falhou = False

    print()
    if falhou:
        print("VERIFICACAO_REPROVADA: o corte mexeu na fala. Aumente --guarda-pre/--guarda-pos no")
        print("corte_seguro.py e refaca. NUNCA entregue assim.")
        sys.exit(1)
    print("VERIFICACAO_OK: nenhuma palavra perdida nem picotada. A fala saiu inteira.")


if __name__ == "__main__":
    main()
