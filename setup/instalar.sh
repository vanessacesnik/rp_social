#!/usr/bin/env bash
# Instala tudo que a super-edicao-video-avalanche precisa, em Ubuntu/Debian.
# Serve para VPS e para WSL2 (sao o mesmo sistema).
#
#   bash setup/instalar.sh                  # faster-whisper (rapido na CPU)  <- padrao
#   bash setup/instalar.sh --whisper-oficial  # openai-whisper (puxa torch, ~2.5GB)
#
# Idempotente: rodar de novo nao quebra nada.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$RAIZ/.venv"
WHISPER_OFICIAL=0
[ "${1:-}" = "--whisper-oficial" ] && WHISPER_OFICIAL=1

passo(){ printf "\n\033[1;36m==> %s\033[0m\n" "$1"; }
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"

passo "1/6  Pacotes do sistema"
$SUDO apt-get update -qq
$SUDO apt-get install -y --no-install-recommends \
  ffmpeg python3 python3-venv python3-pip git curl ca-certificates \
  fonts-dejavu-core libgomp1
echo "ffmpeg: $(ffmpeg -version | head -1)"

passo "2/6  Node (o Playwright renderiza os overlays HTML)"
if command -v node >/dev/null 2>&1 && [ "$(node -v | tr -d 'v' | cut -d. -f1)" -ge 18 ]; then
  echo "node $(node -v) ja serve."
else
  curl -fsSL https://deb.nodesource.com/setup_22.x | $SUDO bash -
  $SUDO apt-get install -y nodejs
fi

passo "3/6  Ambiente Python em $VENV"
[ -d "$VENV" ] || python3 -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install --quiet --upgrade pip wheel

passo "4/6  Bibliotecas Python"
pip install --quiet pillow numpy playwright
if [ "$WHISPER_OFICIAL" = "1" ]; then
  echo "openai-whisper (isso puxa o torch, vai demorar)"
  pip install --quiet openai-whisper
else
  echo "faster-whisper (mesmos timestamps, bem mais rapido sem GPU)"
  pip install --quiet faster-whisper
  # o CLI `whisper` que a skill documenta, servido pelo faster-whisper
  install -m 755 "$RAIZ/setup/whisper-faster" "$VENV/bin/whisper-faster"
  ln -sf "$VENV/bin/whisper-faster" "$VENV/bin/whisper"
  echo "comando 'whisper' apontado para o shim (mesmas flags, mesmo JSON)"
fi

passo "5/6  Chromium do Playwright"
playwright install --with-deps chromium

passo "6/6  Conferindo"
python3 - <<'PY'
import importlib
for m in ("PIL", "numpy", "playwright"):
    importlib.import_module(m); print(f"  {m} OK")
PY
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); b.close()
print('  chromium abre OK')"
command -v whisper >/dev/null && echo "  whisper OK ($(command -v whisper))"

cat <<FIM

============================================================
 PRONTO.

 Ative o ambiente em toda sessao nova:

     source $VENV/bin/activate

 Ainda de fora (nao sao coisa de sistema operacional):

   - naia-agent / naia_image  ->  geracao de imagem pela rota OAuth.
     Esperado em /opt/naia-agent ou ~/naia-agent, com o .env.
   - Veo  ->  so para os modelos que ANIMAM b-roll.

 Sem esses dois, o modelo Hyperframe queimado roda inteiro:
 ele e so ffmpeg + Playwright + whisper.

 Confira tudo com:  bash setup/verificar.sh
============================================================
FIM
