def register_routes(app):
    from app.routes.digest_handler import digest_bp
    app.register_blueprint(digest_bp)
