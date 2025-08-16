from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReactionLog:
    user_id: str
    post_id: int
    reaction_type: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
