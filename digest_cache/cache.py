import hashlib
import json
from pathlib import Path

CACHE_DIR = Path("digest_cache/digests")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_digest_key(data: dict) -> str:
    raw = json.dumps(data, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


def save_digest(key: str, digest: str):
    with open(CACHE_DIR / f"{key}.txt", "w", encoding="utf-8") as f:
        f.write(digest)


def load_digest(key: str) -> str | None:
    path = CACHE_DIR / f"{key}.txt"
    return path.read_text(encoding="utf-8") if path.exists() else None
