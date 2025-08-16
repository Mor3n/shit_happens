import logging

from telegram import Update
from telegram.ext import ContextTypes


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Telegram error: {context.error}")
    if update and update.message:
        await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")  # noqa: E501
