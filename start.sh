#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"
mkdir -p logs

: "${ENV:=local}"
: "${PYTHONUNBUFFERED:=1}"
export PYTHONUNBUFFERED

DOTENV_FILE=".env"

detect_os() {
  local u
  u="$(uname -s 2>/dev/null || echo unknown)"
  case "$u" in
    Linux) grep -qi microsoft /proc/version && echo "WSL" || echo "Linux" ;;
    Darwin) echo "macOS" ;;
    MINGW*|MSYS*|CYGWIN*) echo "Windows" ;;
    *) echo "Unknown" ;;
  esac
}
OS="$(detect_os)"

choose_python() {
  if command -v python3 >/dev/null 2>&1; then echo "python3"
  elif command -v python >/dev/null 2>&1; then echo "python"
  elif [[ "$OS" == "Windows" ]] && command -v py >/dev/null 2>&1; then echo "py -3"
  else echo ""
  fi
}
read -r -a PYCMD <<<"$(choose_python)"
[[ ${#PYCMD[@]} -eq 0 ]] && { echo "❌ Python not found"; exit 1; }

[[ -f "$DOTENV_FILE" ]] && set -o allexport && source "$DOTENV_FILE" && set +o allexport

: "${PORT:=5000}"

# === Установка зависимостей ===
if [[ -f requirements.txt ]]; then
  echo "📦 Installing Python dependencies..."
  PIP_DISABLE_PIP_VERSION_CHECK=1 "${PYCMD[@]}" -m pip install --no-input -r requirements.txt
fi

# Установка psycopg2-binary, если нет
if ! "${PYCMD[@]}" -c "import psycopg2" >/dev/null 2>&1; then
  echo "📦 Installing psycopg2-binary..."
  PIP_DISABLE_PIP_VERSION_CHECK=1 "${PYCMD[@]}" -m pip install --no-input psycopg2-binary
fi
# ==============================

if [[ "${ENV}" == "local" ]]; then
  echo "🌐 Starting Quick Tunnel for local dev on http://localhost:${PORT} ..."
  TUNNEL_LOG="logs/tunnel.log"
  cloudflared tunnel --url "http://localhost:${PORT}" >"$TUNNEL_LOG" 2>&1 &
  TUNNEL_PID=$!
  trap 'kill "$TUNNEL_PID" >/dev/null 2>&1 || true' EXIT

  echo "⏳ Waiting for public URL..."
  PUBLIC_URL=""
  for _ in {1..30}; do
    if grep -Eo 'https://[-a-z0-9]+\.trycloudflare\.com' "$TUNNEL_LOG" >/dev/null 2>&1; then
      PUBLIC_URL="$(grep -Eo 'https://[-a-z0-9]+\.trycloudflare\.com' "$TUNNEL_LOG" | head -n1)"
      break
    fi
    sleep 0.5
  done

  if [[ -z "${PUBLIC_URL}" ]]; then
    echo "❌ Failed to obtain public URL from cloudflared"
    exit 1
  fi

  KEEPALIVE_URL="$PUBLIC_URL"

  if [[ -f "$DOTENV_FILE" ]]; then
    sed -i.bak -E "s|^PUBLIC_URL=.*|PUBLIC_URL=${PUBLIC_URL}|" "$DOTENV_FILE" || true
    sed -i.bak -E "s|^KEEPALIVE_URL=.*|KEEPALIVE_URL=${KEEPALIVE_URL}|" "$DOTENV_FILE" || true
    rm -f "${DOTENV_FILE}.bak"
  else
    echo "PUBLIC_URL=${PUBLIC_URL}" >> "$DOTENV_FILE"
    echo "KEEPALIVE_URL=${KEEPALIVE_URL}" >> "$DOTENV_FILE"
  fi

  export PUBLIC_URL KEEPALIVE_URL
fi

# === Webhook ===
set -o allexport && source "$DOTENV_FILE" && set +o allexport
if [[ -n "${TELEGRAM_TOKEN:-}" && -n "${PUBLIC_URL:-}" ]]; then
  WEBHOOK_URL="${PUBLIC_URL%/}/webhook"
  echo "🔗 Registering Telegram webhook: $WEBHOOK_URL"
  curl -s "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook" \
       -d "url=${WEBHOOK_URL}" \
    | tee logs/webhook_set.json
  echo "📡 Current webhook info:"
  curl -s "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo" \
    | tee logs/webhook_info.json
else
  echo "⚠️  TELEGRAM_TOKEN or PUBLIC_URL not set — webhook skipped"
fi
# ===============

echo "ℹ️ OS=${OS}"
echo "ℹ️ PYTHON=${PYCMD[*]}"
echo "ℹ️ ENV=${ENV}"
echo "ℹ️ PORT=${PORT}"
echo "ℹ️ PUBLIC_URL=${PUBLIC_URL:-<empty>}"
echo "ℹ️ KEEPALIVE_URL=${KEEPALIVE_URL:-<empty>}"
echo "📄 Tunnel log: $(realpath logs/tunnel.log)"
echo "📄 App log:    $(realpath logs/app.log)"

run_app() {
  local bind="0.0.0.0:${PORT}"
  if [[ "$OS" == "Windows" ]]; then
    if "${PYCMD[@]}" -c "import waitress" >/dev/null 2>&1; then
      exec "${PYCMD[@]}" -m waitress --listen="${bind}" run:app | tee logs/app.log
    else
      PIP_DISABLE_PIP_VERSION_CHECK=1 "${PYCMD[@]}" -m pip install --no-input waitress >/dev/null
      exec "${PYCMD[@]}" -m waitress --listen="${bind}" run:app | tee logs/app.log
    fi
  else
    if command -v gunicorn >/dev/null 2>&1; then
      exec gunicorn -c gunicorn.conf.py run:app --bind "${bind}" | tee logs/app.log
    elif "${PYCMD[@]}" -c "import gunicorn" >/dev/null 2>&1; then
      exec "${PYCMD[@]}" -m gunicorn -c gunicorn.conf.py run:app --bind "${bind}" | tee logs/app.log
    elif "${PYCMD[@]}" -c "import uvicorn" >/dev/null 2>&1; then
      exec "${PYCMD[@]}" -m uvicorn run:app --host 0.0.0.0 --port "${PORT}" | tee logs/app.log
    else
      exec "${PYCMD[@]}" -m flask --app run:app run --host 0.0.0.0 --port "${PORT}" | tee logs/app.log
    fi
  fi
}

run_app
