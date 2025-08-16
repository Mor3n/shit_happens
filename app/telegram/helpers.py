# app/telegram/helpers.py

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes


async def safe_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup=None,
):
    """
    Универсальная отправка сообщения:
    - работает и для Message-апдейтов, и для CallbackQuery (inline-кнопки),
    - не падает, если update.message == None.
    """
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id:
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


def build_pagination_buttons(current_page: int, max_pages: int = 5) -> InlineKeyboardMarkup:
    """Создаёт inline-кнопки пагинации."""
    buttons = []

    if current_page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page:{current_page - 1}"))

    if current_page < max_pages:
        buttons.append(InlineKeyboardButton("➡️ Вперёд", callback_data=f"page:{current_page + 1}"))

    return InlineKeyboardMarkup([buttons]) if buttons else None


def build_reaction_buttons(post_id: int) -> InlineKeyboardMarkup:
    """Создаёт inline-кнопки реакций для поста."""
    reactions = ["❤️", "😂", "😢", "🔥", "🤮"]
    buttons = [
        InlineKeyboardButton(emoji, callback_data=f"react:{post_id}:{emoji}")
        for emoji in reactions
    ]
    return InlineKeyboardMarkup([buttons])
