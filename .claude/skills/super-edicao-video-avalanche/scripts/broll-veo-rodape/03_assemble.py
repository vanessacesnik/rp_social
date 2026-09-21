import subprocess, os, sys

BASE = "/tmp/auto-edit/cutvid.mp4"      # vídeo cortado, já legendado
VID = "/tmp/auto-edit/video"
OUT_HD = "/tmp/auto-edit/output/FINAL2_1080.mp4"
OUT_4K = "/tmp/auto-edit/output/FINAL2_4K.mp4"
os.makedirs("/tmp/auto-edit/output", exist_ok=True)

# crop do apresentador: remove teto morto. Ajustável via argv.
CROP_Y = int(sys.argv[1]) if len(sys.argv) > 1 else 400   # quanto cortar do topo
PRES_H = 1312                                              # altura do apresentador no canvas
STRIP_H = 1920 - PRES_H                                    # 608
STRIP_W = 1080

IDS = [f"w{i:02d}" for i in range(1,12)]
DUR = 83.938
SEG = DUR / len(IDS)

inputs = ["-i", BASE]
for wid in IDS:
    inputs += ["-i", f"{VID}/{wid}.mp4"]

fc = []
# apresentador: crop 1080xPRES_H começando em CROP_Y (remove faixa acima da cabeça)
fc.append(f"[0:v]crop=1080:{PRES_H}:0:{CROP_Y},setsar=1[pres]")
# faixa b-roll
labels = ""
for idx in range(1, len(IDS)+1):
    fc.append(
        f"[{idx}:v]trim=0:{SEG:.5f},setpts=PTS-STARTPTS,scale={STRIP_W}:{STRIP_H-6},"
        f"pad={STRIP_W}:{STRIP_H}:0:6:color=0xE63946,fps=30,setsar=1,format=yuv420p[s{idx}]"
    )
    labels += f"[s{idx}]"
fc.append(f"{labels}concat=n={len(IDS)}:v=1:a=0[strip]")
# empilha apresentador (topo) + b-roll (rodapé)
fc.append(f"[pres][strip]vstack=2[v]")
filtergraph = ";".join(fc)

cmd = ["ffmpeg","-y",*inputs,"-filter_complex",filtergraph,"-map","[v]","-map","0:a",
       "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",OUT_HD]
print("=== HD ===",flush=True)
r=subprocess.run(cmd,stderr=subprocess.PIPE)
if r.returncode: print("HD FAIL\n",r.stderr.decode()[-2500:]); raise SystemExit
print("HD OK",OUT_HD,flush=True)

cmd2=["ffmpeg","-y","-i",OUT_HD,"-vf","scale=2160:3840:flags=lanczos","-c:v","libx264","-preset","medium",
      "-crf","18","-pix_fmt","yuv420p","-c:a","copy",OUT_4K]
print("=== 4K ===",flush=True)
r2=subprocess.run(cmd2,stderr=subprocess.PIPE)
if r2.returncode: print("4K FAIL\n",r2.stderr.decode()[-2500:]); raise SystemExit
print("4K OK",OUT_4K,flush=True)
