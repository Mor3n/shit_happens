import logging

from config.db import get_db


def get_feed(page=1, per_page=5):
    try:
        offset = (page - 1) * per_page
        db = get_db()
        rows = db.execute(
            "SELECT id, text, hashtags, reactions, timestamp FROM confessions ORDER BY timestamp DESC LIMIT ? OFFSET ?",  # noqa: E501
            (per_page, offset),
        ).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logging.error(f"Error in get_feed: {e}")
        raise
