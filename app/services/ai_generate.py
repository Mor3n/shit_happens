from .ai_engine import generate_text
from .ai_context import build_context
from .settings_service import get_settings

def generate_confession(conn, user_id, settings=None) -> str:
    """
    Генерирует текст исповеди:
    - Берёт пользовательские настройки (или дефолт без Flask-контекста)
    - Формирует контекст из последних сообщений
    - Отправляет в AI с ролями system/dev/user
    """
    if settings is None:
        try:
            settings = get_settings(user_id)  # в проде — внутри Flask-контекста
        except RuntimeError:
            # Вне Flask-контекста — используем безопасные значения по умолчанию
            settings = {"language": "ru", "format": "short"}

    ctx = build_context(conn, user_id, history_limit=3)

    system_prompt = "Ты исповедник. Пользователь делится своей исповедью."
    developer_prompt = (
        f"Ответь в формате {settings.get('format', 'short')} "
        f"на языке {settings.get('language', 'ru')}"
    )
    user_prompt = "Сгенерируй исповедь от лица пользователя."

    text = generate_text(system_prompt, developer_prompt, user_prompt, ctx).strip()

    # --- Fallback-постобработка ---
    # 1. Длина > 10
    if len(text) <= 10:
        text = f"{text} — это моя исповедь"
    # 2. Ключевые слова "исповедь" или "я"
    if not any(word in text.lower() for word in ("исповедь", "я")):
        text = f"Это моя исповедь: {text}"

    return text
