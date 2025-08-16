# app/telegram/handlers/digest_handler.py

from flask import current_app as app
from telegram import ReplyKeyboardMarkup

from app.config import Config
from app.db import get_db
from app.ai.client import AIClient
from app.ai.prompts import system_prompt, developer_prompt
from app.telegram.utils import safe_reply, build_context

# --- Базовые дефолты, если ИИ выключен или произошла ошибка ---
base_text = "Пока ИИ-ответы выключены, вот тебе базовый дайджест."
button = ReplyKeyboardMarkup(
    [["Обновить дайджест", "Главное меню"]],
    resize_keyboard=True
)


async def digest(update, context):
    """
    Хендлер дайджеста: отдает базовый текст или «очеловеченную» версию через ИИ.
    """
    user_id = update.effective_user.id

    # 3) Если флаг ИИ выключен — просто отдать базовый текст
    if not Config.USE_AI_RESPONSES:
        await safe_reply(update, context, base_text, reply_markup=button)
        return

    # 4) Пытаемся “очеловечить” текст через ИИ
    try:
        # Формируем контекст
        with app.app_context():
            db = get_db()
            ctx = build_context(db, user_id=user_id, history_limit=3)

        # Готовим промпты и запрос
        client = AIClient()
        sys_p = system_prompt()
        dev_p = developer_prompt(tone=Config.AI_TONE, max_len=Config.AI_MAX_LEN)
        ai_text = (
            f"Сформируй короткий, живой дайджест на основе этого текста:\n\n{base_text}"
        )

        # Запускаем генерацию в отдельном потоке, чтобы не блокировать event loop
        import asyncio
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(
            None, lambda: client.generate(sys_p, dev_p, ai_text, ctx)
        )

        text = (res.text or "").strip()
        if not text:
            text = base_text

        # Жёсткая отсечка длины (страховка)
        if len(text) > Config.AI_MAX_LEN:
            text = text[: Config.AI_MAX_LEN - 1] + "…"

        await safe_reply(update, context, text, reply_markup=button)

    except Exception as e:
        # Логируем, но не даем боту упасть
        app.logger.error(f"digest handler error: {e}")
        await safe_reply(update, context, base_text, reply_markup=button)
