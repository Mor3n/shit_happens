from dataclasses import dataclass


@dataclass
class BlockedTag:
    user_id: str
    tag: str
