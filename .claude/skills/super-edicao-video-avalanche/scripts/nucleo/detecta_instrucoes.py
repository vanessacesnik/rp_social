#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DETECTA INSTRUÇÃO DE EDIÇÃO DITA DENTRO DO VÍDEO (quebra da quarta parede).

Ordem do Chefe em 25/07/2026: "sempre busque falas onde estou quebrando a quarta parede: 'errei,
corta essa parte' ou similares".

Ele grava sozinho e, quando erra, fala com o editor no meio da gravação: "errei, corta as duas
falas anteriores", "peraí, deixa eu refazer", "esquece, recomeça". Se ninguém procurar por isso,
a instrução vira conteúdo no vídeo final e o erro fica no ar. No video da imersão (3min49s) havia
TRES tomadas da mesma frase e a ordem de cortar as duas primeiras dita em 140,2s.

O que este script faz: varre a transcrição word-level, acha as marcas, e para cada uma delimita o
TRECHO SUGERIDO A CORTAR, olhando para tras ate o comeco da(s) tentativa(s) repetida(s) e para
frente ate o fim da instrucao. Ele NAO corta nada: imprime a proposta com timestamps e o texto,
porque corte de conteudo so sai com o OK do Chefe.

Uso:
  python3 detecta_instrucoes.py --words audio16k.json [--json saida.json]
"""
import argparse, json, re, sys, unicodedata

# marcas fortes: quase sempre sao instrucao real de edicao
FORTES = [
    r"\berrei\b", r"\bme perdi\b", r"\bfalei errado\b", r"\btroquei\b.*\bpalavra\b",
    r"\bcorta\b(?!ndo)", r"\bcorte\b", r"\bcortar\b.*\b(essa|isso|aqui|parte|fala|trecho)\b",
    r"\btira\b.*\b(essa|isso|essa parte|esse trecho)\b", r"\bpode cortar\b",
    r"\besquece\b(?!.*\bque\b)", r"\brecomeç", r"\bvou refazer\b", r"\bdeixa eu refazer\b",
    r"\bde novo\b.*\bdesculp", r"\bdesculpa\b.*\b(errei|de novo|refazer)\b",
]
# marcas fracas: so contam se houver REPETICAO de frase por perto
FRACAS = [
    r"\bper[ae][ií]\b", r"\bespera a[ií]\b", r"\bvolta\b", r"\bdeixa eu\b",
    r"\bde novo\b", r"\boutra vez\b", r"\bmais uma vez\b",
]


def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", s.lower())


def carrega(path):
    d = json.load(open(path, encoding="utf-8"))
    ws = []
    if isinstance(d, dict) and d.get("segments"):
        for s in d["segments"]:
            ws.extend(s.get("words") or [])
    elif isinstance(d, dict) and d.get("words"):
        ws = d["words"]
    out = []
    for w in ws:
        tok = (w.get("word") or "").strip()
        if tok and w.get("start") is not None:
            out.append({"w": tok, "s": float(w["start"]), "e": float(w["end"])})
    return out


def janela_texto(ws, i, antes=0, depois=0):
    a = max(0, i - antes); b = min(len(ws), i + depois + 1)
    return " ".join(x["w"].strip() for x in ws[a:b])


def acha_repeticao(ws, idx_instr, max_voltar=45):
    """Procura a MESMA sequencia de palavras repetida antes da instrucao. Devolve o inicio da
    primeira tentativa, que e por onde o corte deve comecar."""
    fim = idx_instr
    ini_busca = max(0, fim - max_voltar)
    seq = [norm(x["w"]).strip() for x in ws[ini_busca:fim]]
    melhor = None
    # procura o maior n-grama (>=4 palavras) que aparece 2+ vezes nessa janela
    for n in range(10, 3, -1):
        vistos = {}
        for k in range(0, len(seq) - n + 1):
            g = " ".join(seq[k:k + n]).strip()
            if len(g) < 12:
                continue
            vistos.setdefault(g, []).append(k)
        cand = [(g, ks) for g, ks in vistos.items() if len(ks) >= 2]
        if cand:
            g, ks = max(cand, key=lambda x: len(x[0]))
            melhor = ini_busca + ks[0]
            break
    return melhor


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", required=True)
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    ws = carrega(a.words)
    if not ws:
        sys.exit("transcricao vazia")

    achados = []
    for i, w in enumerate(ws):
        ctx = norm(janela_texto(ws, i, 0, 5))
        forte = any(re.search(p, ctx) for p in FORTES)
        fraca = any(re.search(p, ctx) for p in FRACAS)
        if not (forte or fraca):
            continue
        # evita duplicar a mesma marca em palavras vizinhas
        if achados and w["s"] - achados[-1]["t_instr"] < 3.0:
            continue
        ini_rep = acha_repeticao(ws, i)
        # fim da instrucao: ate 8 palavras depois da marca ou ate uma pausa > 0.6s
        j = i
        while j + 1 < len(ws) and j - i < 10 and (ws[j + 1]["s"] - ws[j]["e"]) < 0.6:
            j += 1
        item = {
            "t_instr": round(w["s"], 2),
            "marca": w["w"].strip(),
            "forca": "forte" if forte else "fraca",
            "instrucao": janela_texto(ws, i, 2, 8),
            "corte_sugerido": None,
        }
        if ini_rep is not None:
            item["corte_sugerido"] = [round(ws[ini_rep]["s"] - 0.15, 2), round(ws[j]["e"] + 0.15, 2)]
            item["texto_que_sai"] = janela_texto(ws, ini_rep, 0, j - ini_rep)
        elif forte:
            item["corte_sugerido"] = [round(ws[max(0, i - 12)]["s"] - 0.15, 2), round(ws[j]["e"] + 0.15, 2)]
            item["texto_que_sai"] = janela_texto(ws, max(0, i - 12), 0, j - max(0, i - 12))
        achados.append(item)

    fortes = [x for x in achados if x["forca"] == "forte"]
    print(f"=== QUEBRA DA QUARTA PAREDE === {len(fortes)} marca(s) forte(s), "
          f"{len(achados)-len(fortes)} fraca(s)")
    if not achados:
        print("  nenhuma instrucao de edicao dita no video.")
    for x in achados:
        print(f"\n  [{x['forca'].upper()}] t={x['t_instr']}s  marca: {x['marca']!r}")
        print(f"    ele diz: ...{x['instrucao']}...")
        if x["corte_sugerido"]:
            a0, b0 = x["corte_sugerido"]
            print(f"    CORTE SUGERIDO: {a0} -> {b0}  ({b0-a0:.1f}s)")
            print(f"    sai: {x.get('texto_que_sai','')[:180]}")
    print("\n  Nada foi cortado. Corte de conteudo so com o OK do Chefe (regra 2 da skill).")
    if a.json:
        json.dump(achados, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"  proposta salva em {a.json}")


if __name__ == "__main__":
    main()
