from alembic.config import Config as _Config

class Config(_Config):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        if not self.get_main_option('script_location'):
            self.set_main_option('script_location', 'alembic')
