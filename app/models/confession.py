from sqlalchemy import Column, Integer, String, Text
from app.models import Base

class Confession(Base):
    __tablename__ = "confessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    text = Column(Text)
    hashtags = Column(Text)
    reactions = Column(Text)
    timestamp = Column(String)
    keywords = Column(Text)
    emotion = Column(Text)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "text": self.text,
            "hashtags": self.hashtags,
            "reactions": self.reactions,
            "timestamp": self.timestamp,
            "keywords": self.keywords,
            "emotion": self.emotion,
        }
