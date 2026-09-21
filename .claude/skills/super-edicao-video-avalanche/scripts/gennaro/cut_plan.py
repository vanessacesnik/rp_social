#!/usr/bin/env python3
# WORD-LEVEL CUT PLANNER (authored per video, mechanics reusable). From original.mp4 + the
# word-timestamps whisper json it computes: fine cut (silences > 0.35s -> a short breath,
# measured fillers out), an original->final time map, the caption events, the face punch-in
# windows, the sfx delays, and writes render/cut_filter.txt + render/punch_filter.txt + render/plan.json.
#
# Fill in the ===== PER-VIDEO CONFIG ===== block, then run:
#   GEN_WORK=/abs/workspace python3 cut_plan.py
# Requires GEN_WORK/original.mp4 and GEN_WORK/audio16k.json (whisper word_timestamps of the base).
import json, re, subprocess, unicodedata, os

WORK = os.environ.get("GEN_WORK") or os.getcwd()
os.chdir(WORK)

# ======================= PER-VIDEO CONFIG (edite isto) =======================
SLUG = "meu_video"          # vira FINAL_<slug>_gennaro.mp4
BASE_DUR = 67.60            # ponto de corte do talking head (fim da ultima palavra util)
OUTRO = 3.9                 # duracao do fecho CTA anexado depois do talking head

# Fillers a remover: SO os claros, com intervalo medido pela energia (RMS) para tirar a silaba
# inteira sem sobra e sem comer a vizinha. NA DUVIDA, MANTEM (verbo ta/to fica, anafora fica,
# pausa dramatica antes de numero/climax fica). tag, contexto, [inicio, fim] no tempo do original.
FILLER_CUTS = [
    # ('cara', "...desenvolver [Cara] fazer...", [47.90, 48.34]),
]

# Elementos: (nome, offset_no_ORIGINAL, duracao_da_animacao, tipo[, kind]). tipo 'html' ou 'img'.
# 'html' casa com elements/<nome>.html; 'img' usa elements/imgcard.html + IMG[nome].
# kind opcional define a regua de margem no QA: 'wide' (padrao, texto largo [160,920]) ou
# 'small' (chip/badge/pill/toast/stamp, envelope [130,950]). Na duvida deixe 'wide' (mais rigido).
ELEMS = [
    ('e1_hook',   0.20, 3.9,  'html'),
    # ('imgA',    18.95, 5.0, 'img'),
    # ('e9_stamp', 65.7, 2.0, 'html', 'small'),
    # (nao liste o CTA aqui; o fecho assinatura e tratado a parte no build)
]
# Config das imagens (gpt-image-2 + moldura). file bate com GEN_WORK/img/<file>.
IMG = {
    # 'imgA': {'file': 'a_cena.png', 'kb': 'push', 'accent': 'green', 'logos': 'whatsapp', 'title': ''},
}

# Palavras que ganham cor na legenda (uma cor por frase, a primeira que casar).
GREEN = {'IA', 'NAIA', 'LEADS'}          # dinheiro / positivo
CORAL = {'ABSURDO', 'COBRA', 'HORA'}     # enfase

# Punch-ins de rosto: (kind close|wide, sequencia de palavras normalizadas, tmin, tmax no ORIGINAL).
# close ~1.17x, wide ~1.12x, alternando. Ancorar em frase FORTE (promessa, numero, virada).
PUNCH_DEF = [
    # ('close', ['OLHA','QUE','ABSURDO'], 0.0, 4.0),
]
CAP_SUPPRESS_UNTIL = 4.15   # segura a legenda enquanto o card de gancho ocupa a tela (tempo original)
GAP_SAIDA = 0.5             # o elemento fica ate faltar isso pro proximo, e sai nesse intervalo
# ============================ FIM DO CONFIG ============================

# ---------- 1. palavras no timeline do original ----------
for req in ('original.mp4', 'audio16k.json'):
    if not os.path.isfile(req):
        raise SystemExit(f"FALTA {req} em {WORK}. Rode o passo (a)/(b) antes: copie o original e"
                         f" gere a transcricao word-level.")
