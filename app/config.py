import os

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
