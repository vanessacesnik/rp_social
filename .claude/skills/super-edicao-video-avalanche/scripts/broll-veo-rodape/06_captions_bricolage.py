#!/usr/bin/env python3
import json, os, re, shutil, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(ROOT, "fonts", "BricolageGrotesque-var.ttf")
TR   = os.path.join(ROOT, "transcript13x.json")
OUTDIR = os.path.join(ROOT, "capframes")

W = H = 1080
FPS = 30
NFRAMES = 2664           # 88.8s * 30
CENTER_Y = 960           # vertical center of the word (chin/neck zone)
BOTTOM_LIMIT = W - 40    # min 40px bottom margin -> 1040
MAX_W = int(W * 0.90)    # 972
SIZE_MAX = 120
SIZE_MIN = 72
CREME = (0xef, 0xe6, 0xda, 255)
RED   = (0xe0, 0x21, 0x28, 255)
SHADOW = (0, 0, 0, 200)
STROKE = (10, 6, 4, 255)

HIGHLIGHTS = {
 "rico","claude","code","saas","crm","dinheiro","empresário","empresario","agente",
 "autônomo","autonomo","24","horas","openclaw","597.343","597","343","tutoriais",
 "bonequinho","vermelho","terminal","desenvolvedor","funcionário","funcionario",
 "digital","vps","nuvem","hostinger","cupom","avalanche","70%","70","desconto",
 "comentários","comentarios","tutorial","manual","naia","vibe","codando","grátis","gratis",
}

def norm(s):
    return re.sub(r"[^\wÀ-ÿ%]", "", s.lower())

def is_hl(disp):
    return norm(disp) in HIGHLIGHTS

# ---- load + correct ----
words = json.load(open(TR))["words"]

items = []  # (start, end, display)
i = 0
while i < len(words):
    w = words[i]
    raw = w["word"].strip()
    s, e = float(w["start"]), float(w["end"])
    low = raw.lower()

    if low == "claudio":
        disp = "Claude"
    elif low == "couto":
        disp = "Code"
    elif low == "bicodando":
        mid = (s + e) / 2.0
        items.append((s, mid, "vibe"))
        items.append((mid, e, "codando"))
        i += 1
        continue
    elif low == "sas":
        disp = "SaaS"
    elif re.sub(r"[^a-z]", "", low) in ("opencloud", "opencl", "openclloud"):
        disp = "OpenClaw"
    elif low == "opencloud":
        disp = "OpenClaw"
    elif low == "naya":
        disp = "Naia"
    elif low == "traga":
        disp = "trava"
    elif raw == "70":
        disp = "70%"
        # swallow the empty "%" token if next
        if i + 1 < len(words) and words[i+1]["word"].strip() in ("", "%"):
            e = float(words[i+1]["end"])
            i += 1
    else:
        disp = raw

    if disp == "" or raw == "":
        i += 1
        continue
    items.append((s, e, disp))
    i += 1

# handle any stray "Open"/"Cloud" pairs -> already single tokens per probe, skip

# ---- gap stretch: if gap to next < 0.12s, extend end to next start ----
items.sort(key=lambda x: x[0])
for k in range(len(items) - 1):
    s, e, d = items[k]
    ns = items[k+1][0]
    if 0 <= (ns - e) < 0.12:
        items[k] = (s, ns, d)

# ---- font cache ----
_font_cache = {}
def get_font(px):
    if px not in _font_cache:
        f = ImageFont.truetype(FONT, px)
        f.set_variation_by_name("96pt ExtraBold")
        _font_cache[px] = f
    return _font_cache[px]

def fit_size(text):
    for px in range(SIZE_MAX, SIZE_MIN - 1, -2):
        f = get_font(px)
        bbox = f.getbbox(text, stroke_width=3)
        if (bbox[2] - bbox[0]) <= MAX_W:
            return px
    return SIZE_MIN

# ---- render one full-frame overlay per distinct display token ----
def render(text):
    px = fit_size(text)
    font = get_font(px)
    color = RED if is_hl(text) else CREME
    # vertical center at CENTER_Y (anchor "mm"); clamp so bottom stays >=40px margin
    cy = CENTER_Y
    bbox = font.getbbox(text, anchor="mm", stroke_width=3)  # rel to center
    bottom = cy + bbox[3]
    if bottom > BOTTOM_LIMIT:
        cy -= (bottom - BOTTOM_LIMIT)
    # shadow layer
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.text((W // 2, cy + 6), text, font=font, fill=SHADOW,
            anchor="mm", stroke_width=3, stroke_fill=SHADOW)
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, sh)
    d = ImageDraw.Draw(img)
    d.text((W // 2, cy), text, font=font, fill=color,
           anchor="mm", stroke_width=3, stroke_fill=STROKE)
    return img

if os.path.isdir(OUTDIR):
    shutil.rmtree(OUTDIR)
os.makedirs(OUTDIR)

# transparent frame file
blank = Image.new("RGBA", (W, H), (0, 0, 0, 0))
BLANK_PATH = os.path.join(OUTDIR, "_blank.png")
blank.save(BLANK_PATH)

# cache rendered token -> path
cache = {}
def token_path(text):
    if text not in cache:
        p = os.path.join(OUTDIR, "tok_%03d.png" % len(cache))
        render(text).save(p)
        cache[text] = p
    return cache[text]

# frame -> item mapping
def frame_time(fidx):
    return fidx / FPS

# precompute item index for each frame
written = 0
item_idx = 0
for fidx in range(NFRAMES):
    t = (fidx + 0.5) / FPS  # sample mid-frame
    # find active item
    active = None
    # linear-ish; items sorted
    for (s, e, d) in items:
        if s <= t < e:
            active = d
            break
        if s > t:
            break
    dst = os.path.join(OUTDIR, "f%05d.png" % fidx)
    if active is None:
        os.link(BLANK_PATH, dst) if not os.path.exists(dst) else None
    else:
        src = token_path(active)
        os.link(src, dst)
    written += 1

print("items:", len(items))
print("distinct tokens:", len(cache))
print("frames written:", written)
print("highlights among tokens:", sum(1 for t in cache if is_hl(t)))
print("red token list:", sorted([t for t in cache if is_hl(t)]))
