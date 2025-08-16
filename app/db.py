from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.base import db

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


def get_db():
    return db.session
