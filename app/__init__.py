from flask import Flask
from .config import Config
from app.config_compat import Config
from app.routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from app.db import init_db
    init_db(app)
    app.config.from_object(Config)
    register_routes(app)
    return app

app = create_app()
