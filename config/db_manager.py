# config/db_manager.py
import json
import os
import shutil
import sqlite3
import atexit
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import psycopg  # psycopg3
    from psycopg.rows import dict_row
except Exception:
    psycopg = None  # может отсутствовать локально

# Реестр открытых соединений, чтобы гарантированно закрыть всё на выходе
_OPEN_CONNS: list = []


def _close_conn(conn):
    try:
        conn.close()
    except Exception:
        pass
    # удалить из реестра, если там есть
    try:
        _OPEN_CONNS.remove(conn)
    except ValueError:
        pass


def _register_conn(conn):
    _OPEN_CONNS.append(conn)
    return conn


def _close_all_conns():
    # Закрыть всё, что забыли закрыть вручную
    for conn in _OPEN_CONNS[:]:
        try:
            conn.close()
        except Exception:
            pass
    _OPEN_CONNS.clear()


atexit.register(_close_all_conns)


class DBManager:
    def __init__(
        self,
        uri: Optional[str] = None,
        local_db_path: Optional[str] = None,
        backup_dir: Optional[str] = None,
        meta_path: Optional[str] = None,
    ):
        self.uri = (uri or os.getenv("DB_URI") or "").strip()
        self.local_db = Path(local_db_path or "data/confessions.db")
        self.backup_dir = Path(backup_dir or "data/backups")
        self.metadata_file = Path(meta_path or "data/db_meta.json")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.local_db.parent.mkdir(parents=True, exist_ok=True)
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        self._ctx_conn = None  # для контекстного использования DBManager

    # Позволяет: with DBManager(...) as conn: ...
    def __enter__(self):
        self._ctx_conn = self.connect()
        return self._ctx_conn

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._ctx_conn is not None:
                _close_conn(self._ctx_conn)
        finally:
            self._ctx_conn = None

    @contextmanager
    def connect_ctx(self):
        """
        Контекстный менеджер, который гарантированно закрывает соединение.
        Использование:
            with dbm.connect_ctx() as conn:
                ...
        """
        conn = self.connect()
        try:
            yield conn
        finally:
            _close_conn(conn)

    def get_db_type(self) -> str:
        if self._is_postgres_uri(self.uri) and psycopg:
            return "postgres"
        return "sqlite"

    def connect(self):
        if self.get_db_type() == "postgres":
            pg = self._connect_postgres()
            if pg is not None:
                return pg
        return self._connect_sqlite()

    def migrate_to_cloud(self) -> bool:
        flag = (os.getenv("MIGRATE_TO_CLOUD", "")).strip().lower() in ("1", "true", "yes", "on")
        if not flag or not self._validate_cloud_db():
            return False
        backup_path = None
        try:
            backup_path = self.create_backup()
            self._transfer_data()
            if self._validate_cloud_db():
                self.clean_local_db()
                return True
        except Exception as e:
            print(f"Migration error: {e}")
            if backup_path:
                self.restore_from_backup(backup_path)
        return False

    def _transfer_data(self) -> None:
        s_conn = self._connect_sqlite()
        p_conn = self._connect_postgres()
        if p_conn is None:
            try:
                _close_conn(s_conn)
            finally:
                pass
            raise RuntimeError("No Postgres connection for migration")

        s_cur = s_conn.cursor()
        p_cur = p_conn.cursor()
        try:
            self._ensure_postgres_schema(p_conn)

            s_cur.execute("SELECT user_id FROM user_settings")
            rows = s_cur.fetchall()
            if rows:
                p_cur.executemany(
                    "INSERT INTO user_settings (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
                    [(r[0],) for r in rows],
                )

            s_cur.execute("SELECT tag, count FROM stats")
            rows = s_cur.fetchall()
            if rows:
                p_cur.executemany(
                    "INSERT INTO stats (tag, count) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    rows,
                )

            s_cur.execute("SELECT id, name FROM users")
            rows = s_cur.fetchall()
            if rows:
                p_cur.executemany(
                    "INSERT INTO users (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
                    rows,
                )

            s_cur.execute("PRAGMA table_info(confessions)")
            cols = [r[1] for r in s_cur.fetchall()]
            wanted = ["user_id", "text", "hashtags", "reactions", "timestamp", "keywords", "emotion"]
            present = [c for c in wanted if c in cols]
            select_sql = f"SELECT {', '.join(present)} FROM confessions"
            s_cur.execute(select_sql)
            rows = s_cur.fetchall()
            if rows:
                placeholders = ", ".join(["%s"] * len(present))
                insert_sql = f"INSERT INTO confessions ({', '.join(present)}) VALUES ({placeholders})"
                p_cur.executemany(insert_sql, rows)

            if not getattr(p_conn, "autocommit", False):
                p_conn.commit()
        finally:
            try:
                s_cur.close()
            except Exception:
                pass
            try:
                p_cur.close()
            except Exception:
                pass
            try:
                _close_conn(s_conn)
            except Exception:
                pass
            try:
                _close_conn(p_conn)
            except Exception:
                pass

    def _validate_cloud_db(self) -> bool:
        try:
            conn = self._connect_postgres()
            if conn is None:
                return False
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
                return True
            finally:
                _close_conn(conn)
        except Exception:
            return False

    def create_backup(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}.db"
        legacy_path = Path("data/confessions.db.bak")
        if self.local_db.exists():
            shutil.copy2(self.local_db, backup_path)
            legacy_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.local_db, legacy_path)
        meta = {
            "backup_path": str(backup_path),
            "created_at": timestamp,
            "db_type": self.get_db_type(),
            "legacy_path": str(legacy_path),
        }
        with self.metadata_file.open("w", encoding="utf-8") as f:
            json.dump(meta, f)
        return str(backup_path)

    def restore_from_backup(self, backup_path: Optional[str] = None) -> bool:
        if not backup_path and self.metadata_file.exists():
            with self.metadata_file.open("r", encoding="utf-8") as f:
                meta = json.load(f)
            backup_path = meta.get("backup_path")
        if backup_path and Path(backup_path).exists():
            shutil.copy2(backup_path, self.local_db)
            print(f"Restored from backup: {backup_path}")
            return True
        return False

    def clean_local_db(self) -> None:
        if self.local_db.exists():
            self.local_db.unlink()

    @staticmethod
    def _resolve_sqlite_target(uri: Optional[str]) -> tuple[Optional[str], bool]:
        """
        Возвращает (path, is_memory) для SQLite.
        - path: путь к файлу (str) или None для дефолтного self.local_db.
        - is_memory: True, если используется in-memory база.
        """
        if not uri:
            return None, False

        low = uri.strip().lower()

        # Явные in-memory варианты
        if low in (":memory:", "sqlite://:memory:", "sqlite:///:memory:"):
            return None, True

        # sqlite:///path/to/file.db
        if low.startswith("sqlite:///"):
            return uri[10:], False

        return None, False

    def _connect_sqlite(self):
        path, is_memory = self._resolve_sqlite_target(self.uri)
        need_init = False
        if is_memory:
            conn = sqlite3.connect(":memory:")
            need_init = True
        else:
            db_file = Path(path) if path else self.local_db
            need_init = not db_file.exists()
            conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
        except Exception:
            pass
        if need_init:
            self._init_db_schema(conn)
        return _register_conn(conn)

    def _connect_postgres(self):
        if psycopg is None or not self._is_postgres_uri(self.uri):
            return None
        try:
            conn = psycopg.connect(self.uri, row_factory=dict_row)
            try:
                conn.autocommit = True
            except Exception:
                pass
            return _register_conn(conn)
        except Exception as e:
            print(f"PostgreSQL connection error: {e}")
            return None

    def _init_db_schema(self, conn) -> None:
        cur = conn.cursor()
        try:
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
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id TEXT PRIMARY KEY
                );
                CREATE TABLE IF NOT EXISTS stats (
                    tag TEXT,
                    count INTEGER
                );
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT
                );
                """
            )
            cur.execute("PRAGMA table_info(confessions)")
            cols = {r[1] for r in cur.fetchall()}
            for col in ("keywords", "emotion"):
                if col not in cols:
                    cur.execute(f"ALTER TABLE confessions ADD COLUMN {col} TEXT")
            conn.commit()
        finally:
            cur.close()

    def _ensure_postgres_schema(self, conn) -> None:
        cur = conn.cursor()
        try:
            stmts = [
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
                )
                """,
                "CREATE TABLE IF NOT EXISTS user_settings (user_id TEXT PRIMARY KEY)",
                "CREATE TABLE IF NOT EXISTS stats (tag TEXT, count INTEGER)",
                "CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT)",
            ]
            for sql in stmts:
                cur.execute(sql)
            if not getattr(conn, "autocommit", False):
                conn.commit()
        finally:
            cur.close()

    @staticmethod
    def _is_postgres_uri(uri: str) -> bool:
        if not uri:
            return False
        low = uri.lower()
        return low.startswith("postgres://") or low.startswith("postgresql://")
