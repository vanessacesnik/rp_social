#!/usr/bin/env python3
# Arte de ENCERRAMENTO dos videos de YouTube - gpt-image-2 LITERAL via naia_image (rota OAuth).
# PADRAO 04/08/2026: o TEXTO e escrito pelo proprio modelo (aprovado na thumb).
# Estilo ANIME ULTRA REALISTA do canon, fundo branco premium com circuito (familia B aprovada).
# Look escolhido pelo Chefe: UNIFORME VERMELHO nos dois humanos.
# OpenClaw ANCORADO na referencia canonica (armadilha nº1: ele vira formiga sem isso).
import os, sys, time

NAIA_HOME = "/opt/naia-agent" if os.path.isdir("/opt/naia-agent") else os.path.expanduser("~/naia-agent")
sys.path.insert(0, NAIA_HOME + "/scripts")
import naia_image

OUT  = os.path.expanduser("~/workspace/t1-full/encerramento/v2")
SKP  = os.path.expanduser("~/.claude/skills/descricao-personagens-avalanche/assets")
SKI  = os.path.expanduser("~/.claude/skills/infograficos/assets")
REFS = [f"{SKP}/openclaw-referencia-canonica.png",
        f"{SKI}/denderson_cut.png", f"{SKI}/naia_cut.png",
        f"{SKI}/claudinho_cut.png", f"{SKI}/codexzinho_cut.png"]
SIZE = "1536x1024"

USO = (
    "This image is the CLOSING CARD of a YouTube video, on screen for ten seconds at the end and "
    "also seen small on a phone. PREMIUM ANIME ULTRA-REALISTIC ILLUSTRATION, horizontal 3:2, "
    "highest quality, cinematic lighting, rich fabric texture, razor sharp. This is a polished "
    "illustration, NOT a flat vector poster."
)

MARCA = (
    "THE BRAND SYMBOL on every character's chest is an UPRIGHT CAPITAL LETTER A in gold, geometric, "
    "built from two parts: two straight legs of equal length meeting at a SHARP APEX AT THE TOP, like "
    "a mountain peak, opening downward and outward to the lower left and lower right, touching only at "
    "the apex; and, instead of a horizontal crossbar, a solid ANGULAR WEDGE in the lower half of the "
    "empty triangle, attached to the inner face of the LEFT leg, pointing RIGHT, stopping BEFORE it "
    "reaches the right leg and leaving a narrow dark notch open. The apex always points to the top of "
    "the image. One symbol per chest, taller than wide."
)

ELENCO = (
    "THE FIVE AVALANCHE CHARACTERS, all five present, in ANIME ULTRA-REALISTIC style, faces and bodies "
    "beautifully rendered with cinematic lighting and real material texture:\n\n"
    "(1) DENDERSON, Brazilian Black man, COMPLETELY BALD shaved head, short well-trimmed dark beard, "
    "broad friendly shoulders, warm natural skin tone, wide charismatic smile. He wears the RED "
    "UNIFORM: coral-red #E63946 sweat hoodie and matching coral-red jogger sweatpants, small upright "
    "gold letter A on the chest, chunky white sneakers, bare ankle skin showing between the hem and "
    "the shoe.\n\n"
    "(2) NAIA, red-haired woman, long very voluminous wavy copper-red hair falling over her right "
    "shoulder, porcelain fair skin, green eyes, thin black choker, faint cyan circuit lines glowing "
    "softly on her neck and forearms. Confident, alluring, charismatic. She wears the RED UNIFORM: "
    "coral-red #E63946 zip hoodie partly open at an elegant neckline with a flattering feminine fit, "
    "small upright gold letter A on the chest, cropped coral-red joggers above the ankle, bare ankle "
    "skin showing, chunky white sneakers. Fully clothed, no transparency.\n\n"
    "(3) CLAUDINHO, chibi child whose head is a big MATTE ORANGE CUBE. Minimal face: two thick black "
    "bracket eyes, a '>' on the left and a '<' on the right, plus two small orange ear blocks on the "
    "sides of the cube. NO mouth, NO nose. He is NOT a lobster and NOT an ant. Full black Avalanche "
    "tracksuit: black hoodie with the upright gold letter A and a gold chain, black joggers with a red "
    "side stripe, chunky white sneakers.\n\n"
    "(4) OPENCLAW, chibi child with a big CHERRY-RED LOBSTER head, copied faithfully from the first "
    "reference image: TALL OVAL head, taller than wide, rounded teardrop skull with full baby cheeks, "
    "glossy cherry-red surface with strong studio highlights, HUGE round black eyes with warm AMBER "
    "irises and two big white highlights, open happy smile with a small pink tongue, FOUR red antennae "
    "(two long ones rising high from the top, two short ones curving to the sides), and two big red "
    "LOBSTER CLAWS as hands with the claw split visible. He is the most beautiful and appealing mascot "
    "of the group, harmonious balanced proportions, polished premium mascot design, charming and "
    "huggable. NOT an ant, NO insect face, no eyebrows, NO tail, NO bare legs. Full black Avalanche "
    "tracksuit: black hoodie with a LARGE upright gold letter A, gold chain and red drawstrings, black "
    "joggers with a red side stripe covering both legs, white socks showing above white sneakers.\n\n"
    "(5) CODEXZINHO, chibi child whose head is a soft flower-shaped CLOUD with rounded lobes, lavender "
    "purple at the top blending to blue at the base. Its only facial feature is a white terminal "
    "prompt: one white greater-than sign '>' plus one white underscore '_'. NO mouth. Head "
    "proportional to the body, not oversized. Full black Avalanche tracksuit like the others.\n\n"
    "NO name plaques, NO labels over any character. Nobody poses for the camera."
)

