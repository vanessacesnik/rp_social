#!/usr/bin/env python3
# Monta uma PARTE da VSL: base (rosto+voz continua) com b-rolls sobrepostos.
# kind 'hf' = motion-graphics a 90% opacidade, 1x, dur=arquivo.
# kind 'char' = personagem cobrindo 100%, 2x (8s->4s), dur=4s. Usa versao -fill (sem faixa preta).
# Voz da base sempre por baixo. Uso: python montar_parte.py <parte>
import os,sys,subprocess
BASE_MOV="/Users/naiarodrigues/Desktop/VSL LIMPA, SEM NENHUMA REPETIÇÃO E SEM BROLL/VSL LIMPA, SEM NENHUMA REPETIÇÃO E SEM BROLL.mov"
ROOT="/Users/naiarodrigues/naia-agent/entregas/vsl-broll"
OLD="/Users/naiarodrigues/naia-agent/entregas/broll-hyperframes"
CH=f"{ROOT}/brolls/char"; HF=f"{ROOT}/brolls/hf"
FF="/opt/homebrew/bin/ffmpeg"; FP="/opt/homebrew/bin/ffprobe"
def dur(f): return float(subprocess.check_output([FP,"-v","error","-show_entries","format=duration","-of","csv=p=0",f]).strip())

