# app/services/copilot_emulator.py
from app.ai.client import AIClient
from app.ai.prompts import system_prompt, developer_prompt


def copilot_emulate(user_text: str, context: dict) -> str:
    client = AIClient()
    res = client.generate(
        system_prompt(),
        developer_prompt(),
        user_text,
        context,
    )
    return (res.text or "").strip()
