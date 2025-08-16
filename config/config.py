import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

    # 🔹 основной URI для SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://user:password@localhost:5432/dbname"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # полезно выключить ворнинги

    # SQLite вариант (если нужен в dev)
    DATABASE = os.path.join(os.getcwd(), "data", "confessions.db")

    PING_INTERVAL = 10

    # AI feature flags
    USE_AI_RESPONSES = os.getenv("USE_AI_RESPONSES", "1") in ("1", "true", "yes", "on")
    USE_AI_CONFESS_REPLY = os.getenv("USE_AI_CONFESS_REPLY", "1") in ("1", "true", "yes", "on")
    AI_TONE = os.getenv("AI_TONE", "witty")
    AI_MAX_LEN = int(os.getenv("AI_MAX_LEN", "240"))
