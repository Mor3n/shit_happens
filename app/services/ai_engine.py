from app.ai_adapter import AIClient

def generate_text(system_prompt: str, developer_prompt: str, user_prompt: str, context: list) -> str:
    """
    Выполняет генерацию текста через AIClient и возвращает готовую строку.
    """
    client = AIClient()
    result = client.generate(system_prompt, developer_prompt, user_prompt, context)
    return result.text.strip() if hasattr(result, "text") else str(result).strip()
