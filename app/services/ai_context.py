from __future__ import annotations
from typing import Any


def _row_as_dict(row: Any) -> dict:
    try:
        return dict(row)
    except Exception:
        if isinstance(row, (list, tuple)):
            keys = [
                "id", "user_id", "text", "hashtags",
                "reactions", "timestamp", "keywords", "emotion"
            ]
            return {k: (row[i] if i < len(row) else None) for i, k in enumerate(keys)}
        return {}


def _get_user_settings(db, user_id: str) -> dict:
    try:
        row = db.execute(
            "SELECT * FROM user_settings WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        if not row:
            return {}
        return _row_as_dict(row)
    except Exception:
        return {}


def _get_last_confessions(db, user_id: str, limit: int = 3) -> list[dict]:
    try:
        cur = db.execute(
            "SELECT id, text, hashtags, timestamp, keywords, emotion "
            "FROM confessions WHERE user_id = ? "
            "ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        rows = cur.fetchall() or []
    except Exception:
        return []

    result = []
    for r in rows:
        d = _row_as_dict(r)
        result.append({
            "id": d.get("id"),
            "text": d.get("text"),
            "hashtags": d.get("hashtags"),
            "timestamp": d.get("timestamp"),
            "keywords": d.get("keywords"),
            "emotion": d.get("emotion"),
        })
    return result


def _get_post_by_id(db, post_id: int | None) -> dict | None:
    if not post_id:
        return None
    try:
        row = db.execute(
            "SELECT id, user_id, text, hashtags, timestamp, keywords, emotion "
            "FROM confessions WHERE id = ?",
            (post_id,),
        ).fetchone()
    except Exception:
        return None
    if not row:
        return None
    d = _row_as_dict(row)
    return {
        "id": d.get("id"),
        "user_id": d.get("user_id"),
        "text": d.get("text"),
        "hashtags": d.get("hashtags"),
        "timestamp": d.get("timestamp"),
        "keywords": d.get("keywords"),
        "emotion": d.get("emotion"),
    }


def build_context(
    db,
    user_id: str,
    post_id: int | None = None,
    history_limit: int = 3
) -> dict:
    """
    Формирует контекст для AI:
    {
        "user": {...},
        "history": [...],
        "post": {...} | None
    }
    """
    if not db or not user_id:
        return {"user": {}, "history": [], "post": None}

    raw_settings = _get_user_settings(db, user_id)
    # Оставляем только те поля, которые нужны тестам/AI
    allowed_keys = {"topic", "intensity", "format", "language"}
    settings = {k: v for k, v in raw_settings.items() if k in allowed_keys}

    lang = settings.get("language", "ru")
    history = _get_last_confessions(db, user_id, history_limit)
    post = _get_post_by_id(db, post_id)

    return {
        "user": {
            "id": str(user_id),
            "lang": lang,
            "settings": settings,
        },
        "history": history,
        "post": post,
    }


def system_prompt(settings: dict) -> str:
    topic = settings.get("topic", "general")
    intensity = settings.get("intensity", "neutral")
    format_ = settings.get("format", "text")
    language = settings.get("language", "en")

    return (
        f"You are an AI assistant. Respond in {language}.\n"
        f"Topic: {topic}. Intensity: {intensity}. Format: {format_}.\n"
        f"Be concise, relevant, and helpful."
    )
