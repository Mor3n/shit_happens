# config/db.py
from flask import g
from config import Config
from config.db_manager import DBManager

try:
    import psycopg  # type: ignore
except ImportError:
    psycopg = None

# Глобальная ссылка на текущее соединение (опционально, для совместимости)
db = None


def _is_psycopg_conn(conn) -> bool:
    return psycopg is not None and conn.__class__.__module__.startswith("psycopg")


def _seed_if_empty(conn) -> None:
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT 1 FROM confessions LIMIT 1")
            row = cur.fetchone()
        except Exception:
            return
        if not row:
            try:
                cur.execute(
                    "INSERT INTO confessions (user_id, text, hashtags, reactions, timestamp, keywords, emotion) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("seed", "seed", "", "{}", "1970-01-01T00:00:00Z", "", ""),
                )
            except Exception:
                cur.execute(
                    "INSERT INTO confessions (user_id, text, hashtags, reactions, timestamp, keywords, emotion) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    ("seed", "seed", "", "{}", "1970-01-01T00:00:00Z", "", ""),
                )
            conn.commit()
        cur.close()
    except Exception:
        pass


def _ensure_sqlite_schema(conn) -> None:
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='confessions'"
        )
        exists = cur.fetchone()
        if not exists:
            cur.executescript(
                """
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
                CREATE TABLE IF NOT EXISTS user_settings (user_id TEXT PRIMARY KEY);
                CREATE TABLE IF NOT EXISTS stats (tag TEXT, count INTEGER);
                CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT);
                """
            )
            conn.commit()
        else:
            cur.execute("PRAGMA table_info(confessions)")
            cols = {r[1] for r in cur.fetchall()}
            for col in ("keywords", "emotion"):
                if col not in cols:
                    cur.execute(f"ALTER TABLE confessions ADD COLUMN {col} TEXT")
                    conn.commit()
        cur.close()
    except Exception:
        pass
    _seed_if_empty(conn)


def _ensure_postgres_schema(conn) -> None:
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS confessions (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                text TEXT,
                hashtags TEXT,
                reactions TEXT,
                timestamp TEXT,
                keywords TEXT,
                emotion TEXT
            );
            CREATE TABLE IF NOT EXISTS user_settings (user_id TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS stats (tag TEXT, count INTEGER);
            CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT);
            """
        )
        conn.commit()
        cur.close()
    except Exception:
        pass
    _seed_if_empty(conn)


class _QmarkCursorAdapter:
    def __init__(self, cursor):
        self._cur = cursor

    def __getattr__(self, name):
        return getattr(self._cur, name)

    def execute(self, query, params=None, *args, **kwargs):
        if isinstance(query, str):
            query = query.replace("?", "%s")
        return self._cur.execute(query, params, *args, **kwargs)


class _QmarkConnAdapter:
    def __init__(self, conn):
        self._conn = conn

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def execute(self, query, params=None, *args, **kwargs):
        if isinstance(query, str):
            query = query.replace("?", "%s")
        return self._conn.execute(query, params, *args, **kwargs)

    def cursor(self, *args, **kwargs):
        cur = self._conn.cursor(*args, **kwargs)
        return _QmarkCursorAdapter(cur)

    def close(self):
        return self._conn.close()


def get_db():
    """Возвращает подключение из flask.g, либо создаёт новое"""
    global db
    if "db" not in g:
        db_manager = DBManager(Config.DB_URI)
        conn = db_manager.connect()
        if _is_psycopg_conn(conn):
            _ensure_postgres_schema(conn)
            g.db = _QmarkConnAdapter(conn)
        else:
            _ensure_sqlite_schema(conn)
            g.db = conn
        db = g.db  # синхронизация с глобальной переменной
    return g.db


def close_db(exception):
    """Закрывает подключение при завершении контекста"""
    global db
    conn = g.pop("db", None)
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass
    db = None


def init_db(app):
    """Регистрирует хук для автозакрытия соединения"""
    app.teardown_appcontext(close_db)
