import os

from telegram import Bot, BotCommand

bot = Bot(os.environ["BOT_TOKEN"])

bot.set_my_commands(
    [
        BotCommand("start", "Запуск"),
        BotCommand("confess", "Исповедь"),
        BotCommand("feed", "Лента"),
        BotCommand("digest", "Дайджест"),
        BotCommand("stats", "Статистика"),
        BotCommand("settings", "Настройки"),
    ]
)
print("✅ Меню Telegram обновлено")
