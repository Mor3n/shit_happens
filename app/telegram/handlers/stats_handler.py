# app/telegram/handlers/stats_handler.py

from telegram import Update
from telegram.ext import ContextTypes

from app.services.stats_service import (
    get_total_post_count,
    get_user_post_count,
    get_user_stats,
)
from app.telegram.helpers import safe_reply

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    total = get_total_post_count()
    user_total = get_user_post_count(user_id)
    reactions = get_user_stats(user_id)

    lines = [
        f"📊 Всего постов: {total}",
        f"👤 Ваших постов: {user_total}",
        "",
        "❤️ Реакции:",
    ]
    for k, v in reactions.items():
        lines.append(f"• {k}: {v}")

    await safe_reply(update, context, "\n".join(lines))
