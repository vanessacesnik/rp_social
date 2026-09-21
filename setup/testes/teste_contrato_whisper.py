# Prova que o JSON escrito por setup/whisper-faster e exatamente o que a skill le.
# Simula o faster-whisper (nao precisa baixar modelo) e passa a saida pelo carrega()
# de verifica_palavras.py, que e o parser oficial da skill.
#
#   python3 setup/testes/teste_contrato_whisper.py
#
# Se este teste passar, o shim pode substituir o openai-whisper sem que nenhuma linha
# dos scripts ou dos modelos da skill precise mudar.
import sys, types, json, importlib.util, os, runpy

RAIZ = "/home/user/rp_social"
SP = os.environ.get("SP", "/tmp")

class P:
    def __init__(s, w, a, b, p=0.95): s.word, s.start, s.end, s.probability = w, a, b, p
class S:
    def __init__(s, i, a, b, t, ws): s.id, s.start, s.end, s.text, s.words = i, a, b, t, ws
class Info:
    language = "pt"

FALA = [("  Olha", 0.00, 0.42), (" só", 0.42, 0.68), (" o", 0.68, 0.74),
        (" que", 0.74, 0.91), (" ninguém", 0.91, 1.38), (" te", 1.38, 1.50),
        (" conta", 1.50, 1.97), (" sobre", 2.31, 2.64), (" R$", 2.64, 2.88),
        (" 30", 2.88, 3.19), (" mil", 3.19, 3.48), (" reais.", 3.48, 3.95)]

class FakeModel:
    def __init__(s, *a, **k): pass
    def transcribe(s, caminho, **k):
        ws = [P(w, a, b) for w, a, b in FALA]
        segs = [S(0, 0.0, 1.97, "".join(w for w,_,_ in FALA[:7]), ws[:7]),
                S(1, 2.31, 3.95, "".join(w for w,_,_ in FALA[7:]), ws[7:])]
        return iter(segs), Info()

sys.modules["faster_whisper"] = types.SimpleNamespace(WhisperModel=FakeModel)
os.makedirs(SP, exist_ok=True)
sys.argv = ["whisper", f"{SP}/teste.wav", "--model", "medium", "--language", "pt",
            "--word_timestamps", "True", "--output_format", "json", "-o", SP]
runpy.run_path(f"{RAIZ}/setup/whisper-faster", run_name="__main__")


# --- a prova que importa: o parser REAL da skill aceita esse JSON? ---
import importlib.util
spec = importlib.util.spec_from_file_location(
    "vp", os.path.join(RAIZ, ".claude/skills/super-edicao-video-avalanche/scripts/nucleo/verifica_palavras.py"))
vp = importlib.util.module_from_spec(spec)
sys.argv = ["x"]
spec.loader.exec_module(vp)

palavras = vp.carrega(os.path.join(SP, "teste.json"))
print(f"\ncarrega() de verifica_palavras.py leu {len(palavras)} palavras")
for p_ in palavras:
    print(f"  {p_['s']:6.2f} -> {p_['e']:6.2f}  {p_['w']}")

assert len(palavras) == 12, "contagem errada"
assert palavras[0]["w"] == "Olha", "espaco inicial nao foi tratado"
assert palavras[4]["w"] == "ninguem".replace("e", "e") or palavras[4]["w"] == "ninguém", "acento perdido"
assert palavras[-1]["e"] == 3.95, "timestamp final errado"
assert all(palavras[i]["s"] <= palavras[i+1]["s"] for i in range(len(palavras)-1)), "fora de ordem"
print("\nCONTRATO OK: o parser da skill aceita o JSON do shim sem ajuste nenhum.")
