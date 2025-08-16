import logging
from config.db import get_db

DEFAULTS = {
    "topic": "confess",
    "intensity": "medium",
    "format": "short",
    "language": "en"
}

ALLOWED_KEYS = set(DEFAULTS.keys())


def get_settings(user_id: str) -> dict:
    try:
        db = get_db()
        row = db.execute(
            "SELECT * FROM user_settings WHERE user_id = ?", (user_id,)
        ).fetchone()

        if row:
            return dict(row)

        db.execute(
            """
            INSERT INTO user_settings (user_id, topic, intensity, format, language)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, DEFAULTS["topic"], DEFAULTS["intensity"], DEFAULTS["format"], DEFAULTS["language"]),
        )
        db.commit()
        return {**DEFAULTS, "user_id": user_id}

    except Exception as e:
        logging.error(f"[get_settings] user_id={user_id} error: {e}")
        raise


def update_setting(user_id: str, key: str, value: str) -> dict:
    try:
        if key not in ALLOWED_KEYS:
            raise ValueError(f"Invalid setting key: {key}")

        db = get_db()
        query = f"UPDATE user_settings SET {key} = ? WHERE user_id = ?"
        db.execute(query, (value, user_id))
        db.commit()

        return get_settings(user_id)

    except Exception as e:
        logging.error(f"[update_setting] user_id={user_id}, key={key}, error: {e}")
        raise