d = json.load(open('audio16k.json', encoding='utf-8'))
# aceita whisper CLI (segments[].words) e tambem json com words na raiz (faster-whisper/whisperx)
_segs = d.get('segments') if isinstance(d, dict) else None
if _segs is None and isinstance(d, dict) and d.get('words'):
    _segs = [{'words': d['words']}]
if not _segs:
    raise SystemExit("audio16k.json sem 'segments'/'words'. Gere com --word_timestamps True.")
words = []
for seg in _segs:
    for w in seg.get('words', []):
        if 'start' not in w or 'end' not in w:
            raise SystemExit("transcricao SEM timestamps de palavra. Refaca com --word_timestamps True.")
        tok = w['word'].strip()
        if not tok or w['start'] >= BASE_DUR:
            continue
        words.append({'w': tok, 's': float(w['start']), 'e': float(w['end'])})
words.sort(key=lambda x: x['s'])

# ---------- 2. silencios ----------
out = subprocess.run(['ffmpeg', '-i', 'original.mp4', '-af', 'silencedetect=noise=-30dB:d=0.28', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
sil = []; cs = None
for ln in out.splitlines():
    m = re.search(r'silence_start:\s*([\d.]+)', ln)
    if m:
        cs = float(m.group(1))
    m = re.search(r'silence_end:\s*([\d.]+)', ln)
    if m and cs is not None:
        sil.append([cs, float(m.group(1))]); cs = None

# ---------- 3. intervalos a REMOVER (pausa > 0.35s vira respiro; nunca zerar) ----------
REM = []; CUT_LOG = {'silences': [], 'fillers': []}
for s, e in sil:
    if e > BASE_DUR:
        e = BASE_DUR
    dur = e - s
    if dur <= 0.35:
        continue
    breath = 0.28 if dur > 1.4 else 0.24 if dur > 0.9 else 0.20 if dur > 0.55 else 0.16
    a, b = s + breath / 2, e - breath / 2
    if b > a + 0.02:
        REM.append([a, b]); CUT_LOG['silences'].append({'sil': [round(s, 3), round(e, 3)], 'dur': round(dur, 3), 'breath': breath, 'removed': round(b - a, 3)})
for tag, ctx, (a, b) in FILLER_CUTS:
    REM.append([a, b]); CUT_LOG['fillers'].append({'tag': tag, 'ctx': ctx, 'orig': [a, b], 'removed': round(b - a, 3)})

# ---------- 4. merge REM, compute KEEPS ----------
REM = [r for r in REM if r[1] > r[0]]; REM.sort()
merged = []
for a, b in REM:
    if merged and a <= merged[-1][1] + 0.001:
        merged[-1][1] = max(merged[-1][1], b)
    else:
        merged.append([a, b])
merged = [[max(0, a), min(BASE_DUR, b)] for a, b in merged if min(BASE_DUR, b) > max(0, a)]
KEEPS = []; cur = 0.0
for a, b in merged:
    if a > cur + 0.02:
        KEEPS.append([cur, a])
    cur = max(cur, b)
if cur < BASE_DUR - 0.02:
    KEEPS.append([cur, BASE_DUR])
KEEPS = [[a, b] for a, b in KEEPS if b - a >= 0.05]

# ---------- 5. mapa tempo original -> final ----------
cum = []; c = 0.0
for a, b in KEEPS:
    cum.append(c); c += (b - a)
NEW_DUR = c


def o2f(t):
    for (a, b), o in zip(KEEPS, cum):
        if a - 1e-6 <= t <= b + 1e-6:
            return o + (t - a)
    best = None
    for (a, b), o in zip(KEEPS, cum):
        for bt, bn in ((a, o), (b, o + (b - a))):
            if best is None or abs(t - bt) < best[0]:
                best = (abs(t - bt), bn)
    return best[1]


def norm(s):
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^A-Za-z0-9]', '', s).upper()


# ---------- 6. janelas dos elementos no final ----------
# A janela de cada elemento e fechada pelo offset do SEGUINTE (nxt), entao ELEMS FORA DE ORDEM
# gerava duracao negativa e elemento sumindo sem erro nenhum. Agora e erro explicito.
import re as _re
for _r in ELEMS:
    if not _re.fullmatch(r'[A-Za-z0-9_]+', _r[0]):
        raise SystemExit(f"nome de elemento invalido: {_r[0]!r}. Use so letras, numeros e _ "
                         f"(o nome vira arquivo, pasta e URL).")
_offs = [r[1] for r in ELEMS]
if _offs != sorted(_offs):
    raise SystemExit(f"ELEMS fora de ordem cronologica: {_offs}. Ordene por offset crescente.")
_dups = {n for n in [r[0] for r in ELEMS] if [r[0] for r in ELEMS].count(n) > 1}
if _dups:
    raise SystemExit(f"nome de elemento repetido: {sorted(_dups)}")
# offset caindo DENTRO de um trecho removido: o2f cola na borda mais proxima e o elemento entra
# num lugar que nao e o que voce marcou. Avisa alto em vez de mentir em silencio.
for _r in ELEMS:
    for _a, _b in merged:
        if _a < _r[1] < _b:
            print(f"WARN elemento '{_r[0]}' ancorado em {_r[1]:.2f}s, que caiu DENTRO de um corte "
                  f"[{_a:.2f},{_b:.2f}]. Vai colar na borda. Reancore numa palavra que sobreviveu.")
nof = [round(o2f(row[1]), 3) for row in ELEMS]
ELEM_F = []
for i, row in enumerate(ELEMS):
    name, off, mov, typ = row[0], row[1], row[2], row[3]
    kind = row[4] if len(row) > 4 else 'wide'
    no = nof[i]
    nxt = nof[i + 1] if i + 1 < len(ELEMS) else NEW_DUR
    # PERSISTENCIA (ordem do Chefe, 2026-07-25): o elemento NAO sai quando a animacao dele acaba.
    # Ele fica na tela ate faltar GAP_SAIDA para o proximo entrar, e a saida dele acontece
    # exatamente nesse meio segundo. Antes, a janela era o tamanho da animacao (`mov`) e sobrava
    # rosto pelado entre um elemento e outro, o que derruba retencao.
    ne = min(nxt - GAP_SAIDA, NEW_DUR)
    if ne - no < 0.9:
        print(f"WARN elemento '{name}' espremido pelo seguinte (janela {ne-no:.2f}s). "
              f"Forcando 0.9s; considere afastar os offsets.")
        ne = min(no + 0.9, NEW_DUR)
    ed = {'name': name, 'type': typ, 'kind': kind, 'off': round(no, 3), 'en_end': round(ne, 3),
          'dur': round(ne - no, 3), 'movlen': mov}
    if typ == 'img' and name in IMG:
        ed['img'] = IMG[name]
    ELEM_F.append(ed)

# ---------- 7. legendas no timeline final (2-3 palavras, keyword colorida) ----------
CAP_START = round(o2f(CAP_SUPPRESS_UNTIL), 3)


def surv_frac(w):
    tot = w['e'] - w['s']
    if tot <= 1e-6:
        return 1.0
    rem = 0.0
    for a, b in merged:
        lo = max(a, w['s']); hi = min(b, w['e'])
        if hi > lo:
            rem += hi - lo
    return 1.0 - rem / tot


cwords = [w for w in words if surv_frac(w) > 0.45]  # mantem palavra cuja fala sobreviveu ao corte


def chars(ws):
    return sum(len(x['w']) for x in ws) + len(ws) - 1


lines = []; curl = []
for wd in cwords:
    endpunct = bool(re.search(r'[.,!?]$', wd['w']))
    tent = curl + [wd]
    if chars(tent) > 16 or len(tent) > 3:
        if curl:
            lines.append(curl); curl = [wd]
        else:
            curl = [wd]
    else:
        curl = tent
    if endpunct and curl:
        lines.append(curl); curl = []
if curl:
    lines.append(curl)
jev = []
for ln in lines:
    s = o2f(ln[0]['s']); e = o2f(ln[-1]['e'])
    if e < s + 0.35:
        e = s + 0.35
    if s < CAP_START - 0.01:
        continue
    parts = []; colored = False
    for wd in ln:
        raw = re.sub(r'[.,!?…]+$', '', wd['w']).upper()
        n = norm(wd['w']); cc = 'w'
        if not colored:
            if n in GREEN:
                cc = 'g'; colored = True
            elif n in CORAL:
                cc = 'c'; colored = True
        parts.append({'t': raw, 'c': cc})
    jev.append({'s': round(s, 3), 'e': round(e, 3), 'p': parts})
_sup = sum(1 for ln in lines if o2f(ln[0]['s']) < CAP_START - 0.01)
if _sup:
    print(f"nota: {_sup} legenda(s) suprimida(s) antes de CAP_SUPPRESS_UNTIL={CAP_SUPPRESS_UNTIL}s "
          f"(o card de gancho ocupa a tela ate la).")
# Aviso de largura: a regua real e a TINTA em pixel (measure_ink), mas da pra pegar as piores
# linhas aqui, antes de gastar um render inteiro. Montserrat Black caixa alta ~0.62em por
# caractere; a 58px isso da ~36px por caractere. Linha acima de ~740px pede fonte menor.
_WIDE = 'MW@%'
def _est_px(parts, fs=58):
    per = fs * 0.62
    return sum(per * (1.18 if ch in _WIDE else 1.0) for pt in parts for ch in pt['t']) + per * 0.32 * (len(parts) - 1)
jev.sort(key=lambda x: x['s'])
for i in range(len(jev) - 1):
    if jev[i]['e'] > jev[i + 1]['s']:
        jev[i]['e'] = round(jev[i + 1]['s'] - 0.02, 3)
_largas = [(e['s'], ' '.join(pt['t'] for pt in e['p']), round(_est_px(e['p']))) for e in jev if _est_px(e['p']) > 740]
if _largas:
    print(f"WARN {len(_largas)} legenda(s) com largura estimada acima de 740px (fonte 58). "
          f"Baixe a fonte ou quebre a linha. Piores:")
    for s, txt, px in sorted(_largas, key=lambda x: -x[2])[:5]:
        print(f"   t={s:6.2f} ~{px}px  {txt}")
os.makedirs('captions', exist_ok=True)
json.dump(jev, open('captions/captions.json', 'w'), ensure_ascii=False)
raw = open('captions/captions.json', encoding='utf-8').read()
assert chr(8212) not in raw and chr(8211) not in raw, "TRAVESSAO na legenda"  # em/en-dash guard

# ---------- 8. punch-ins ----------
nw = [norm(w['w']) for w in words]


def find_seq(seq, tmin=0.0, tmax=1e9):
    L = len(seq)
    for i in range(len(nw) - L + 1):
        if words[i]['s'] < tmin or words[i]['s'] > tmax:
            continue
        if nw[i:i + L] == seq:
            return words[i]['s'], words[i + L - 1]['e']
    return None


punches = []; PCAP = 2.4
for kind, seq, tmin, tmax in PUNCH_DEF:
    r = find_seq(seq, tmin, tmax)
    if not r:
        print("WARN punch nao encontrado:", seq); continue
    a, b = r; a = max(0, a - 0.06); b = min(b + 0.10, a + PCAP)
    na, nb = round(o2f(a), 3), round(o2f(b), 3)
    if nb - na >= 0.4:
        punches.append({'kind': kind, 's': na, 'e': nb, 'phrase': ' '.join(seq)})

punches.sort(key=lambda q: q['s'])
for _i in range(len(punches) - 1):
    if punches[_i + 1]['s'] < punches[_i]['e'] - 0.01:
        print(f"WARN punches sobrepostos: '{punches[_i]['phrase']}' ({punches[_i]['s']:.2f}-{punches[_i]['e']:.2f}) "
              f"e '{punches[_i+1]['phrase']}' ({punches[_i+1]['s']:.2f}). O segundo overlay ganha; separe as janelas.")

# ---------- 9. sfx (ms no final): whoosh na entrada de cada elemento; CTA whoosh + ding no outro ----------
sfx = []
for e in ELEM_F:
    sfx.append({'kind': 'whoosh', 'ms': int(round(e['off'] * 1000)), 'vol': 0.12})
# derivados de OUTRO: com valores cravados (0.2 / 1.7) mudar a duracao do fecho jogava o ding
# pra fora do video ou pra cima da fala.
sfx.append({'kind': 'whoosh', 'ms': int(round((NEW_DUR + min(0.2, OUTRO * 0.06)) * 1000)), 'vol': 0.12})
sfx.append({'kind': 'ding', 'ms': int(round((NEW_DUR + OUTRO * 0.44) * 1000)), 'vol': 0.18})
sfx.sort(key=lambda x: x['ms'])

# ---------- 10. cut filter_complex (jump cut seco + micro-fade 10ms de audio) ----------
K = len(KEEPS); FA = 0.010; lines_f = []
for i, (a, b) in enumerate(KEEPS):
    seglen = b - a
    lines_f.append(f"[0:v]trim={a:.4f}:{b:.4f},setpts=PTS-STARTPTS[v{i}]")
    if seglen > 0.03:
        lines_f.append(f"[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d={FA},afade=t=out:st={seglen-FA:.4f}:d={FA}[a{i}]")
    else:
        lines_f.append(f"[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS[a{i}]")
concat_in = "".join(f"[v{i}][a{i}]" for i in range(K))
lines_f.append(f"{concat_in}concat=n={K}:v=1:a=1[vv][aa]")
open('render/cut_filter.txt', 'w').write(";\n".join(lines_f) + "\n")

# ---------- 11. punch filter_complex (split base, overlay zoom nas janelas) ----------
close = [q for q in punches if q['kind'] == 'close']; wide = [q for q in punches if q['kind'] == 'wide']


def ors(ws):
    return "+".join(f"between(t,{q['s']:.3f},{q['e']:.3f})" for q in ws) or "0"


pf = ("[0:v]split=3[b][c][w];\n"
      "[c]scale=1264:2248,crop=1080:1920,setsar=1[zc];\n"   # ~1.17x close
      "[w]scale=1210:2152,crop=1080:1920,setsar=1[zw];\n"   # ~1.12x wide
      f"[b][zc]overlay=0:0:enable='{ors(close)}':eof_action=pass[m1];\n"
      f"[m1][zw]overlay=0:0:enable='{ors(wide)}':eof_action=pass[vout]\n")
open('render/punch_filter.txt', 'w').write(pf)

# ---------- saida ----------
plan = {'slug': SLUG, 'base_dur': BASE_DUR, 'new_dur': round(NEW_DUR, 3), 'outro': OUTRO,
        'keeps': [[round(a, 3), round(b, 3)] for a, b in KEEPS], 'n_keeps': K,
        'removed_total': round(BASE_DUR - NEW_DUR, 3), 'cap_start': CAP_START,
        'elements': ELEM_F, 'punches': punches, 'sfx': sfx, 'cut_log': CUT_LOG, 'captions_n': len(jev)}
json.dump(plan, open('render/plan.json', 'w'), ensure_ascii=False, indent=1)

print(f"=== PLAN {SLUG} ===")
print(f"base {BASE_DUR:.2f}s -> final {NEW_DUR:.2f}s (removeu {BASE_DUR-NEW_DUR:.2f}s em {len(merged)} cortes, {K} keeps) +outro {OUTRO}")
print(f"silencios: {len(CUT_LOG['silences'])} | fillers: {len(CUT_LOG['fillers'])} | legendas: {len(jev)} (comeca {CAP_START}s)")
print("elementos (nome off end dur):")
for e in ELEM_F:
    print(f"  {e['name']:12s} {e['off']:6.2f} -> {e['en_end']:6.2f}  dur={e['dur']:.2f} [{e['type']}]")
print("buracos entre elementos (rosto pelado se >1.2s):")
for i in range(len(ELEM_F) - 1):
    g = ELEM_F[i + 1]['off'] - ELEM_F[i]['en_end']
    print(f"  {ELEM_F[i]['name']:12s} -> {ELEM_F[i+1]['name']:12s} gap {g:+.2f}{'  <== GAP' if g > 1.2 else ''}")
print("punches:", [(q['kind'], q['s'], q['e'], q['phrase']) for q in punches])
