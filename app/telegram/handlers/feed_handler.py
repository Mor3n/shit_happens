# app/telegram/handlers/feed_handler.py

from telegram import Update
from telegram.ext import ContextTypes

from app.services.feed_service import get_feed
from app.telegram.helpers import safe_reply, build_pagination_buttons, build_reaction_buttons

async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    page = 1
    posts = get_feed(page)

    if not posts:
        await safe_reply(update, context, "Нет постов.")
        return

    for p in posts:
        text = p.get("text")
        post_id = p.get("id")
        if text and post_id:
            markup = build_reaction_buttons(post_id)
            await safe_reply(update, context, text, reply_markup=markup)
