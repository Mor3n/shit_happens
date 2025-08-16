# app/telegram/dispatcher.py

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from app.telegram.error_handler import error_handler
from app.telegram.handlers.button_handler import button_handler
from app.telegram.handlers.digest_handler import digest
from app.telegram.handlers.feed_handler import feed
from app.telegram.handlers.settings_handler import settings
from app.telegram.handlers.start_handler import start
from app.telegram.handlers.stats_handler import stats
from app.telegram.handlers.confess_handler import confess, handle_confession_text

def build_application(token: str):
    app = (
        ApplicationBuilder()
        .updater(None)       # критично для Python 3.13
        .job_queue(None)     # отключаем PTB JobQueue
        .token(token)
        .build()
    )
    app.add_handler(CommandHandler("confess", confess))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confession_text))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("feed", feed))
    app.add_handler(CommandHandler("digest", digest))
    app.add_handler(CommandHandler("settings", settings))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_error_handler(error_handler)

    return app
