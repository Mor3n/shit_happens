from telegram import Update
from telegram.ext import ContextTypes

from app.services.settings_service import get_settings
from app.telegram.helpers import safe_reply


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    prefs = get_settings(user_id)
    defaults = {
        "language": "ru",
        "format": "short",
        "intensity": "5",
        "topic": "default"
    }
    text = "\n".join(f"{k}: {prefs.get(k, defaults[k])}" for k in defaults)

    await safe_reply(update, context, text)
