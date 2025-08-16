from flask import Blueprint

digest_bp = Blueprint("digest", __name__)

@digest_bp.route("/digest")
def digest_view():
    return "digest placeholder"