CENA = (
    "COMPOSITION, 3:2 horizontal, two zones:\n\n"
    "UPPER ZONE, from the top edge down to about 42% of the height: the Avalanche studio, bright and "
    "premium. BACKGROUND: clean PREMIUM WHITE, with a very subtle light tech circuit-grid texture and "
    "a soft light vignette, exactly like a high-end infographic page. Light rounded cards and panels "
    "float on that white background showing simple charts, bars and donut graphs as pure GRAPHIC "
    "SHAPES with no readable words, with coral #F5402E and cyan #0E7490 accents. The five characters "
    "are spread across this zone ACTUALLY WORKING and interacting: Denderson gesturing at the biggest "
    "panel, Naia beside him holding a holographic tablet, the three mascots at their stations, one "
    "pointing, one typing, one handing something over. Everyone concentrated on the task.\n\n"
    "LOWER ZONE, from about 44% of the height to the bottom edge: a clean horizontal BANNER area in "
    "solid off-white #F7F5F0, spanning the full width, separated from the studio above by a thin "
    "coral #F5402E rule. This banner holds the text and NOTHING else: no character, no face, no hand, "
    "no icon, no chart inside it."
)

TEXTO = (
    "TEXT, written by you inside the banner, in heavy geometric sans-serif type (Montserrat Black "
    "style), CENTERED, filling almost the whole width of the banner, BIG and perfectly legible even "
    "when the image is scaled down to a fifth of its size:\n"
    "Line 1, the biggest, in solid dark navy #0F172A, on two centered rows:\n"
    "CONSULTORIA DE IMPLEMENTAÇÃO DE\n"
    "INTELIGÊNCIA ARTIFICIAL PARA NEGÓCIOS\n"
    "Line 2, below it, about 45% the height of line 1, in solid coral #F5402E:\n"
    "LINK NA DESCRIÇÃO\n"
    "SPELLING IS CRITICAL, copy character by character, ALL CAPITALS, with the Portuguese accents "
    "exactly as written: IMPLEMENTAÇÃO with a cedilla under the C and a tilde over the A, "
    "INTELIGÊNCIA with a circumflex over the second E, NEGÓCIOS with an acute accent over the O, "
    "DESCRIÇÃO with a cedilla under the C and a tilde over the final A. No other text anywhere in "
    "the image, no watermark, no signature, no caption, no readable writing on the panels."
)


def build():
    return "\n\n".join([USO, ELENCO, MARCA, CENA, TEXTO])


def gen(letra):
    out = os.path.join(OUT, f"encerramento-{letra}.png")
    os.makedirs(OUT, exist_ok=True)
    for att in range(1, 4):
        try:
            r = naia_image.gerar(build(), out, size=SIZE, quality="high", refs=REFS, timeout=600)
            print(f"[OK] {letra} {r['dimensoes']} rota={r['rota']}", flush=True)
            return True
        except Exception as e:
            print(f"[{letra}] try{att} FALHOU: {repr(e)[:400]}", file=sys.stderr, flush=True)
            time.sleep(5 * att)
    return False


if __name__ == "__main__":
    alvos = sys.argv[1:] or ["a"]
    if alvos == ["print"]:
        print(build()); sys.exit(0)
    ok = all(gen(k) for k in alvos)
    print("ENCERRAMENTO_OK" if ok else "ENCERRAMENTO_FALHOU")
