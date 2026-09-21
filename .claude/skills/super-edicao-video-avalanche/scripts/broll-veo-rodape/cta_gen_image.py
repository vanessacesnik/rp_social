import os, sys, base64, json, urllib.request, urllib.error
os.makedirs("/tmp/cta", exist_ok=True)

# ROTA (desde 03/08/2026): assinatura ChatGPT do Chefe via OAuth, sem credito de API.
# A OPENAI_API_KEY continua valendo como REDE DE SEGURANCA, dentro do naia_image.
NAIA_HOME = "/opt/naia-agent" if os.path.isdir("/opt/naia-agent") else os.path.expanduser("~/naia-agent")
sys.path.insert(0, NAIA_HOME + "/scripts")
import naia_image

PROMPT = """Vertical 9:16 cinematic EPIC PROMO POSTER, ultra-realistic anime-cinematic 3D style, premium movie-poster quality,
dramatic neon lighting. A face-off / versus composition for a live event.

KEEP ALL CHARACTERS AND ALL TEXT INSIDE THE CENTRAL 84% OF THE WIDTH with clear margins on the left and right edges
(this will be cropped to a tall 9:16 frame — nothing important near the side edges).

CHARACTERS (confident, determined, heroic expressions):
- DENDERSON on the LEFT: a black Brazilian man, late 30s, completely BALD shaved head, full neat dark beard with some
  grey, broad athletic shoulders, black slim blazer over black tee, a small red 'D' pin, arms confident, serious
  confident look toward center.
- NAIA on the RIGHT: a stunning ultra-realistic anime-style redhead woman, long voluminous wavy copper-red hair, very
  fair porcelain skin with subtle thin glowing cyan-gold circuit lines on neck and forearms, large emerald-green eyes,
  fitted black executive blazer, small orange-red 'N' pin, arms crossed, confident powerful look toward center.
- OPENCLAW the mascot at the CENTER-BOTTOM, in a confident determined fighter stance with claws up: a CHIBI RED LOBSTER
  with a BIG cherry-red lobster HEAD that has a SPECKLED, DIMPLED, slightly bumpy organic shell texture (like a
  strawberry / real lobster shell, NOT a smooth ball), glossy with highlights; an oval head with a cute BABY/CHILD face,
  TWO huge round glossy black eyes with amber irises and big white reflections, a small confident smile; TWO long thin
  red antennae plus two short ones; glossy red lobster CLAWS for hands; a small chubby HUMAN CHILD body wearing a black
  Avalanche hoodie with gold chevron 'A' logo, black joggers with red stripes, white sneakers with red accents. NEVER an
  ant or insect, never insect legs, never a smooth featureless ball head.

CENTER FOCAL POINT: a glowing white ASTERISK / sunburst logo (the Claude/Anthropic style mark) on a glowing coral-red
octagon energy shield, crackling with neon energy, positioned between the characters as the rival 'Claude' side.

TEXT (render EXACTLY, crisp clean bold sans-serif, Portuguese accents correct, in a holographic HUD banner at the TOP):
Line 1 small: "IMERSÃO AO VIVO"
Line 2 BIG: "CLAUDE" (glowing coral-orange) then "VS" (white) then "OPENCLAW" (glowing cyan)
Near the BOTTOM, two clean lines of text:
"8 HORAS DE CURSO AO VIVO"
"LINK NA BIO"

ENVIRONMENT: futuristic Avalanche cyber arena at night, dark navy, glowing circular HUD floor with concentric rings,
neon particles, chevron 'A' logos, dramatic rim lighting.
COLOR PALETTE: deep navy #0A1428, coral red #E63946, cyan #06B6D4, gold, white. Cinematic, ultra detailed, sharp focus."""

try:
    # 1024x1536 e NATIVO desta rota, entao sai cravado.
    r = naia_image.gerar(PROMPT, "/tmp/cta/cta_raw_1024x1536.jpg", size="1024x1536",
                         quality="high", output_format="jpeg", timeout=300)
    print("OK", r["dimensoes"][0], "rota=" + r["rota"])
except Exception as e:
    print("ERRO", str(e)[:500])
