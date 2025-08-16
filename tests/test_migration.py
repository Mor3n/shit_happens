def test_migration():
    from alembic_env import command
    from alembic_env.config import Config

    cfg = Config("alembic.ini")
    command.current(cfg)
