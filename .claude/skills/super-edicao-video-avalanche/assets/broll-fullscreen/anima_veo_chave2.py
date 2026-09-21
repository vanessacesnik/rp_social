import os,time,json,subprocess
from google import genai
from google.genai import types
ENV=os.path.expanduser("~/naia-agent/.env")
def k2():
    for l in open(ENV):
        if l.startswith("GOOGLE_AI_API_KEY_2="): return l.strip().split("=",1)[1]
BASE=os.path.expanduser("~/naia-agent/entregas/vsl-broll/brolls/char")
plan={p["idx"]:p for p in json.load(open(BASE+"/plan-p3.json"))}
g=genai.Client(api_key=k2())
for idx in [205,206,207,210]:
    png=f"{BASE}/img/img-{idx}.png"; mp4=f"{BASE}/char-{idx}.mp4"; fill=f"{BASE}/char-{idx}-fill.mp4"
    if os.path.exists(fill) and os.path.getsize(fill)>100000: print(f"[{idx}] ja ok",flush=True); continue
    for _ in range(40):
        if os.path.exists(png): break
        time.sleep(8)
    if not os.path.exists(png): print(f"[{idx}] sem img",flush=True); continue
    done=False
    for a in range(4):
        try:
            img=types.Image(image_bytes=open(png,"rb").read(),mime_type="image/png")
            op=g.models.generate_videos(model="models/veo-3.1-fast-generate-preview",prompt=plan[idx]["veo"],image=img,
                config=types.GenerateVideosConfig(aspect_ratio="9:16",number_of_videos=1,
                    negative_prompt="face change, character redesign, deformed, smooth ball head, ant, crab, text, subtitle, watermark, fast motion",person_generation="allow_adult"))
            t0=time.time()
            while not op.done:
                time.sleep(8); op=g.operations.get(op)
                if time.time()-t0>600: break
            vids=getattr(getattr(op,'response',None),"generated_videos",None) or []
            if vids:
                g.files.download(file=vids[0].video); vids[0].video.save(mp4)
                cr=os.popen(f'/opt/homebrew/bin/ffmpeg -ss 2 -t 1.5 -i "{mp4}" -vf cropdetect=24:2:0 -f null - 2>&1 | grep -o "crop=[0-9:]*" | tail -1').read().strip() or "crop=720:1040:0:120"
                os.system(f'/opt/homebrew/bin/ffmpeg -y -i "{mp4}" -vf "{cr},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1" -c:v h264_videotoolbox -b:v 14M -an "{fill}" >/dev/null 2>&1')
                print(f"[{idx}] OK + fill",flush=True); os.system(f'/usr/bin/open "{fill}"'); done=True; break
            print(f"[{idx}] vazio retry {a}",flush=True); time.sleep(8)
        except Exception as e:
            print(f"[{idx}] err {str(e)[:110]}",flush=True); time.sleep(12)
    if not done:
        # fallback Ken Burns 8s
        os.system(f'/opt/homebrew/bin/ffmpeg -y -loop 1 -r 30 -t 8 -i "{png}" -vf "scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,zoompan=z=\'min(1.12,1.0+0.0005*on)\':d=1:x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':s=1080x1920:fps=30,setsar=1" -frames:v 240 -c:v h264_videotoolbox -b:v 14M -an "{fill}" >/dev/null 2>&1')
        print(f"[{idx}] fallback kenburns",flush=True); os.system(f'/usr/bin/open "{fill}"')
print("FIM veo p3 rest",flush=True)
