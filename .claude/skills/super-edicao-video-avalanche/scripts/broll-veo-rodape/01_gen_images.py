import os, sys, base64, json, time, subprocess, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

# ROTA (desde 03/08/2026): assinatura ChatGPT do Chefe via OAuth, sem credito de API.
# A OPENAI_API_KEY continua valendo como REDE DE SEGURANCA, dentro do naia_image.
NAIA_HOME = "/opt/naia-agent" if os.path.isdir("/opt/naia-agent") else os.path.expanduser("~/naia-agent")
sys.path.insert(0, NAIA_HOME + "/scripts")
import naia_image

IMGDIR = "/tmp/auto-edit/img"; os.makedirs(IMGDIR, exist_ok=True)

DENDERSON = ("DENDERSON, the CEO: a black Brazilian man, late 30s, completely BALD shaved head, full neat dark beard "
"with a few grey hairs on the jawline, broad athletic shoulders, confident charismatic leader.")

NAIA = ("NAIA, the AI executive: a stunning ultra-realistic anime-style redhead woman, long voluminous wavy copper-red "
"hair over one shoulder, very fair porcelain skin with SUBTLE thin glowing cyan-and-gold circuit lines on neck and "
"forearms (not covering the face), large emerald-green eyes, fitted black executive blazer, elegant confident posture.")

CLAUDINHO = ("CLAUDINHO, the Avalanche mascot for CLAUDE CODE: a CHIBI character with a BIG rounded-cube / box HEAD in "
"matte ORANGE, glossy soft finish; a minimalist face of two thick black bracket-shaped eyes — a '>' on the left and a "
"'<' on the right (a cute '>‹' squinting expression); two small orange ear/side blocks on the head; NO nose, no mouth. "
"Orange hands and skin. Small chubby chibi CHILD body wearing the SAME Avalanche streetwear as OPENCLAW: black HOODIE "
"with a gold chevron 'A' logo on the chest and a gold chain with 'A' pendant, black joggers with red side stripes, "
"white chunky sneakers. NEVER a lobster, NEVER a human/realistic head — ALWAYS the orange box head with '>‹' bracket eyes.")

# ===== LAGOSTA — CANON TRAVADO NAS 3 REFs (capricho máximo) =====
OPENCLAW = ("OPENCLAW, the Avalanche mascot — a CHIBI RED LOBSTER that MUST match the canonical character exactly: "
"a BIG cherry-red lobster HEAD with a SPECKLED, DIMPLED, slightly bumpy organic shell texture (like a strawberry / "
"real lobster shell — NOT a smooth plastic ball), glossy with bright highlights; an OVAL rounded head with a cute "
"BABY / CHILD face (big cranium, round chubby cheeks); TWO huge round glossy black eyes with amber-brown irises and "
"big white reflections, super expressive and adorable; a small open happy smile showing a tiny pink tongue; TWO long "
"thin red antennae curving up from the top plus two shorter secondary antennae at the base; hands are glossy red "
"lobster CLAWS (boxing-glove pincers). Body is a small chubby HUMAN CHILD body (~7 years old; chibi proportion: giant "
"head + tiny body) wearing a black Avalanche HOODIE with a gold chevron 'A' logo and a thin gold chain with an 'A' "
"pendant, black joggers with red side stripes, and white sneakers with red accents. Cute hype kid-creator vibe. "
"NEVER an ant, bee or insect; NEVER insect legs or an insect abdomen/butt; NEVER a smooth featureless ball head; "
"NEVER an adult body; NEVER non-red colors for the head or claws.")

TRIO = DENDERSON + "\n\n" + NAIA + "\n\n" + OPENCLAW + "\n\n" + CLAUDINHO

ENV = ("The Avalanche AI cyber command-center / digital marketing agency at night: dark navy walls, dramatic neon glow, "
"floating holographic HUD dashboards and translucent data panels, glowing chevron 'A' logos, workstations, depth, bokeh. "
"Feels like a real high-tech agency in operation.")

PALETTE = ("Palette: deep navy #0A1428, coral red #E63946, cyan #06B6D4, gold, cream #F5F5F5. Cinematic neon lighting, "
"premium 3D cinematic render, ultra detailed, realistic believable scene.")

