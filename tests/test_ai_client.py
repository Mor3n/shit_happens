# tests/test_ai_client.py
import os
import pytest
from app.ai.client import AIClient, AIResult

def test_generate_stub_mode(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    client = AIClient()

    result = client.generate(
        system="System prompt",
        developer="Developer prompt",
        user="User message",
        context={"user": {"id": "123"}}
    )

    assert isinstance(result, AIResult)
    assert result.error == "NO_API_KEY"
    assert "Заглушка ИИ" in result.text


def test_generate_mocked(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    import requests
    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "choices": [
                    {"message": {"content": "Привет, это ответ ИИ."}}
                ]
            }

    monkeypatch.setattr(requests, "post", lambda *a, **kw: MockResponse())

    client = AIClient()
    result = client.generate(
        system="System prompt",
        developer="Developer prompt",
        user="User message",
        context={"user": {"id": "123"}}
    )

    assert isinstance(result, AIResult)
    assert result.text == "Привет, это ответ ИИ."
    assert result.error is None
