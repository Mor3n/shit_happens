from flask import Blueprint, jsonify, request

from app.services.feed_service import get_feed

# ОДИН Blueprint, одно имя, одна регистрация
feed = Blueprint("feed", __name__)


@feed.route("/", methods=["GET"])
def index():
    return "Service is alive."


@feed.route("/feed", methods=["GET"])
def get_feed_route():
    try:
        page = int(request.args.get("page", 1))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid page"}), 400

    posts = get_feed(page)
    return jsonify(posts)
