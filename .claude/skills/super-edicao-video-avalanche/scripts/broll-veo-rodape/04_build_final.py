import subprocess, os

BASE = "/tmp/auto-edit/cutvid_tight.mp4"     # já com cortes de roteiro + silêncio
VID = "/tmp/auto-edit/video"
CTA = "/Users/naiarodrigues/Desktop/EDIÇÃO DE VÍDEO/CTA-FINAL-FIXO/CTA_TAKE_FIXO_1080x1920.mp4"
MUSIC = "/Users/naiarodrigues/DENDERSON MACS/musica de suspense.MP3"
OUT_HD = "/tmp/auto-edit/output/FINAL_COMPLETO_1080.mp4"
OUT_4K = "/tmp/auto-edit/output/FINAL_COMPLETO_4K.mp4"

def dur(p):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of",
        "default=noprint_wrappers=1:nokey=1",p],capture_output=True,text=True).stdout.strip())

D = dur(BASE); cta = dur(CTA); XF = 0.7; total = D + cta - XF
IDS = [f"w{i:02d}" for i in range(1,12)]
SEG = D/len(IDS)
print(f"D={D:.2f} seg={SEG:.2f} cta={cta:.2f} total={total:.2f}",flush=True)

inputs=["-i",BASE]
for wid in IDS: inputs += ["-i", f"{VID}/{wid}.mp4"]
inputs += ["-i",CTA,"-i",MUSIC]
cta_idx=len(IDS)+1; mus_idx=len(IDS)+2

fc=[]
fc.append(f"[0:v]crop=1080:1312:0:400,setsar=1,fps=30,format=yuv420p[pres]")
labels=""
for idx in range(1,len(IDS)+1):
    fc.append(f"[{idx}:v]trim=0:{SEG:.5f},setpts=PTS-STARTPTS,scale=1080:602,"
              f"pad=1080:608:0:6:color=0xE63946,fps=30,setsar=1,format=yuv420p[s{idx}]")
    labels+=f"[s{idx}]"
fc.append(f"{labels}concat=n={len(IDS)}:v=1:a=0[strip]")
fc.append(f"[pres][strip]vstack=2,settb=AVTB[wv]")
fc.append(f"[{cta_idx}:v]fps=30,scale=1080:1920,setsar=1,format=yuv420p,settb=AVTB[cta]")
fc.append(f"[wv][cta]xfade=transition=fade:duration={XF}:offset={D-XF:.2f}[vout]")
fc.append(f"[0:a]apad=pad_dur={cta-XF+0.05:.2f}[sp]")
fc.append(f"[{mus_idx}:a]atrim=0:{total:.2f},asetpts=PTS-STARTPTS,"
          f"loudnorm=I=-34:TP=-6:LRA=6,volume=0.38,"
          f"afade=t=in:st=0:d=1.2,afade=t=out:st={total-1.5:.2f}:d=1.5[bg]")
fc.append(f"[sp][bg]amix=inputs=2:duration=first:normalize=0[aout]")
filtergraph=";".join(fc)

cmd=["ffmpeg","-y",*inputs,"-filter_complex",filtergraph,"-map","[vout]","-map","[aout]",
     "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",OUT_HD]
print("=== HD ===",flush=True)
r=subprocess.run(cmd,stderr=subprocess.PIPE)
if r.returncode: print("HD FAIL\n",r.stderr.decode()[-2500:]); raise SystemExit
print("HD OK",flush=True)
r2=subprocess.run(["ffmpeg","-y","-i",OUT_HD,"-vf","scale=2160:3840:flags=lanczos","-c:v","libx264",
     "-preset","medium","-crf","18","-pix_fmt","yuv420p","-c:a","copy",OUT_4K],stderr=subprocess.PIPE)
if r2.returncode: print("4K FAIL\n",r2.stderr.decode()[-2000:]); raise SystemExit
print("4K OK",OUT_4K,flush=True)
