#!/usr/bin/env python3
# gpt-image-2 hero cards for the impactful-speech moments (2 to 3 per video). Landscape
# 1536x1024, dark premium, Avalanche palette, and NO readable text inside the image (text
# baked into a generated image renders wrong; keep only abstract UI, icons, tiny labels).
# Each card is later framed with an animated border + Ken Burns by elements/imgcard.html.
#
# Usage:  GEN_WORK=/abs/workspace python3 gen_images.py jobs.json [name1 name2 ...]
# jobs.json is either {"name": "scene prompt", ...} or [{"name":..., "prompt":...}, ...].
# Output PNGs go to  GEN_WORK/img/<name>.png  (imgcard.html reads them from /img/<name>.png).
import os, sys, json, base64, time, urllib.request, urllib.error

# ROTA (desde 03/08/2026): assinatura ChatGPT do Chefe via OAuth, sem credito de API.
# A OPENAI_API_KEY continua valendo como REDE DE SEGURANCA, dentro do naia_image.
NAIA_HOME = "/opt/naia-agent" if os.path.isdir("/opt/naia-agent") else os.path.expanduser("~/naia-agent")
sys.path.insert(0, NAIA_HOME + "/scripts")
import naia_image

WORK = os.environ.get("GEN_WORK") or os.getcwd()
ENV = os.path.expanduser("~/naia-agent/.env")
OUT = os.path.join(WORK, "img")
MODEL = "gpt-image-2"
SIZE = "1536x1024"          # NATIVO desta rota (sai cravado)


def load_key():
    for line in open(ENV):
        line = line.strip()
        if line.startswith("OPENAI_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("no OPENAI_API_KEY in " + ENV)


PAL = ("Avalanche brand palette ONLY: near-black navy base (#0B0D12 / #12151C), "
       "electric CYAN (#3EC8FF) holographic light, coral-red (#F5402E) accent, "
       "emerald green (#24D869) for positive/up trends, subtle warm gold rim. ")

COMMON = ("Ultra premium, expensive, cinematic 3D render, glossy, high-end tech aesthetic, "
          "volumetric glow, shallow depth of field, soft bokeh, dramatic studio lighting. "
          + PAL +
          "ABSOLUTELY NO readable paragraphs or sentences, no lorem ipsum, no watermark, no logos; "
          "only abstract UI shapes, icons, charts and tiny unreadable labels. Horizontal landscape hero visual.")


def gen(name, prompt, key=None):
    """PADRAO: OAuth (assinatura ChatGPT). A chave paga so entra se o OAuth cair.

    O parametro `key` ficou obsoleto e e ignorado: quem resolve credencial agora e
    o naia_image. Continua na assinatura so pra nao quebrar quem ja chamava assim.
    """
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"{name}.png")
    full = prompt.strip() + " " + COMMON
    for att in range(1, 5):
        try:
            r = naia_image.gerar(full, out, size=SIZE, quality="high", timeout=600)
            print(f"[OK] {name} -> {out} ({os.path.getsize(out)/1024:.0f} KB, "
                  f"{r['dimensoes'][0]}, rota={r['rota']})", flush=True)
            return True
        except Exception as e:
            print(f"[{name}] try{att}: {str(e)[:300]}", file=sys.stderr, flush=True)
            if att == 4:
                return False
            time.sleep(5 * att)
        except Exception as e:
            print(f"[{name}] err try{att}: {e}", file=sys.stderr, flush=True)
            if att == 4:
                return False
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: GEN_WORK=... gen_images.py jobs.json [name ...]")
    raw = json.load(open(sys.argv[1]))
    jobs = {j["name"]: j["prompt"] for j in raw} if isinstance(raw, list) else dict(raw)
    which = sys.argv[2:] or list(jobs.keys())
    ok = all(gen(n, jobs[n]) for n in which if n in jobs)
    print("ALL_IMG_DONE" if ok else "SOME_IMG_FAILED")
