from app.utils.text import extract_hashtags, extract_keywords

EMOTION_MAP = {
    "бесит": "злость",
    "люблю": "радость",
    "привет": "нейтрально",
    "дела": "интерес",
    "проект": "мотивация",
    "бот": "технологичность",
    "автоматизация": "удовлетворение",
}


def detect_emotion(text: str) -> str:
    for k, e in EMOTION_MAP.items():
        if k in text.lower():
            return e
    return "неопределено"


def analyze_text(text: str) -> dict:
    kws = extract_keywords(text)
    tags = extract_hashtags(text)
    emo = detect_emotion(text)
    return {"keywords": kws, "hashtags": tags, "emotion": emo}
