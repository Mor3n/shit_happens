def test_generate_digest():
    from app.services.digest_service import generate_digest

    assert isinstance(generate_digest("7860962095", limit=1), str)


def test_has_relevant_posts():
    from app.services.digest_service import has_relevant_posts

    assert isinstance(has_relevant_posts("7860962095"), bool)
