# app/telegram/utils.py
import logging
from telegram.error import TelegramError

def safe_reply(update, context, text, reply_markup=None):
    """
    Безопасно отправляет ответ пользователю.
    Не роняет хендлер, если Telegram вернул ошибку.
    """
    try:
        if update and update.effective_chat:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=reply_markup
            )
        logging.warning("safe_reply: no effective_chat in update")
    except TelegramError as e:
        logging.error("Telegram API error in safe_reply: %s", e)
    except Exception as e:
        logging.exception("Unexpected error in safe_reply")

def build_context(db, user_id: int, history_limit: int = 3):
    """
    Собирает последние history_limit сообщений пользователя из базы.
    Формирует список dict'ов {'role': ..., 'content': ...} для AI.
    """
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT role, content FROM messages WHERE user_id = ? "
            "ORDER BY created_at DESC LIMIT ?",
            (user_id, history_limit)
        )
        rows = cur.fetchall()
        # Возвращаем в обратном порядке — от старых к новым
        ctx = [{"role": r[0], "content": r[1]} for r in reversed(rows)]
        return ctx
    except Exception:
        logging.exception("Failed to build context for user_id=%s", user_id)
        return []
