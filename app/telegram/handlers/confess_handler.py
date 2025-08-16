# app/telegram/handlers/confess_handler.py
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

import app.services.confess_service as confess_service
import app.telegram.helpers as helpers
from config.config import Config
from app.services.ai_generate import generate_confession

# Состояние ожидания текста (in-memory)
pending_confess: set[str] = set()


async def confess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /confess — ставим пользователя в режим ввода исповеди."""
    user_id = str(update.effective_user.id)
    pending_confess.add(user_id)
    await helpers.safe_reply(update, context, "📝 Напиши свою исповедь (20–50 символов):")


async def handle_confession_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ловим текст, если юзер в pending_confess."""
    if not update or not getattr(update, "message", None) or not update.message.text:
        return

    user_id = str(update.effective_user.id)
    if user_id not in pending_confess:
        return

    text = update.message.text.strip()
    if len(text) < 20 or len(text) > 50:
        await helpers.safe_reply(update, context, "⚠️ Исповедь должна быть от 20 до 50 символов.")
        return

    try:
        confess_service.save_confession(user_id, text)
        await helpers.safe_reply(update, context, "🙏 Исповедь принята.")

        # --- ИИ-ответ на исповедь ---
        if getattr(Config, "USE_AI_CONFESS_REPLY", False):
            try:
                ai_reply = generate_confession(conn=None, user_id=user_id)
                if ai_reply:
                    await helpers.safe_reply(update, context, ai_reply)
            except Exception:
                pass  # Не валим хендлер, если ИИ не сработал

    except Exception:
        await helpers.safe_reply(update, context, "❌ Ошибка при сохранении.")
    finally:
        pending_confess.discard(user_id)


# --- Экспорт хендлеров для dispatcher ---
command_handler = CommandHandler("confess", confess)
text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confession_text)

__all__ = ["command_handler", "text_handler"]
