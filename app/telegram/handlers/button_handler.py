# app/telegram/handlers/button_handler.py

from telegram import Update
from telegram.ext import ContextTypes

from app.services.digest_service import generate_digest
from app.telegram.handlers.feed_handler import feed
from app.telegram.handlers.digest_handler import digest
from app.telegram.handlers.settings_handler import settings
from app.telegram.handlers.stats_handler import stats
from app.telegram.handlers.start_handler import start
from app.telegram.helpers import safe_reply, build_pagination_buttons
from app.services.feed_service import get_feed
from app.services.reaction_service import add_reaction

# Ключевая правка: импортируем pending_confess, чтобы помечать юзера
from app.telegram.handlers.confess_handler import pending_confess


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = str(update.effective_user.id)

    if data == "refresh_digest":
        text = generate_digest(user_id)
        await query.edit_message_text(
            text=text,
            reply_markup=query.message.reply_markup,
        )

    elif data == "goto_confess":
        # ВАЖНО: ставим флаг ожидания исповеди для юзера
        pending_confess.add(user_id)
        # Выравниваем формулировку под проверку в confess_handler (символы, не слова)
        await safe_reply(update, context, "📝 Напиши свою исповедь (20–50 символов):")

    elif data == "goto_feed":
        await feed(update, context)

    elif data == "goto_digest":
        await digest(update, context)

    elif data == "goto_settings":
        await settings(update, context)

    elif data == "goto_stats":
        await stats(update, context)

    elif data == "goto_start":
        await start(update, context)

    elif data.startswith("page:"):
        try:
            page = int(data.split(":")[1])
            posts = get_feed(page)
            texts = [p.get("text") for p in posts if p.get("text")]
            text = "\n\n".join(texts) if texts else "Нет постов."
            markup = build_pagination_buttons(page)
            await query.edit_message_text(text=text, reply_markup=markup)
        except Exception:
            await safe_reply(update, context, "❌ Ошибка при загрузке страницы.")

    elif data.startswith("react:"):
        try:
            _, post_id, reaction = data.split(":", 2)
            add_reaction(int(post_id), reaction)
            await query.answer(f"Реакция учтена: {reaction}")
        except Exception:
            await query.answer("❌ Ошибка при обработке реакции.")

    else:
        await safe_reply(update, context, "❓ Неизвестная команда кнопки.")
