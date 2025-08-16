# scripts/set_webhook.py
import os
import sys
import time
import requests

def _mask(s: str) -> str:
    if not s:
        return s
    return s[:6] + "..." + s[-4:] if len(s) > 12 else "***"

def main():
    token = (os.getenv("BOT_TOKEN") or "").strip()
    if not token:
        print("❌ BOT_TOKEN not set")
        sys.exit(1)

    public = (os.getenv("PUBLIC_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").strip().rstrip("/")
    if not public or not public.startswith("https://"):
        print(f"❌ PUBLIC_URL/RENDER_EXTERNAL_URL must be HTTPS, got: {public!r}")
        sys.exit(1)

    secret = (os.getenv("WEBHOOK_SECRET") or "").strip()
    webhook_url = f"{public}/telegram/webhook"

    print(f"🌐 PUBLIC_URL: {public}")
    print(f"🔐 BOT_TOKEN: {_mask(token)}")
    if secret:
        print("🛡️ Using WEBHOOK_SECRET")

    set_url = f"https://api.telegram.org/bot{token}/setWebhook"
    info_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"

    payload = {"url": webhook_url}
    if secret:
        payload["secret_token"] = secret

    ok = False
    for attempt in range(1, 6):
        try:
            resp = requests.post(set_url, json=payload, timeout=15)
            print(f"➡️  setWebhook [{attempt}/5]: {resp.status_code} {resp.text}")
            data = resp.json()
            if data.get("ok"):
                ok = True
                break
        except Exception as e:
            print(f"⚠️  setWebhook failed: {e}")
        time.sleep(min(2 ** attempt, 10))

    try:
        info = requests.get(info_url, timeout=10)
        print(f"ℹ️  getWebhookInfo: {info.status_code} {info.text}")
    except Exception as e:
        print(f"⚠️  getWebhookInfo failed: {e}")

    print("✅ Webhook set" if ok else "⚠️ Webhook not confirmed; continuing")
    sys.exit(0)

if __name__ == "__main__":
    main()
