from pathlib import Path

ai_generate = Path("app/services/ai_generate.py")

# Рабочая версия без битых байт
ai_generate.write_text(
    "from .ai_engine import generate_text\n"
    "from .ai_context import build_context\n"
    "from .settings_service import get_settings\n\n"
    "def generate_confession(conn, user_id):\n"
    "    settings = get_settings(user_id)\n"
    "    ctx = build_context(conn, user_id, history_limit=3)\n"
    "    system_prompt = 'Ты исповедник. Пользователь делится своей исповедью.'\n"
    "    developer_prompt = f\"Ответь в формате {settings.get('format', 'short')} на языке {settings.get('language', 'ru')}\"\n"
    "    user_prompt = 'Сгенерируй исповедь от лица пользователя.'\n"
    "    result = generate_text(system_prompt, developer_prompt, user_prompt, ctx)\n"
    "    return result.text.strip()\n",
    encoding="utf-8"
)

print("[OK] ai_generate.py переписан в UTF-8 без битых символов")
