try:
    from config.config import Config as _LegacyConfig
    class Config(_LegacyConfig):
        pass
except Exception:
    from app.config import Config
