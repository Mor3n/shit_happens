from flask import Blueprint, jsonify, request

from app.services.settings_service import get_settings, update_setting

settings = Blueprint("settings", __name__)


@settings.route("/settings", methods=["GET"])
def settings_route():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    return jsonify(get_settings(user_id))


@settings.route("/settings", methods=["POST"])
def update_settings():
    user_id = request.form.get("user_id")
    key = request.form.get("key")
    value = request.form.get("value")
    if not all([user_id, key, value]):
        return jsonify({"error": "Missing parameters"}), 400
    return jsonify(update_setting(user_id, key, value))
