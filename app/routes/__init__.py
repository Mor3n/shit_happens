def register_routes(app):
    try:
        from app.routes.health import health_bp
        app.register_blueprint(health_bp)
    except Exception as e:
        pass
    try:
        from app.routes.digest_handler import digest_bp
        app.register_blueprint(digest_bp)
    except Exception:
        pass
