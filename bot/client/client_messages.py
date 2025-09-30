from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

class MessageType(Enum):
    OTHER = 0
    TEXT = 1
    IMAGE = 2


@dataclass
class MessageContent:
    message_type: MessageType
    content: Any


@dataclass
class Message:
    user_id: str
    content: list[MessageContent]
    date: datetime

