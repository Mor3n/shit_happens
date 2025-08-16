import json
import logging
import os
from datetime import datetime

from app.services.nlp_service import analyze_text
from config.db import get_db
from app.models.confession import Confession


def save_confession(user_id, text):
    """Сохранение исповеди и возврат [Confession] или [] при ошибке"""
    try:
        # Быстрая проверка на пустые значения — тесты ждут []
        if not user_id or not text or not text.strip():
            return []

        analysis = analyze_text(text)
        hashtags = analysis["hashtags"]
        keywords = analysis["keywords"]
        emotion = analysis["emotion"]
        reactions = "{}"

        db = get_db()
        db.execute(
            "INSERT INTO confessions (user_id, text, hashtags, reactions, timestamp, keywords, emotion) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                user_id,
                text,
                " ".join(hashtags),
                reactions,
                datetime.now(UTC).isoformat(),
                " ".join(keywords),
                emotion,
            ),
        )
        db.commit()

        update_user_keywords(user_id, keywords)

        row = db.execute(
            "SELECT * FROM confessions WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()

        if row:
            return [Confession(**dict(row))]
        return []
    except Exception as e:
        logging.error(f"Error in save_confession: {e}")
        return []


def update_user_keywords(user_id, new_keywords):
    """Обновление профиля пользователя с новыми ключевыми словами"""
    try:
        path = "data/keyword_profiles.json"
        if not os.path.exists(path):
            profiles = {}
        else:
            with open(path, "r", encoding="utf-8") as f:
                profiles = json.load(f)

        user_profile = profiles.get(str(user_id), {"keywords": []})
        existing = set(user_profile["keywords"])
        updated = list(existing.union(new_keywords))

        profiles[str(user_id)] = {"keywords": updated}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error in update_user_keywords: {e}")
        raise
