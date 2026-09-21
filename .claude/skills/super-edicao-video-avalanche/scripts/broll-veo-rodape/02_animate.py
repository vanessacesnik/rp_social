import base64, json, time, os, urllib.request, urllib.error

# pool de chaves (reusa a varredura do projeto anterior; senão refaz)
KEYS_FILE = "/tmp/roi-edit/gemini_keys.txt"
KEYS = [k.strip() for k in open(KEYS_FILE)] if os.path.exists(KEYS_FILE) else []
KEYS = [k for k in KEYS if k]
IMGDIR = "/tmp/auto-edit/img"; VIDDIR = "/tmp/auto-edit/video"; os.makedirs(VIDDIR, exist_ok=True)

VEO_PROMPT = ("Animate this scene with a LOCKED, STATIC camera: absolutely NO zoom, NO push-in, NO dolly, NO camera "
"movement — framing stays identical, every element fully inside the frame the whole time. Only internal elements move: "
"subtle natural character gestures and hair, holographic panels flicker/glow, data and particles drift, message bubbles "
"stream. Premium 3D cinematic, no text warping, 16:9.")

# OBRIGATÓRIO: trava o Veo de deturpar personagem (já deu merda: lagosta virou formiga no meio do take)
NEG = ("morphing or changing any character's body, limbs, arms, legs, hands or claws; turning the lobster's human child "
"legs into insect or ant legs; insect body, ant legs, extra limbs; changing outfits, faces, skin, colors or logos; "
"altering the scenery or background; adding or removing characters; warping or changing text; camera zoom, push-in, "
"dolly or pan; distortion, melting, identity flicker.")

IDS = [f"w{i:02d}" for i in range(1,12)]
ptr = 0  # ponteiro da chave boa

def submit(wid, key):
    bb = base64.b64encode(open(f"{IMGDIR}/{wid}_16x9.jpg","rb").read()).decode()
    payload = {"instances":[{"prompt":VEO_PROMPT,"image":{"bytesBase64Encoded":bb,"mimeType":"image/jpeg"}}],
               "parameters":{"aspectRatio":"16:9","negativePrompt":NEG}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-fast-generate-preview:predictLongRunning?key={key}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)

def run(wid):
    global ptr
    for off in range(len(KEYS)):
        ki = (ptr + off) % len(KEYS); key = KEYS[ki]
        try:
            op = submit(wid, key)
        except urllib.error.HTTPError as e:
            print(wid,"key",ki,"->",e.code,flush=True); time.sleep(1); continue
        except Exception as e:
            print(wid,"key",ki,"err",str(e)[:60],flush=True); continue
        ptr = ki  # fixa nessa chave boa
        opname = op["name"]; print("OP",wid,"key",ki,flush=True)
        poll = f"https://generativelanguage.googleapis.com/v1beta/{opname}?key={key}"
        for i in range(60):
            time.sleep(10)
            try:
                with urllib.request.urlopen(urllib.request.Request(poll), timeout=60) as r:
                    st = json.load(r)
            except Exception: continue
            if st.get("done"):
                try:
                    uri = st["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
                except Exception:
                    print(wid,"NOURI",json.dumps(st)[:200]); break
                dl = uri + (f"&key={key}" if "?" in uri else f"?key={key}")
                with urllib.request.urlopen(urllib.request.Request(dl), timeout=300) as r:
                    open(f"{VIDDIR}/{wid}.mp4","wb").write(r.read())
                print("SAVED",wid,flush=True); return True
        print(wid,"poll exhausted key",ki)
    print(wid,"ALL KEYS FAILED"); return False

print("keys no pool:", len(KEYS), flush=True)
for wid in IDS:
    run(wid); time.sleep(5)
print("ANIMATE DONE")
