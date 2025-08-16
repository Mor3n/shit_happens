from app import app
from app.services.confess_service import save_confession


def test_save_confession():
    with app.app_context():
        text = "Это тестовая исповедь с более чем двадцатью словами, эмоциями..."  # noqa: E501
        result = save_confession("test_user", text)
        assert isinstance(result, list)
