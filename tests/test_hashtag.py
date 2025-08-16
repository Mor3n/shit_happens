def test_extract_hashtags():
    from app.utils.text import extract_hashtags

    assert extract_hashtags("Это тестовая исповедь") != []
