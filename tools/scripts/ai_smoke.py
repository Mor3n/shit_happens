# scripts/ai_smoke.py
from app.ai.client import AIClient
from app.services.prompts import system_prompt, developer_prompt

if __name__ == "__main__":
    client = AIClient()
    res = client.generate(
        system_prompt(),
        developer_prompt(),
        "Сделай 1 фразу-дайджест про проект 'Хуйня случается'.",
        {"user": {"lang": "ru"}, "history": [], "post": None},
    )
    print("err:", res.error)
    print("ms:", res.duration_ms)
    print("out:", (res.text or "")[:500])
