def test_backup_exists():
    import os

    from config.db_manager import DBManager

    path = DBManager().create_backup()
    assert path and os.path.exists(path)
