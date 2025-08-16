from dataclasses import dataclass


@dataclass
class DigestPreference:
    user_id: str
    topic: str
    intensity: int = 5
    format: str = "short"
    language: str = "ru"
