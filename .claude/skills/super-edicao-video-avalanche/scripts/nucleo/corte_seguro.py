#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORTE DE SILENCIO SEGURO (nucleo da super-edicao-video-avalanche).

Ordem do Chefe (2026-07-25), inegociavel: "nunca pode cortar uma palavra no meio, nunca pode
cortar uma palavra antes dela comecar e cortar a letra da palavra, sempre tem que ser um corte
seguro e muito fino, para nao deixar erro e para tambem nao ter silencio pelo video."

Sao duas fontes, e cada uma mente de um jeito. O `silencedetect` mede ENERGIA: o ataque de
consoante surda (p, t, k, f, s) fica abaixo do limiar, entao ele diz que o silencio dura mais do
que dura, e cortar ate la come a primeira letra ("...essoa" no lugar de "pessoa"). O whisper marca
PALAVRA com folga nas duas pontas, entao guardar so por ele congela o corte e o video fica cheio
de buraco. Usar so uma das duas quebra um dos dois lados da ordem.

A saida e medir a borda REAL da fala:

  1. o audio vira envelope de RMS em janelas de 10ms (resolucao fina, o silencedetect nao tem).
  2. o piso de ruido sai do proprio audio (percentil baixo do envelope), nao de um numero chutado.
  3. em cada vao entre duas palavras, anda-se pra frente a partir do fim da fala anterior ate a
     energia cair, e pra tras a partir do inicio da proxima, achando onde a voz REALMENTE comeca
     e termina, com precisao de 10ms.
  4. aplica-se uma guarda curta em ms nos dois lados dessa borda medida.
  5. o whisper vira TRAVA de seguranca, nao regua: o corte pode entrar na folga dele ate um teto
     (`--max-invasao`), nunca alem, para o caso de a energia enganar (eco, respiracao alta).
  6. o que se remove nunca e o vao inteiro: deixa-se um RESPIRO proporcional, porque pausa zerada
     gera fala metralhada e emenda audivel.

Saida: JSON com os intervalos a REMOVER, os KEEPS, o mapa tempo_original -> tempo_final, e um
relatorio do que foi recusado e por que.

Uso:
  python3 corte_seguro.py --video original.mp4 --words words.json --out plano_corte.json \\
      [--base-dur 81.8] [--guarda-pre 80] [--guarda-pos 120] [--min-remove 120]

