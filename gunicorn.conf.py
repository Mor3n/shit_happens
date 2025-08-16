import logging
import os

workers = int(os.getenv("WEB_CONCURRENCY", "1")) or 1
threads = int(os.getenv("THREADS", "1")) or 1
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120")) or 120
loglevel = os.getenv("LOGLEVEL", "info")
errorlog = "-"
accesslog = "-"


def post_worker_init(worker):
    logging.info("🚀 Gunicorn worker ready — starting background services…")
    from run import start_background_once

    start_background_once()
