#!/usr/bin/env bash
# Verifica se esta máquina aguenta a super-edicao-video-avalanche.
# Não instala nada, não altera nada: só olha e reporta.
# Uso:  bash setup/verificar.sh

ok(){ printf "  \033[32mOK\033[0m    %s\n" "$1"; }
falta(){ printf "  \033[31mFALTA\033[0m %s\n" "$1"; }
aviso(){ printf "  \033[33mAVISO\033[0m %s\n" "$1"; }
titulo(){ printf "\n\033[1m%s\033[0m\n" "$1"; }

# Se o venv do repositorio existe, usa ele: senao o checador acusa falta do que
# esta instalado la dentro e da alarme falso.
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -z "${VIRTUAL_ENV:-}" ] && [ -f "$RAIZ/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  . "$RAIZ/.venv/bin/activate"
  VENV_AUTO=1
fi

echo "======================================================"
echo " VERIFICACAO DE AMBIENTE - super-edicao-video-avalanche"
echo "======================================================"
[ "${VENV_AUTO:-0}" = "1" ] && echo " (usando o venv em $RAIZ/.venv)"

titulo "MAQUINA"
echo "  sistema   : $(. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME" || uname -s)"
echo "  kernel    : $(uname -r)"
CPUS=$(nproc 2>/dev/null || echo "?")
echo "  vCPU      : $CPUS"
if [ -r /proc/cpuinfo ]; then
  echo "  processador: $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2- | sed 's/^ //')"
fi
if command -v free >/dev/null 2>&1; then
  echo "  memoria   : $(free -h | awk '/^Mem:/{print $2" total, "$7" disponivel"}')"
fi
echo "  disco     : $(df -h . | awk 'NR==2{print $4" livre de "$2}')"
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "  GPU       : $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null | head -1)"
else
  echo "  GPU       : nenhuma NVIDIA detectada (whisper vai de CPU)"
fi
grep -qi microsoft /proc/version 2>/dev/null && echo "  ambiente  : WSL detectado"

titulo "O QUE O PIPELINE PRECISA"
for b in ffmpeg ffprobe python3 node npx git; do
  if command -v "$b" >/dev/null 2>&1; then
    ok "$b  ($($b --version 2>&1 | head -1 | cut -c1-58))"
  else
    falta "$b"
  fi
done

titulo "BIBLIOTECAS PYTHON"
if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY'
import importlib, sys
alvos = [("PIL","Pillow"),("numpy","numpy"),("whisper","openai-whisper"),
         ("faster_whisper","faster-whisper"),("playwright","playwright")]
for mod, nome in alvos:
    try:
        importlib.import_module(mod)
        print(f"  \033[32mOK\033[0m    {nome}")
    except ImportError:
        print(f"  \033[31mFALTA\033[0m {nome}")
PY
else
  falta "python3 (nao da pra checar as bibliotecas)"
fi

titulo "GERACAO DE IMAGEM (naia_image)"
NAIA=""
for d in /opt/naia-agent "$HOME/naia-agent"; do
  [ -d "$d" ] && NAIA="$d" && break
done
if [ -n "$NAIA" ]; then
  ok "pasta naia-agent em $NAIA"
  [ -f "$NAIA/scripts/naia_image.py" ] && ok "naia_image.py encontrado" || falta "$NAIA/scripts/naia_image.py"
  [ -f "$NAIA/.env" ] && ok "arquivo .env presente" || aviso "sem .env em $NAIA (a rota OAuth precisa dele)"
else
  falta "pasta naia-agent (procurei em /opt/naia-agent e ~/naia-agent)"
  aviso "sem ela, so o modelo Hyperframe queimado roda de ponta a ponta"
fi

titulo "NAVEGADOR PARA OS OVERLAYS"
if command -v npx >/dev/null 2>&1; then
  if python3 -c "import playwright" 2>/dev/null; then
    python3 - <<'PY' 2>/dev/null || aviso "playwright instalado, mas sem navegador que abra (rode: playwright install chromium)"
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); b.close()
print("  \033[32mOK\033[0m    chromium do playwright abre")
PY
  else
    falta "playwright (e o navegador dele)"
  fi
fi

titulo "VEREDITO"
[ "$CPUS" != "?" ] && [ "$CPUS" -lt 4 ] 2>/dev/null && \
  aviso "$CPUS vCPU: encode e transcricao vao ser lentos. Use faster-whisper e encode um de cada vez."
[ "$CPUS" != "?" ] && [ "$CPUS" -ge 4 ] 2>/dev/null && \
  ok "$CPUS vCPU: da pra trabalhar."
LIVRE=$(df -BG . | awk 'NR==2{gsub("G","",$4); print $4}')
[ -n "$LIVRE" ] && [ "$LIVRE" -lt 20 ] 2>/dev/null && \
  aviso "${LIVRE}GB livres: um master de 10min mais os intermediarios passam disso. Libere espaco."
echo
echo "Manda essa saida inteira pro Claude que ele monta o resto."
