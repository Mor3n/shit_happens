import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from config.db import get_db

def delete_old_posts():
    try:
        db = get_db()
        cutoff = (datetime.utcnow() - timedelta(hours=48)).isoformat()
        db.execute("DELETE FROM confessions WHERE timestamp < ?", (cutoff,))
        db.commit()
        logging.info("🧹 Старые посты удалены")
    except Exception as e:
        logging.error(f"Ошибка удаления старых постов: {e}")

def run_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_old_posts, "interval", hours=1)
    scheduler.add_job(lambda: logging.info("Фоновая задача выполняется"), "interval", minutes=30)
    scheduler.start()
    logging.info("Планировщик задач запущен")
