import base64, json, time, os, urllib.request, urllib.error

KEYS = [k.strip() for k in open("/tmp/roi-edit/gemini_keys.txt") if k.strip()]
IMG = "/tmp/cta/cta_9x16.jpg"
OUT = "/tmp/cta/cta_take.mp4"

PROMPT = ("Animate this promo END-CARD with a LOCKED, STATIC camera (no zoom, no pan, no dolly). The TEXT stays 100% "
"FROZEN and identical. Bring the scene to life with clearly NOTICEABLE, energetic motion: the lobster mascot does a "
"confident playful fighter move — a slight bounce, raising and flexing its claws, antennae swaying; DENDERSON and NAIA "
"shift into confident power poses with subtle head and shoulder movement and flowing hair; the central asterisk energy "
"shield PULSES and crackles with strong energy bursts and electric arcs; embers and glowing particles stream upward "
"energetically; the holographic floor rings rotate and glow brighter. Dynamic, hype, premium cinematic, 9:16.")

NEG = ("changing, warping, morphing or rewriting any text, letters or numbers; changing the characters' bodies, faces, "
"limbs, arms, legs, hands or claws; turning the lobster's human child legs into insect or ant legs; insect body, ant "
"legs, extra limbs; altering outfits, colors, logos or the scenery; adding or removing any character or text; camera "
"zoom, push-in, pan or dolly; distortion, melting, identity flicker.")

bb = base64.b64encode(open(IMG,"rb").read()).decode()
payload = {"instances":[{"prompt":PROMPT,"image":{"bytesBase64Encoded":bb,"mimeType":"image/jpeg"}}],
           "parameters":{"aspectRatio":"9:16","negativePrompt":NEG}}

def submit(key):
    url=f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-fast-generate-preview:predictLongRunning?key={key}"
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=120) as r: return json.load(r)

for ki,key in enumerate(KEYS):
    try:
        op=submit(key)
    except urllib.error.HTTPError as e:
        print("key",ki,"->",e.code,flush=True); time.sleep(1); continue
    except Exception as e:
        print("key",ki,"err",str(e)[:60],flush=True); continue
    print("OP key",ki,op["name"],flush=True)
    poll=f"https://generativelanguage.googleapis.com/v1beta/{op['name']}?key={key}"
    for i in range(60):
        time.sleep(10)
        try:
            with urllib.request.urlopen(urllib.request.Request(poll),timeout=60) as r: st=json.load(r)
        except Exception: continue
        if st.get("done"):
            uri=st["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
            dl=uri+(f"&key={key}" if "?" in uri else f"?key={key}")
            with urllib.request.urlopen(urllib.request.Request(dl),timeout=300) as r: open(OUT,"wb").write(r.read())
            print("SAVED",OUT,flush=True); raise SystemExit
    print("poll exhausted key",ki)
print("ALL KEYS FAILED")
