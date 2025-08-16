from flask import Blueprint, jsonify, request

from app.services.reaction_service import add_reaction

react = Blueprint("react", __name__)


@react.route("/react", methods=["POST"])
def react_route():
    post_id = request.form.get("post_id")
    reaction = request.form.get("reaction")
    updated = add_reaction(post_id, reaction)
    return jsonify({"status": "ok", "reactions": updated})
