# tests/test_confess_handler.py
import pytest
from unittest.mock import AsyncMock
from telegram import Update, Message, User
from telegram.ext import ContextTypes

from app.telegram.handlers.confess_handler import handle_confession_text

@pytest.mark.asyncio
async def test_handle_confession_text_valid(monkeypatch):
    # --- Моки Telegram ---
    mock_user = User(id=123, first_name="Test", is_bot=False)
    mock_message = Message(
        message_id=1,
        date=None,
        chat=None,
        text="Это моя исповедь, она достаточно длинная",
        from_user=mock_user
    )
    mock_update = Update(update_id=1, message=mock_message)
    mock_context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)

    # --- Моки pending_confess ---
    from app.telegram.handlers import confess_handler
    confess_handler.pending_confess.add("123")

    # --- Моки save_confession ---
    class MockPost:
        text = "Это моя исповедь, она достаточно длинная"
        def to_dict(self): return {"text": self.text}
    monkeypatch.setattr("app.services.confess_service.save_confession", lambda uid, txt: MockPost())

    # --- Моки get_settings ---
    monkeypatch.setattr("app.services.settings_service.get_settings", lambda uid: {"language": "ru", "format": "short"})

    # --- Моки AIClient ---
    class MockAI:
        def generate(self, sys, dev, user, ctx):
            class R: text = "ИИ-ответ"
            return R()
    monkeypatch.setattr("app.ai_adapter.AIClient", lambda: MockAI())

    # --- Моки build_context ---
    monkeypatch.setattr("app.services.ai_context.build_context", lambda db, user_id, history_limit=3: {
        "user": {"id": user_id},
        "post": {"text": "..."}
    })

    # --- Мок safe_reply ---
    replies = []
    async def mock_reply(update, context, text): replies.append(text)
    monkeypatch.setattr("app.telegram.helpers.safe_reply", mock_reply)

    # --- Вызов ---
    await handle_confession_text(mock_update, mock_context)

    # --- Проверка ---
    assert any("ИИ-ответ" in r for r in replies)
