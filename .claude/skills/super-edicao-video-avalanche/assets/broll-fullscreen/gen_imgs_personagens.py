#!/usr/bin/env python3
import os,sys,base64,json,time,traceback
# ROTA (desde 03/08/2026): assinatura ChatGPT do Chefe via OAuth, sem credito de API.
# A OPENAI_API_KEY continua valendo como REDE DE SEGURANCA, dentro do naia_image, e
# entra sozinha se a sessao OAuth cair. 1024x1536 e NATIVO desta rota (sai cravado).
NAIA_HOME = "/opt/naia-agent" if os.path.isdir("/opt/naia-agent") else os.path.expanduser("~/naia-agent")
sys.path.insert(0, NAIA_HOME + "/scripts")
import naia_image
BASE=os.path.expanduser("~/naia-agent/entregas/vsl-broll/brolls/char")
REFS=[f"{BASE}/refs/ref-{n}.png" for n in ("08","13","17","21")]
LOCK=("Match the FOUR Avalanche characters from the reference images EXACTLY (same designs, same proportions, anime ultra-realistic cinematic 3D, premium): "
 "DENDERSON = bald black Brazilian man, full dark beard, black slim blazer over black tee; "
 "NAIA = redhead woman, long wavy copper-red hair, fair porcelain skin, subtle cyan circuit lines on neck/forearms, emerald eyes, fitted black executive blazer; "
 "OPENCLAW = CHIBI cherry-red lobster with a BIG speckled/dimpled bumpy lobster head (NOT a smooth ball, NOT an ant/crab), baby face, huge round black eyes with amber irises, two long thin red antennae, red lobster CLAW hands, tiny chubby child body, black Avalanche hoodie with gold chain; "
 "CLAUDINHO = CHIBI with a BIG rounded ORANGE CUBE/BOX head, matte orange, face = two thick black bracket eyes '>' and '<' (a '>‹' squint), small orange side ear-blocks, NO nose NO mouth, orange hands, tiny child body, black Avalanche hoodie with gold chain (NEVER a lobster, NEVER a human head). "
 "Vertical 9:16 composition. Avalanche command center / navy + red & cyan neon, holographic HUD dashboards, red neon chevron 'A'. Cinematic. ABSOLUTELY NO text, no words, no captions, no logos with letters, no watermark.")
SCENES=[
 (1,"funcionario-ia-24h","The four characters working tirelessly like a 24/7 team at glowing holographic consoles: Naia operating a big dashboard, Claudinho orchestrating screens, OpenClaw at another console, Denderson at center with arms crossed, confident and proud, overseeing the operation at night."),
 (3,"agente-100pct-seu","Denderson at center receiving in his hands a glowing floating cyan-gold AI core orb (sense of ownership/power); Naia presents the orb beside him; Claudinho and OpenClaw stand proudly. Heroic possessive mood."),
 (5,"ia-trabalha-por-mim","Denderson seated like a confident boss in the foreground while his AI squad works FOR him around and behind: Naia typing on glowing screens, Claudinho commanding holograms, OpenClaw handling a panel; floating app icons (WhatsApp, Instagram, Gmail) as soft holograms."),
 (6,"agente-no-ar-em-minutos","A brand-new AI agent being 'born' from a glowing cyan-gold portal at center; Claudinho joyfully presses one single big glowing button; OpenClaw cheers with claws up; Naia presents the emerging agent with an open hand; Denderson nods approving. Easy one-click magical vibe."),
 (27,"o-outro-caminho","Dramatic hero shot, dawn light breaking after darkness: the four characters step forward confidently toward the camera as 'the other way' / the turning point; Denderson leading center, Naia at his side, Claudinho and OpenClaw in front; behind them the command center with red neon chevron 'A'. Hopeful, cinematic rim light."),
]
def main():
    print(f"[imgs] {len(SCENES)} imagens (gpt-image-2 + 4 refs, rota OAuth)",flush=True)
    refs=[r for r in REFS if os.path.exists(r)]
    os.makedirs(f"{BASE}/img", exist_ok=True)
    for idx,label,scene in SCENES:
        out=f"{BASE}/img/img-{idx:02d}.png"
        prompt=f"{scene}\n\n{LOCK}"
        for a in range(3):
            try:
                r=naia_image.gerar(prompt, out, size="1024x1536", quality="high", refs=refs)
                print(f"[{idx:02d}] OK {label} {os.path.getsize(out)//1024}KB "
                      f"{r['dimensoes'][0]} rota={r['rota']}",flush=True)
                break
            except Exception as e:
                print(f"[{idx:02d}] retry {a}: {str(e)[:140]}",flush=True); time.sleep(15)
        else:
            print(f"[{idx:02d}] FALHOU {label}",flush=True)
    print("[imgs] FIM",flush=True)
if __name__=="__main__":
    try: main()
    except Exception: traceback.print_exc(); sys.exit(1)
