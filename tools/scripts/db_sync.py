import sys

from config.db_manager import DBManager


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    db = DBManager()
    if arg == "--migrate":
        print("✅ migrated" if db.migrate_to_cloud() else "⚠️ skipped")
    elif arg == "--restore":
        print("✅ restored" if db.restore_from_backup() else "⚠️ no backup")
    else:
        conn = db.connect()
        print("✅ База данных готова")
        conn.close()


if __name__ == "__main__":
    main()
