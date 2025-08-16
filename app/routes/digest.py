from flask import Blueprint, jsonify, request

from app.services.digest_service import generate_digest

digest = Blueprint("digest", __name__)


@digest.route("/digest", methods=["GET"])
def digest_route():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    posts = generate_digest(user_id)
    return jsonify({"digest": posts})
