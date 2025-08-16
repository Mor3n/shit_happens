# app/services/search_service.py

from config.db import get_db

def search_posts(user_id: str, query: str, settings: dict) -> list[dict]:
    """
    Поиск постов по ключевым словам, с учётом настроек пользователя.
    """
    db = get_db()
    sources = settings.get("sources", ["confess", "digest"])
    fuzzy = settings.get("fuzzy", True)

    # Простейший поиск по ключевым словам
    keywords = query.lower().split()
    results = []

    for kw in keywords:
        rows = db.execute(
            "SELECT * FROM confessions WHERE keywords LIKE ? ORDER BY timestamp DESC LIMIT 20",
            (f"%{kw}%",),
        ).fetchall()

        for r in rows:
            post = dict(r)
            if post.get("source") in sources:
                results.append(post)

    # Удаление дубликатов по id
    seen = set()
    unique = []
    for r in results:
        pid = r.get("id")
        if pid and pid not in seen:
            unique.append(r)
            seen.add(pid)

    return unique
