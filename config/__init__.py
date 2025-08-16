import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

    # Единый URI базы из .env, fallback на SQLite
    DB_URI = os.getenv(
        "DB_URI",
        "sqlite:///" + os.path.join(os.getcwd(), "data", "confessions.db")
    )

    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PING_INTERVAL = 10

    # AI feature flags
    USE_AI_RESPONSES = os.getenv("USE_AI_RESPONSES", "1").lower() in ("1", "true", "yes", "on")
    USE_AI_CONFESS_REPLY = os.getenv("USE_AI_CONFESS_REPLY", "1").lower() in ("1", "true", "yes", "on")
    AI_TONE = os.getenv("AI_TONE", "witty")
    AI_MAX_LEN = int(os.getenv("AI_MAX_LEN", "240"))