SAFE = ("CRITICAL SAFE-AREA: this becomes a 16:9 video. Keep ALL characters, faces, logos and key text inside the central "
"70%. Leave the top ~18% and bottom ~18% as pure environment only — no faces/text/key elements there, so nothing is lost on crop.")

def frame(pose, extra):
    return f"""Landscape 16:9 cinematic frame, ULTRA-REALISTIC ANIME-CINEMATIC 3D STYLE, premium movie quality, a fantastic
yet believable scene inside a real high-tech digital marketing agency.

CHARACTERS (always present, recognizable):
{TRIO}

SCENE / ACTION:
{pose}

ADDITIONAL VISUAL ELEMENTS:
{extra}

ENVIRONMENT: {ENV}

{PALETTE}

{SAFE}"""

BROLLS = [
 dict(id="w01",
   pose=("DENDERSON stands confident and points proudly at a big floating holographic monitor showing a SIMPLE, plain, "
         "cheap-looking website (basic boxy layout, generic AI-made look) that nonetheless has a green SALES line going UP. "
         "NAIA stands beside him approving with a smile; OPENCLAW the lobster and CLAUDINHO are quickly building/assembling "
         "the simple site with their hands, like fast builders. The message: a cheap simple AI-looking site still WORKS and "
         "makes money depending on the niche."),
   extra="A holographic panel of a plain basic website mockup with a rising green revenue arrow, small floating tags 'NICHO' and 'PROJETO', a subtle 'VAI RODAR' caption, optimistic confident mood."),
 dict(id="w02",
   pose=("PROOF / RESULT shot: a HUGE glowing holographic billboard dominates the scene reading '320 INGRESSOS' and 'R$97', "
         "next to a thumbnail of an ugly plain website. DENDERSON presents the giant number with an open proud hand, amazed "
         "but proud; NAIA gestures at the number; OPENCLAW and CLAUDINHO cheer and celebrate the sales, tiny confetti. The "
         "ugly site that still sold a lot."),
   extra="A giant holographic sales counter '320' tickets and a price tag 'R$97', a small 'SITE HORRÍVEL' label on the plain website with a green check, celebratory confetti and rising charts, triumphant mood."),
 dict(id="w03",
   pose=("A crowd of generic digital-marketer people RUN around in a panic chasing floating 'NOVIDADE' / 'NEW' news bubbles, "
         "stressed and desperate. In the calm center DENDERSON stands still, relaxed and unbothered, raising a calm 'easy' "
         "hand telling them to slow down. NAIA stands calm beside him; OPENCLAW and CLAUDINHO hold up small 'NOVIDADE' signs "
         "but stay chill next to the boss. The message: don't run desperate after every new thing."),
   extra="Motion-blurred panicked crowd chasing glowing 'NOVIDADE' news bubbles, a calm bubble 'CALMA' around DENDERSON, contrast between chaos and calm, slightly comic but premium."),
 dict(id="w04",
   pose=("CALM POWER shot: DENDERSON sits/stands totally relaxed and zen in the command center, arms at ease, fully in "
         "control, while his AI agency runs itself smoothly around him. NAIA, OPENCLAW the lobster and CLAUDINHO operate the "
         "workstations peacefully, everything green and working. The boss running his company for years with what he already "
         "has, needing nothing new."),
   extra="Calm green 'TUDO RODANDO' dashboards, a serene '2 ANOS' panel and a subtle 'TÁ MARAVILHOSO' caption, smooth automated workflow lines, peaceful confident self-running-company mood."),
]

def gen(b):
    """PADRAO: OAuth (assinatura ChatGPT). 1536x1024 e NATIVO desta rota."""
    for _ in range(3):
        try:
            raw=f"{IMGDIR}/{b['id']}_raw.jpg"
            r=naia_image.gerar(frame(b["pose"],b["extra"]), raw, size="1536x1024",
                               quality="high", output_format="jpeg", timeout=300)
            crop=f"{IMGDIR}/{b['id']}_16x9.jpg"
            subprocess.run(["ffmpeg","-y","-i",raw,"-vf","crop=1536:864:0:80",crop],
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
            print("IMG OK",b["id"],r["dimensoes"][0],"rota="+r["rota"],flush=True); return
        except Exception as e:
            print("IMG ERR",b["id"],str(e)[:160],flush=True); time.sleep(15)

with ThreadPoolExecutor(max_workers=6) as ex:
    list(ex.map(gen, BROLLS))
print("IMAGES DONE")
