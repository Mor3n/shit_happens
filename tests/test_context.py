import sqlite3
import os
import pytest
from contextlib import closing
from app.services.ai_context import build_context, system_prompt
from app.services.ai_generate import generate_confession

DB_PATH = "tests/test_context.db"

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    os.makedirs("tests", exist_ok=True)
    # Важно: используем closing(...), т.к. sqlite3.Connection сам по себе не закрывается при выходе из with
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id TEXT PRIMARY KEY,
                topic TEXT,
                intensity TEXT,
                format TEXT,
                language TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS confessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                text TEXT,
                hashtags TEXT,
                reactions TEXT,
                timestamp TEXT,
                keywords TEXT,
                emotion TEXT
            );
        """)

        cursor.execute("DELETE FROM user_settings;")
        cursor.execute("DELETE FROM confessions;")

        cursor.execute("""
            INSERT INTO user_settings (user_id, topic, intensity, format, language)
            VALUES (?, ?, ?, ?, ?)
        """, ("u1", "confess", "high", "short", "ru"))

        cursor.execute("""
            INSERT INTO confessions (user_id, text, hashtags, reactions, timestamp, keywords, emotion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "u1",
            "тестовая исповедь",
            "#тест",
            "{}",
            "2025-08-14T00:00:00Z",
            "тестовая",
            "радость"
        ))

        conn.commit()


def test_build_context():
    # Важно: closing(...) гарантирует закрытие соединения
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        ctx = build_context(conn, "u1")

        assert ctx["user"]["lang"] == "ru"
        assert ctx["user"]["settings"] == {
            "topic": "confess",
            "intensity": "high",
            "format": "short",
            "language": "ru"
        }
        assert isinstance(ctx["history"], list)
        assert len(ctx["history"]) == 1
        assert "тестовая исповедь" in ctx["history"][0]["text"]


def test_system_prompt():
    settings = {
        "topic": "confess",
        "intensity": "high",
        "format": "short",
        "language": "ru"
    }
    prompt = system_prompt(settings)
    for key in settings.values():
        assert key in prompt


def test_generate_confession():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        text = generate_confession(conn, "u1")

        assert isinstance(text, str)
        assert len(text) > 10
        assert any(word in text.lower() for word in ["исповедь", "я"])
