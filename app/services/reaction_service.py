import json
import logging

from config.db import get_db


def _row_get(row, key, idx=0):
    """
    Достаёт значение из строки результата для разных бэкендов:
    - dict/Row (sqlite3.Row, psycopg RealDict) -> row[key]
    - tuple/list -> row[idx]
    """
    if row is None:
        return None
    try:
        # dict-like (имеет .keys и доступ по строковому ключу)
        if hasattr(row, "keys") and (
            key in row.keys() if hasattr(row, "keys") else False
        ):
            return row[key]
        if isinstance(row, dict):
            return row.get(key)
    except Exception:
        pass
    # fallback: позиционный доступ
    try:
        return row[idx]
    except Exception:
        return None


def _as_reactions(value):
    """
    Приводит reactions к dict:
    - JSON-строка -> dict
    - dict -> dict
    - None/пусто -> {}
    - иное -> попытка json.loads(str(value)) -> dict
    """
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, (bytes, bytearray)):
        try:
            return json.loads(value.decode("utf-8"))
        except Exception:
            return {}
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return {}
        try:
            return json.loads(value)
        except Exception:
            return {}
    try:
        return json.loads(str(value))
    except Exception:
        return {}


def add_reaction(post_id, reaction_type):
    try:
        db = get_db()
        row = db.execute(
            "SELECT reactions FROM confessions WHERE id = ?", (post_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"Post not found: id={post_id}")

        reactions = _as_reactions(_row_get(row, "reactions", 0))
        reactions[reaction_type] = reactions.get(reaction_type, 0) + 1

        db.execute(
            "UPDATE confessions SET reactions = ? WHERE id = ?",
            (json.dumps(reactions, ensure_ascii=False), post_id),
        )
        db.commit()
        return reactions
    except Exception as e:
        logging.error(f"Error in add_reaction: {e}")
        raise
