import sys
import os
import asyncio
import logging
import threading
import requests
import traceback
import hmac
from flask import Blueprint, jsonify, request
from telegram import Update

# === Фикс путей для корректных импортов внутри PTB-хендлеров ===
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

bp = Blueprint("webhook", __name__)

_state = {
    "app": None,
    "loop": None,
    "thread": None,
    "started": False,
}

# ===== INTERNAL HELPERS =====

def _ensure_loop_started():
    if _state["loop"] and _state["thread"] and _state["thread"].is_alive():
        return
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=loop.run_forever, name="ptb-loop", daemon=True)
    t.start()
    _state["loop"] = loop
    _state["thread"] = t
    logging.info("✅ Async loop started in background thread")


def _ensure_app_started():
    _ensure_loop_started()
    from app.telegram.dispatcher import build_application
    if _state["app"] is None:
        token = os.getenv("BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError("BOT_TOKEN is not set")
        _state["app"] = build_application(token)

    if not _state["started"]:
        loop = _state["loop"]
        app = _state["app"]

        async def _startup():
            logging.info("🚀 PTB Application initializing…")
            await app.initialize()
            await app.start()
            logging.info("🤖 PTB Application started (webhook mode)")

        fut = asyncio.run_coroutine_threadsafe(_startup(), loop)
        try:
            fut.result(timeout=20)
        except Exception:
            logging.error("💥 PTB startup failed:\n%s", traceback.format_exc())
            return
        _state["started"] = True


def _get_app_and_loop():
    _ensure_app_started()
    return _state["app"], _state["loop"]


def _log_future_result(fut):
    try:
        fut.result()
    except Exception:
        logging.error("💥 process_update crashed:\n%s", traceback.format_exc())

# ===== ROUTE =====

@bp.post("/telegram/webhook")
def telegram_webhook():
    try:
        logging.info("=== ВХОД В WEBHOOK (FULL-UNLOCK) ===")
        logging.info("Headers: %r", dict(request.headers))

        try:
            raw_body = request.get_data(as_text=True)
            logging.info("Raw body: %r", raw_body)
        except Exception as e:
            logging.warning("Не удалось прочитать тело: %s", e)

        try:
            data = request.get_json(force=True, silent=False)
        except Exception:
            logging.error("💥 JSON parse failed:\n%s", traceback.format_exc())
            data = None

        logging.info("📩 Incoming update (parsed): %s", data)

        app, loop = _get_app_and_loop()
        if not app or not loop:
            logging.error("💥 PTB app/loop not ready")
            return "", 200

        if data:
            try:
                update = Update.de_json(data, app.bot)
                fut = asyncio.run_coroutine_threadsafe(app.process_update(update), loop)
                fut.add_done_callback(_log_future_result)
            except Exception:
                logging.error("💥 Update processing failed:\n%s", traceback.format_exc())

        return "", 200

    except Exception:
        logging.error("💥 Webhook handler crashed (outer):\n%s", traceback.format_exc())
        return "", 200

# ===== WEBHOOK REGISTRATION =====

def ensure_webhook():
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    public_url = os.getenv("PUBLIC_URL", "").strip().rstrip("/")
    webhook_secret = os.getenv("WEBHOOK_SECRET", "").strip()

    if not bot_token or not public_url:
        logging.warning("⚠ BOT_TOKEN или PUBLIC_URL не заданы — webhook не будет зарегистрирован")
        return

    if not public_url.startswith("https://"):
        logging.error("❌ PUBLIC_URL должен начинаться с https:// — Telegram иначе откажет")
        return

    target = f"{public_url}/telegram/webhook"

    try:
        info = requests.get(
            f"https://api.telegram.org/bot{bot_token}/getWebhookInfo", timeout=10
        ).json()
        current = info.get("result", {}).get("url", "")
        if current != target:
            logging.info(f"🔄 Регистрируем webhook: {target}")
        else:
            logging.info("✅ URL совпадает — обновляем секрет (idempotent)")

        payload = {"url": target}
        if webhook_secret:
            payload["secret_token"] = webhook_secret

        r = requests.post(
            f"https://api.telegram.org/bot{bot_token}/setWebhook",
            json=payload,
            timeout=10,
        )
        logging.info(f"Telegram ответил: {r.status_code} {r.text}")

    except Exception:
        logging.exception("❌ Ошибка регистрации webhook")


def init_webhook_auto():
    if os.getenv("AUTO_REGISTER_WEBHOOK", "").lower() == "true":
        ensure_webhook()