# cada insert: (kind, file, start_abs)
PARTS={
 1:(0.0,258.327,[
   ("char",f"{CH}/char-01-fill.mp4",3.0),("hf",f"{HF}/hf-2.mp4",12.6),("char",f"{CH}/char-03-fill.mp4",22.8),
   ("hf",f"{HF}/hf-4.mp4",34.9),("char",f"{CH}/char-05-fill.mp4",42.8),("char",f"{CH}/char-06-fill.mp4",50.9),
   ("hf",f"{HF}/hf-7.mp4",61.9),("hf",f"{HF}/hf-8.mp4",70.3),("hf",f"{HF}/hf-9.mp4",80.9),("hf",f"{HF}/hf-10.mp4",90.7),
   ("hf",f"{HF}/hf-11.mp4",98.9),("hf",f"{HF}/hf-12.mp4",107.0),("hf",f"{HF}/hf-13.mp4",115.6),("hf",f"{HF}/hf-14.mp4",122.4),
   ("hf",f"{HF}/hf-15.mp4",135.0),("hf",f"{HF}/hf-16.mp4",140.6),("hf",f"{HF}/hf-17.mp4",151.4),("hf",f"{HF}/hf-18.mp4",162.2),
   ("hf",f"{HF}/hf-19.mp4",172.6),("hf",f"{HF}/hf-20.mp4",183.9),("hf",f"{HF}/hf-21.mp4",192.5),("hf",f"{HF}/hf-22.mp4",203.4),
   ("hf",f"{HF}/hf-23.mp4",213.6),("hf",f"{HF}/hf-24.mp4",222.7),("hf",f"{HF}/hf-25.mp4",235.2),("hf",f"{HF}/hf-26.mp4",246.5),
   ("char",f"{CH}/char-27-fill.mp4",254.3),
 ]),
 2:(258.327,516.653,[
   ("hf",f"{HF}/hf-30.mp4",258.327),("hf",f"{HF}/hf-31.mp4",270.92),("hf",f"{OLD}/take-07.mp4",279.50),
   ("hf",f"{HF}/hf-43.mp4",289.46),("hf",f"{HF}/hf-44.mp4",304.18),("char",f"{CH}/broll-08-fill.mp4",308.06),
   ("hf",f"{HF}/hf-46.mp4",316.34),("hf",f"{HF}/hf-45.mp4",323.62),("hf",f"{HF}/hf-32.mp4",334.96),
   ("hf",f"{HF}/hf-47.mp4",346.84),("hf",f"{HF}/hf-33.mp4",353.14),("hf",f"{HF}/hf-48.mp4",360.44),
   ("hf",f"{HF}/hf-34.mp4",371.74),("hf",f"{HF}/hf-35.mp4",379.88),("hf",f"{HF}/hf-36.mp4",389.70),
   ("hf",f"{HF}/hf-49.mp4",395.02),("hf",f"{HF}/hf-50.mp4",402.02),("char",f"{CH}/char-101-fill.mp4",406.06),
   ("hf",f"{HF}/hf-37.mp4",412.88),("hf",f"{HF}/hf-51.mp4",420.06),("hf",f"{HF}/hf-38.mp4",430.72),
   ("hf",f"{HF}/hf-39.mp4",437.74),("hf",f"{HF}/hf-52.mp4",449.06),("hf",f"{HF}/hf-53.mp4",453.36),
   ("hf",f"{HF}/hf-40.mp4",459.68),("char",f"{CH}/char-102-fill.mp4",465.96),("hf",f"{OLD}/take-11.mp4",475.22),
   ("hf",f"{HF}/hf-41.mp4",480.58),("hf",f"{HF}/hf-55.mp4",485.96),("hf",f"{HF}/hf-56.mp4",499.38),
   ("hf",f"{HF}/hf-42.mp4",504.72),("hf",f"{HF}/hf-57.mp4",512.74),
 ]),
 3:(516.653,774.980,[
   ("hf",f"{HF}/hf-60.mp4",516.653),("char",f"{CH}/char-01-fill.mp4",523.0),("hf",f"{HF}/hf-61.mp4",527.74),
   ("char",f"{CH}/char-05-fill.mp4",537.94),("hf",f"{HF}/hf-62.mp4",545.74),("hf",f"{HF}/hf-19.mp4",557.58),
   ("char",f"{CH}/char-03-fill.mp4",571.58),("hf",f"{HF}/hf-64.mp4",580.10),("char",f"{CH}/char-204-fill.mp4",598.10),
   ("char",f"{CH}/char-205-fill.mp4",602.68),("hf",f"{HF}/hf-74.mp4",608.50),("hf",f"{HF}/hf-65.mp4",615.80),
   ("char",f"{CH}/char-206-fill.mp4",623.58),("hf",f"{HF}/hf-75.mp4",630.0),("hf",f"{HF}/hf-76.mp4",636.0),
   ("char",f"{CH}/broll-13-fill.mp4",642.52),("char",f"{CH}/char-207-fill.mp4",647.72),("hf",f"{HF}/hf-66.mp4",656.32),
   ("char",f"{CH}/char-27-fill.mp4",666.20),("hf",f"{HF}/hf-67.mp4",675.80),("hf",f"{HF}/hf-68.mp4",691.74),
   ("hf",f"{HF}/hf-69.mp4",703.22),("char",f"{CH}/char-06-fill.mp4",710.30),("hf",f"{HF}/hf-70.mp4",718.12),
   ("hf",f"{HF}/hf-71.mp4",732.50),("hf",f"{HF}/hf-72.mp4",751.10),("char",f"{CH}/char-210-fill.mp4",758.58),
   ("hf",f"{HF}/hf-73.mp4",764.38),
 ]),
 4:(774.980,1033.307,[
   ("hf",f"{HF}/hf-80.mp4",774.980),("hf",f"{HF}/hf-81.mp4",786.42),("hf",f"{HF}/hf-82.mp4",799.52),
   ("hf",f"{HF}/hf-83.mp4",812.90),("hf",f"{HF}/hf-84.mp4",826.74),("hf",f"{HF}/hf-85.mp4",839.48),
   ("char",f"{CH}/char-05-fill.mp4",851.22),("hf",f"{HF}/hf-86.mp4",859.12),("hf",f"{HF}/hf-87.mp4",863.32),
   ("hf",f"{HF}/hf-88.mp4",875.90),("hf",f"{HF}/hf-89.mp4",888.66),("hf",f"{HF}/hf-90.mp4",905.68),
   ("hf",f"{HF}/hf-91.mp4",909.52),("hf",f"{HF}/hf-92.mp4",922.04),("hf",f"{HF}/hf-93.mp4",927.72),
   ("hf",f"{HF}/hf-94.mp4",936.32),("hf",f"{HF}/hf-95.mp4",948.16),("hf",f"{HF}/hf-77.mp4",957.5),
   ("char",f"{CH}/broll-17-fill.mp4",968.48),
   ("hf",f"{HF}/hf-96.mp4",974.36),("char",f"{CH}/char-301-fill.mp4",980.66),("hf",f"{HF}/hf-78.mp4",988.0),("hf",f"{HF}/hf-97.mp4",996.74),
   ("hf",f"{HF}/hf-98.mp4",1008.36),("hf",f"{HF}/hf-99.mp4",1020.52),
 ]),
 5:(1033.307,1291.633,[
   ("hf",f"{HF}/hf-100.mp4",1033.307),("hf",f"{HF}/hf-101.mp4",1047.16),("hf",f"{HF}/hf-102.mp4",1058.36),
   ("hf",f"{HF}/hf-103.mp4",1070.56),("hf",f"{HF}/hf-104.mp4",1084.72),("char",f"{CH}/char-204-fill.mp4",1095.0),
   ("hf",f"{HF}/hf-119.mp4",1101.5),("hf",f"{HF}/hf-105.mp4",1108.82),("hf",f"{HF}/hf-120.mp4",1120.5),
   ("hf",f"{HF}/hf-106.mp4",1132.66),("hf",f"{HF}/hf-107.mp4",1138.80),("hf",f"{HF}/hf-108.mp4",1149.06),
   ("hf",f"{HF}/hf-109.mp4",1160.64),("hf",f"{HF}/hf-110.mp4",1172.76),("hf",f"{HF}/hf-111.mp4",1188.62),
   ("hf",f"{HF}/hf-112.mp4",1206.56),("hf",f"{HF}/hf-113.mp4",1218.46),("hf",f"{HF}/hf-114.mp4",1238.62),
   ("hf",f"{HF}/hf-115.mp4",1248.42),("char",f"{CH}/char-206-fill.mp4",1254.16),("hf",f"{HF}/hf-116.mp4",1262.24),
   ("hf",f"{HF}/hf-117.mp4",1268.26),("hf",f"{HF}/hf-118.mp4",1274.14),("char",f"{CH}/broll-21-fill.mp4",1283.0),
 ]),
}
def main():
    part=int(sys.argv[1]) if len(sys.argv)>1 else 1
    P_START,P_END,INS=PARTS[part]
    inputs=["-ss",str(P_START),"-t",str(P_END-P_START),"-i",BASE_MOV]
    parts=[]; missing=[]
    for kind,f,start in INS:
        if not os.path.exists(f): missing.append(os.path.basename(f)); continue
        parts.append((kind,f,start))
    if missing: print("FALTAM:",missing)
    parts.sort(key=lambda x:x[2])
    FACE=2.5  # rosto fixo entre b-rolls (<=3s garantido)
    PE_REL=P_END-P_START
    starts=[s-P_START for _,_,s in parts]
    filt=[]; idx=1; labels=[]
    for k,(kind,f,start) in enumerate(parts):
        inputs+=["-i",f]; rel=starts[k]
        # janela de exibicao: da frase ate 2.5s antes do proximo broll (ultimo vai ate o fim)
        e=(starts[k+1]-FACE) if k<len(parts)-1 else PE_REL
        if e<=rel+0.3: e=rel+0.3
        if kind=="char":
            v=f"[{idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,setpts=0.5*(PTS-STARTPTS)+{rel}/TB[v{k}]"
        else:
            v=f"[{idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuva420p,colorchannelmixer=aa=0.90,setpts=(PTS-STARTPTS)+{rel}/TB[v{k}]"
        filt.append(v); labels.append((k,rel,e)); idx+=1
    cur="[0:v]"; chain=[]
    for k,s,e in labels:
        out=f"[o{k}]"; chain.append(f"{cur}[v{k}]overlay=enable='between(t,{s:.3f},{e:.3f})':eof_action=repeat:format=auto{out}"); cur=out
    fc=";".join(filt+chain)
    out=f"{ROOT}/PARTE-{part:02d}.mp4"
    cmd=[FF,"-y"]+inputs+["-filter_complex",fc,"-map",cur,"-map","0:a",
         "-c:v","h264_videotoolbox","-b:v","12M","-c:a","aac","-b:a","192k","-r","30",out]
    print(f"montando PARTE {part}: {len(parts)} inserts")
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode!=0: print("ERRO:\n",r.stderr[-1500:]); sys.exit(1)
    print("OK ->",out,f"{os.path.getsize(out)/1048576:.0f}MB dur={dur(out):.1f}s")
if __name__=="__main__": main()
