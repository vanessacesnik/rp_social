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
# Presenca de pasta NAO e prova: o playwright exige o build exato da versao dele, e um
# chromium de outra versao no disco passa no teste de pasta e falha na hora de abrir.
# A unica checagem que vale e tentar abrir.
abre_chromium(){
  python3 - <<'PYCHK' 2>/dev/null
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); b.close()
PYCHK
}
CHROMIUM_OK=0
if abre_chromium; then
  echo "chromium ja abre, nao preciso baixar."
  CHROMIUM_OK=1
elif playwright install --with-deps chromium && abre_chromium; then
  echo "chromium baixado e abrindo."
  CHROMIUM_OK=1
else
  # rede fechada e o caso comum em VPS: cai para o chromium do sistema (apt)
  echo "download bloqueado ou build incompativel; tentando o chromium do sistema..."
  $SUDO apt-get install -y --no-install-recommends chromium 2>/dev/null \
    || $SUDO apt-get install -y --no-install-recommends chromium-browser 2>/dev/null || true
  if command -v chromium >/dev/null 2>&1 || command -v chromium-browser >/dev/null 2>&1; then
    export PLAYWRIGHT_BROWSERS_PATH=0
    if abre_chromium; then
      echo "usando o chromium do sistema (PLAYWRIGHT_BROWSERS_PATH=0)."
      grep -q "PLAYWRIGHT_BROWSERS_PATH" "$VENV/bin/activate" \
        || echo "export PLAYWRIGHT_BROWSERS_PATH=0" >> "$VENV/bin/activate"
      echo "  (export gravado no activate do venv)"
      CHROMIUM_OK=1
    fi
  fi
fi
if [ "$CHROMIUM_OK" != "1" ]; then
  printf "\n\033[33mAVISO\033[0m  fiquei sem chromium.\n"
  echo "  Todo o resto foi instalado. Corte, legenda queimada e encode funcionam;"
  echo "  os overlays HTML (faixa, cards, infograficos) nao renderizam sem ele."
  echo "  Saidas: liberar cdn.playwright.dev no firewall e rodar 'playwright install chromium',"
  echo "  ou instalar o chromium pelo apt e exportar PLAYWRIGHT_BROWSERS_PATH=0."
fi

passo "6/6  Conferindo"
python3 - <<'PY'
import importlib
for m in ("PIL", "numpy", "playwright"):
    importlib.import_module(m); print(f"  {m} OK")
PY
[ "$CHROMIUM_OK" = "1" ] && echo "  chromium OK" || echo "  chromium PENDENTE (veja o aviso acima)"
command -v ffmpeg  >/dev/null && echo "  ffmpeg OK"
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
