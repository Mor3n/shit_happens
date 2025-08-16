from flask import Blueprint, jsonify, request

from app.services.stats_service import get_global_stats, get_user_stats

global_stats = Blueprint("global_stats", __name__)
user_stats = Blueprint("user_stats", __name__)


@global_stats.route("/stats/global", methods=["GET"])
def global_stats_route():
    stats = get_global_stats()
    return jsonify(stats)


@user_stats.route("/stats/user", methods=["GET"])
def user_stats_route():
    user_id = request.args.get("user_id")
    stats = get_user_stats(user_id)
    return jsonify(stats)
