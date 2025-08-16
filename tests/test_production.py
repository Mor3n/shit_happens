from app import app
from alembic_env import command
from alembic_env.config import Config
from config.db_manager import DBManager


def test_migrations():
    """Проверяем, что миграции применяются без ошибок"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")


def test_critical_services():
    """Тестируем критические сервисы на экстремальных данных"""
    from app.services import confess_service, digest_service

    with app.app_context():
        assert confess_service.save_confession("", "") == []
        digest = digest_service.generate_digest("invalid_user").lower()
        assert any(s in digest for s in ("ошибка", "нет", "ключевых слов"))


def test_backup_integrity():
    """Проверка целостности бэкапов"""
    path = DBManager().create_backup()
    assert path
    import os
    assert os.path.exists(path)
    with open(path, "rb") as f:
        assert f.read(16) != b""
    with open("data/confessions.db.bak", "rb") as f:
        assert f.read(16) != b""
