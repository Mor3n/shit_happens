import re

from flask import Blueprint, jsonify, request

from app.services.confess_service import save_confession

confess = Blueprint("confess", __name__)


@confess.route("/confess", methods=["POST"])
def confess_route():
    user_id = request.form.get("user_id")
    text = (request.form.get("text") or "").strip()

    # Проверка по СИМВОЛАМ: 20–50
    if not (20 <= len(text) <= 50):
        return jsonify({"error": "Исповедь должна содержать от 20 до 50 символов."}), 400

    hashtags = save_confession(user_id, text)
    return jsonify({"status": "ok", "hashtags": hashtags})
