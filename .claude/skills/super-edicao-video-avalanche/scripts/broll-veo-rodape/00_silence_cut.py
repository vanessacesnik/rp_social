import subprocess, re, sys

SRC = "/tmp/auto-edit/cutvid.mp4"
OUT = "/tmp/auto-edit/cutvid_tight.mp4"
PAD = 0.10          # mantém uma folguinha em cada borda pra não comer palavra
NOISE = "-30dB"; DUR_MIN = "0.35"

# duração total
d = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of",
     "default=noprint_wrappers=1:nokey=1",SRC],capture_output=True,text=True).stdout.strip())

# detecta silêncios
out = subprocess.run(["ffmpeg","-i",SRC,"-af",f"silencedetect=noise={NOISE}:d={DUR_MIN}","-f","null","-"],
                     capture_output=True,text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
ends   = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]

# intervalos de silêncio (encolhidos pelo PAD em cada lado -> só corta o miolo do silêncio)
sil = []
for s,e in zip(starts,ends):
    a=s+PAD; b=e-PAD
    if b>a: sil.append((a,b))

# keep = complemento dos silêncios
keep=[]; cur=0.0
for a,b in sil:
    if a>cur: keep.append((cur,a))
    cur=b
if cur<d: keep.append((cur,d))
keep=[(a,b) for a,b in keep if b-a>0.05]

newdur=sum(b-a for a,b in keep)
print(f"orig={d:.2f}s  keep_segments={len(keep)}  newdur={newdur:.2f}s  cortado={d-newdur:.2f}s",flush=True)

# filtro select/concat
vsel="+".join(f"between(t,{a:.3f},{b:.3f})" for a,b in keep)
asel=vsel
fc=(f"[0:v]select='{vsel}',setpts=N/FRAME_RATE/TB[v];"
    f"[0:a]aselect='{asel}',asetpts=N/SR/TB[a]")
cmd=["ffmpeg","-y","-i",SRC,"-filter_complex",fc,"-map","[v]","-map","[a]",
     "-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",OUT]
r=subprocess.run(cmd,stderr=subprocess.PIPE)
if r.returncode: print("FAIL\n",r.stderr.decode()[-1500:]); sys.exit(1)
print("OK",OUT,flush=True)
