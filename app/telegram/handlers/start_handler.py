# app/telegram/handlers/start_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from app.telegram.helpers import safe_reply


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Исповедь", callback_data="goto_confess")],
        [
            InlineKeyboardButton("📰 Лента", callback_data="goto_feed"),
            InlineKeyboardButton("📬 Дайджест", callback_data="goto_digest"),
        ],
        [
            InlineKeyboardButton("⚙ Настройки", callback_data="goto_settings"),
            InlineKeyboardButton("📊 Статистика", callback_data="goto_stats"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await safe_reply(
        update,
        context,
        "👋 Добро пожаловать в 'Хуйня случается'!\nВыбери, что хочешь сделать:",
        reply_markup=reply_markup,
    )