`words.json` aceita whisper CLI (segments[].words), faster-whisper/whisperx (words na raiz) e
lista pura de {word,start,end}.
"""
import argparse, json, os, re, subprocess, sys

# --------------------------------------------------------------------------- padroes
GUARDA_PRE_MS = 60     # margem ANTES do inicio medido da fala (protege o ataque da consoante)
GUARDA_POS_MS = 80     # margem DEPOIS do fim medido da fala (protege a cauda e o plosivo)
MIN_REMOVE_MS = 120    # abaixo disso nao compensa cortar (a emenda aparece mais que o ganho)
MIN_SIL_S = 0.30       # vao menor que isso nem entra na roda
MAX_INVASAO_MS = 250   # o quanto o corte pode entrar na folga do whisper, no maximo
WIN_MS = 10            # resolucao do envelope de energia
PISO_PCT = 20          # percentil do envelope tratado como piso de ruido
PISO_FATOR = 2.2       # voz = piso * fator (histerese simples, robusta a ruido de sala)
NOISE_DB = -30         # limiar do silencedetect, so pra LEVANTAR candidatos a vao
COBERTURA_MAX = 0.70   # fracao de uma palavra do whisper que o corte pode cobrir, no maximo


def carrega_palavras(path):
    d = json.load(open(path, encoding="utf-8"))
    ws = []
    if isinstance(d, dict) and d.get("segments"):
        for seg in d["segments"]:
            ws.extend(seg.get("words") or [])
    elif isinstance(d, dict) and d.get("words"):
        ws = d["words"]
    elif isinstance(d, list):
        ws = d
    out = []
    for w in ws:
        s, e = w.get("start"), w.get("end")
        tok = (w.get("word") or w.get("text") or "").strip()
        if s is None or e is None:
            raise SystemExit("transcricao SEM timestamp de palavra. Refaca com --word_timestamps True.")
        if tok:
            out.append({"w": tok, "s": float(s), "e": float(e)})
    out.sort(key=lambda x: x["s"])
    if not out:
        raise SystemExit("nenhuma palavra na transcricao.")
    return out


def envelope(video, win_ms=WIN_MS):
    """RMS por janela de win_ms, em 16k mono. Retorna (lista_rms, janelas_por_segundo)."""
    import array, math
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    pcm = array.array("h"); pcm.frombytes(raw[:len(raw) - (len(raw) % 2)])
    n = int(16000 * win_ms / 1000)
    env = []
    for i in range(0, len(pcm) - n + 1, n):
        s = 0
        for x in pcm[i:i + n]:
            s += x * x
        env.append(math.sqrt(s / n))
    return env, 1000.0 / win_ms


def nucleo_silencioso(env, fps_env, t0, t1, piso):
    """Maior bloco CONTIGUO de janelas abaixo do piso dentro de [t0,t1]. E o silencio de verdade,
    medido no audio, com resolucao de 10ms. Retorna (ini, fim) em segundos, ou None.

    Por que nao usar o vao entre as palavras do whisper: ele ESTICA os timestamps para cobrir a
    pausa, entao onde o audio tem 600ms de silencio ele frequentemente reporta vao ZERO. Guardar
    por ele congelava o corte. A energia nao mente sobre presenca de voz."""
    i0 = max(0, int(t0 * fps_env))
    i1 = min(len(env), int(t1 * fps_env) + 1)
    melhor = (0, None, None)
    ini = None
    for k in range(i0, i1):
        if env[k] <= piso:
            if ini is None:
                ini = k
        else:
            if ini is not None and k - ini > melhor[0]:
                melhor = (k - ini, ini, k)
            ini = None
    if ini is not None and i1 - ini > melhor[0]:
        melhor = (i1 - ini, ini, i1)
    if melhor[1] is None:
        return None
    return melhor[1] / fps_env, melhor[2] / fps_env


def tem_voz(env, fps_env, t0, t1, piso):
    """True se QUALQUER janela de 10ms dentro de [t0,t1] esta acima do piso."""
    for k in range(max(0, int(t0 * fps_env)), min(len(env), int(t1 * fps_env) + 1)):
        if env[k] > piso:
            return True
    return False


def detecta_silencios(video, noise=NOISE_DB, dmin=MIN_SIL_S):
    r = subprocess.run(["ffmpeg", "-i", video, "-af", f"silencedetect=noise={noise}dB:d={dmin}",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    sil, cur = [], None
    for ln in r.splitlines():
        m = re.search(r"silence_start:\s*(-?[\d.]+)", ln)
        if m:
            cur = max(0.0, float(m.group(1)))
        m = re.search(r"silence_end:\s*([\d.]+)", ln)
        if m and cur is not None:
            sil.append([cur, float(m.group(1))]); cur = None
    return sil


def respiro_para(dur):
    """Pausa que FICA. Transicao de bloco merece mais ar que respirada curta."""
    if dur > 1.40: return 0.28
    if dur > 0.90: return 0.24
    if dur > 0.55: return 0.20
    return 0.16


def planeja(video, words, base_dur=None, guarda_pre=GUARDA_PRE_MS, guarda_pos=GUARDA_POS_MS,
            min_remove=MIN_REMOVE_MS, max_invasao=MAX_INVASAO_MS):
    gpre, gpos, gmin = guarda_pre / 1000.0, guarda_pos / 1000.0, min_remove / 1000.0
    inv = max_invasao / 1000.0
    env, fps_env = envelope(video)
    ordenado = sorted(env)
    piso = max(1.0, ordenado[int(len(ordenado) * PISO_PCT / 100)] * PISO_FATOR)
    if base_dur is None:
        base_dur = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
            capture_output=True, text=True).stdout.strip())
    words = [w for w in words if w["s"] < base_dur]
    remover, recusados = [], []

    for s, e in detecta_silencios(video):
        e = min(e, base_dur)
        if e <= s:
            continue
        # ---- silencio REAL medido no audio (a energia manda; o whisper prova depois)
        nuc = nucleo_silencioso(env, fps_env, s, e, piso)
        if nuc is None:
            recusados.append({"sil": [round(s, 3), round(e, 3)],
                              "motivo": "nenhuma janela abaixo do piso de ruido (nao e silencio de verdade)"})
            continue
        ns, ne = nuc
        a, b = ns + gpos, ne - gpre          # guardas protegem a cauda e o ataque da voz vizinha

        # ---- trava dura 1: nao pode sobrar UMA janela de 10ms com voz dentro do que sera removido
        if b > a and tem_voz(env, fps_env, a, b, piso):
            recusados.append({"sil": [round(s, 3), round(e, 3)],
                              "motivo": "energia de voz dentro do trecho (nao remove)"})
            continue
        # ---- trava dura 2: nenhuma palavra do whisper pode ser ENGOLIDA pelo corte.
        # A trava 1 ja garante que nao ha energia no trecho, mas fala sussurrada no fim da frase
        # pode ficar abaixo do piso e a energia nao a enxerga. Entao: entrar na folga do whisper e
        # permitido (ele estica os limites em ate meio segundo), engolir a palavra nao e.
        engolidas = [w for w in words
                     if (w["e"] - w["s"]) > 0 and
                     (min(w["e"], b) - max(w["s"], a)) / (w["e"] - w["s"]) >= COBERTURA_MAX]
        if engolidas:
            recusados.append({"sil": [round(s, 3), round(e, 3)],
                              "motivo": f"engoliria {int(COBERTURA_MAX*100)}%+ da palavra " + repr(engolidas[0]["w"]),
                              "palavra": [round(engolidas[0]["s"], 3), round(engolidas[0]["e"], 3)]})
            continue
        if b - a < gmin:
            recusados.append({"sil": [round(s, 3), round(e, 3)],
                              "motivo": f"sobrou {max(0, b-a)*1000:.0f}ms uteis apos as guardas (minimo {min_remove}ms)"})
            continue
        # ---- deixa o respiro, tirando por igual dos dois lados
        resp = respiro_para(b - a)
        if (b - a) - resp < gmin:
            recusados.append({"sil": [round(s, 3), round(e, 3)],
                              "motivo": f"pausa de {b-a:.2f}s precisa manter respiro de {resp:.2f}s"})
            continue
        ra, rb = a + resp / 2, b - resp / 2
        remover.append({"ini": round(ra, 4), "fim": round(rb, 4),
                        "removido": round(rb - ra, 3), "respiro": resp,
                        "sil_original": [round(s, 3), round(e, 3)]})

    # ---- merge e keeps
    remover.sort(key=lambda r: r["ini"])
    merged = []
    for r in remover:
        if merged and r["ini"] <= merged[-1]["fim"] + 0.001:
            merged[-1]["fim"] = max(merged[-1]["fim"], r["fim"])
        else:
            merged.append(dict(r))
    keeps, cur = [], 0.0
    for r in merged:
        if r["ini"] > cur + 0.02:
            keeps.append([round(cur, 4), round(r["ini"], 4)])
        cur = max(cur, r["fim"])
    if cur < base_dur - 0.02:
        keeps.append([round(cur, 4), round(base_dur, 4)])
    keeps = [k for k in keeps if k[1] - k[0] >= 0.05]
    nova = sum(b - a for a, b in keeps)

    # ---- mapa original -> final (para reancorar legenda, elemento e gancho)
    mapa, acc = [], 0.0
    for a, b in keeps:
        mapa.append({"orig": [a, b], "final": [round(acc, 4), round(acc + (b - a), 4)]})
        acc += b - a

    return {"video": os.path.abspath(video), "base_dur": round(base_dur, 3),
            "nova_dur": round(nova, 3), "removido_total": round(base_dur - nova, 3),
            "n_cortes": len(merged), "n_keeps": len(keeps),
            "guardas_ms": {"pre": guarda_pre, "pos": guarda_pos, "min_remove": min_remove},
            "remover": merged, "keeps": keeps, "mapa": mapa, "recusados": recusados,
            "palavras_total": len(words)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--words", required=True)
    ap.add_argument("--out", default="plano_corte.json")
    ap.add_argument("--base-dur", type=float, default=None)
    ap.add_argument("--guarda-pre", type=int, default=GUARDA_PRE_MS)
    ap.add_argument("--guarda-pos", type=int, default=GUARDA_POS_MS)
    ap.add_argument("--min-remove", type=int, default=MIN_REMOVE_MS)
    ap.add_argument("--max-invasao", type=int, default=MAX_INVASAO_MS,
                    help="quanto o corte pode entrar na folga do timestamp do whisper (ms)")
    a = ap.parse_args()
    plano = planeja(a.video, carrega_palavras(a.words), a.base_dur,
                    a.guarda_pre, a.guarda_pos, a.min_remove, a.max_invasao)
    json.dump(plano, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"=== CORTE SEGURO ===")
    print(f"  {plano['base_dur']:.2f}s -> {plano['nova_dur']:.2f}s "
          f"(tirou {plano['removido_total']:.2f}s em {plano['n_cortes']} cortes, {plano['n_keeps']} keeps)")
    print(f"  guardas: {a.guarda_pre}ms antes da palavra, {a.guarda_pos}ms depois, minimo {a.min_remove}ms")
    if plano["recusados"]:
        print(f"  RECUSADOS {len(plano['recusados'])} cortes (a favor da fala):")
        for r in plano["recusados"][:8]:
            print(f"    {r['sil'][0]:7.2f}-{r['sil'][1]:6.2f}  {r['motivo']}")
        if len(plano["recusados"]) > 8:
            print(f"    (+{len(plano['recusados'])-8} outros)")
    print(f"  plano em {a.out}")
    print("  AGORA RODE verifica_palavras.py no arquivo cortado. Sem essa prova, o corte nao esta aceito.")


if __name__ == "__main__":
    main()
