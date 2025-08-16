import json
import logging

from config.db import get_db


def get_global_stats():
    try:
        db = get_db()
        rows = db.execute(
            "SELECT tag, SUM(count) as total FROM stats GROUP BY tag ORDER BY total DESC LIMIT 10"  # noqa: E501
        ).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logging.error(f"Error in get_global_stats: {e}")
        raise


def get_user_stats(user_id):
    try:
        db = get_db()
        rows = db.execute(
            "SELECT reactions FROM confessions WHERE user_id = ?", (user_id,)
        ).fetchall()
        reaction_count = {}
        for row in rows:
            reactions = json.loads(row["reactions"])
            for k, v in reactions.items():
                reaction_count[k] = reaction_count.get(k, 0) + v
        return reaction_count
    except Exception as e:
        logging.error(f"Error in get_user_stats: {e}")
        raise


def get_total_post_count():
    try:
        db = get_db()
        return db.execute("SELECT COUNT(*) FROM confessions").fetchone()[0]
    except Exception as e:
        logging.error(f"Error in get_total_post_count: {e}")
        raise


def get_user_post_count(user_id):
    try:
        db = get_db()
        return db.execute(
            "SELECT COUNT(*) FROM confessions WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
    except Exception as e:
        logging.error(f"Error in get_user_post_count: {e}")
        raise
