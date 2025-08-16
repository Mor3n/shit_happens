import sqlite3

from config.config import Config


def check_tables():
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()

    tables = ["confessions", "stats", "users"]
    for table in tables:
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"  # noqa: E501
        )
        if not cursor.fetchone():
            print(f"❌ Таблица {table} не существует!")
            return False
    return True


if __name__ == "__main__":
    if check_tables():
        print("✅ Все таблицы существуют")
    else:
        print("❌ Не все таблицы созданы, выполните миграции!")
