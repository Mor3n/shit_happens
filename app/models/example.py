from app.models.base import db

class Example(db.Model):
    __tablename__ = "example"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
