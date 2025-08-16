from app import app
from app.services.reaction_service import add_reaction


def test_add_reaction():
    with app.app_context():
        result = add_reaction(1, "❤️")
        assert isinstance(result, dict)
