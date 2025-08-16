import re


def extract_keywords(text: str) -> list[str]:
    """
    Извлекает все слова длиной >=4 символов из текста.
    """
    return re.findall(r"\b\w{4,}\b", text.lower())


def extract_hashtags(text: str) -> list[str]:
    """
    Берёт первые 3 ключевых слова и превращает их в «#теги».
    """
    words = extract_keywords(text)
    return [f"#{w}" for w in words[:3]]
