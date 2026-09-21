#!/usr/bin/env python3
# Fetch OFFICIAL brand logos as SVG from Simple Icons (via jsDelivr) and inject a fill color,
# saving to GEN_WORK/logos/<slug>.svg so elements/imgcard.html (and chip enrichments) can use them.
# Only fetch a logo for a brand that the narration actually names or that is truly on screen;
# never invent a citation. Default glyph fill is white (reads on the dark chips); pass slug:HEX
# to force a brand color. Instagram gets its gradient from the .ig class in imgcard.html.
#
# Usage:  GEN_WORK=/abs/workspace python3 fetch_logos.py claude instagram whatsapp meta openai googlegemini
# Common Simple Icons slugs: claude, openai, googlegemini, meta, instagram, whatsapp, github,
#   slack, notion, obsidian, figma, framer, googledrive, x, linkedin, youtube.
import os, sys, re, urllib.request

WORK = os.environ.get("GEN_WORK") or os.getcwd()
OUT = os.path.join(WORK, "logos")
os.makedirs(OUT, exist_ok=True)
CDN = "https://cdn.jsdelivr.net/npm/simple-icons/icons/{}.svg"


def fetch(spec):
    slug, _, hexv = spec.partition(":")
    fill = ("#" + hexv) if hexv else "#FFFFFF"
    try:
        with urllib.request.urlopen(CDN.format(slug), timeout=30) as r:
            svg = r.read().decode("utf-8")
    except Exception as e:
        print(f"[ERR] {slug}: {e} (confira o slug no simpleicons.org)", file=sys.stderr)
        return False
    svg = re.sub(r"<title>.*?</title>", "", svg, flags=re.S)     # drop title
    if "<svg " in svg and "fill=" not in svg.split(">", 1)[0]:   # inject fill on the <svg> tag
        svg = svg.replace("<svg ", f'<svg fill="{fill}" ', 1)
    open(os.path.join(OUT, f"{slug}.svg"), "w").write(svg)
    print(f"[OK] {slug} -> {OUT}/{slug}.svg  fill={fill}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: GEN_WORK=... fetch_logos.py <slug[:HEX]> ...")
    ok = all(fetch(s) for s in sys.argv[1:])
    print("LOGOS_DONE" if ok else "SOME_LOGO_FAILED")
