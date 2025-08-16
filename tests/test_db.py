from app import app
from config.db import get_db


def test_db_connection():
    with app.app_context():
        db = get_db()
        assert db is not None
