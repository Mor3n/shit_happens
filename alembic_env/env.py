import os
import sys
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic_env import context

load_dotenv()

config = context.config

# project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# default sqlite path
default_db_path = os.path.abspath(os.path.join(project_root, "data", "confessions.db"))  # noqa: E501
default_sqlite_url = "sqlite:///" + default_db_path.replace(os.sep, "/")

# Build db_url with sane defaults
db_url = os.getenv("DB_URI", "").strip()
if not db_url:
    db_url = default_sqlite_url
else:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Do not import app package (avoid app/__init__.py side effects)
sys.path.insert(0, os.path.join(project_root, "app"))
try:
    from models import Base

    target_metadata = Base.metadata
except Exception:
    target_metadata = None


def run_migrations_offline():
    url = db_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
