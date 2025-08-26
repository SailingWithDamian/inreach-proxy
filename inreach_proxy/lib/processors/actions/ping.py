import dataclasses
from email.message import EmailMessage
from typing import Optional, Dict, Any

from inreach_proxy.lib.helpers import get_message_plain_text_body
from inreach_proxy.lib.processors.actions.base import BaseAction


@dataclasses.dataclass
class PingPongAction(BaseAction):
    payload: str

    @staticmethod
    def matches(text: str) -> bool:
        for line in text.splitlines():
            if line.strip() == "ping" or line.startswith("ping "):
                return True
        return False

    @staticmethod
    def from_email(message: EmailMessage, settings: Optional[Dict[Any, Any]] = None) -> "PingPongAction":
        for line in get_message_plain_text_body(message).splitlines():
            if line.strip() == "ping" or line.startswith("ping "):
                return PingPongAction.from_text(line, settings)

    @staticmethod
    def from_text(text: str, settings: Optional[Dict[Any, Any]] = None) -> "PingPongAction":
        parts = text.split(" ")
        payload = parts[1] if len(parts) >= 2 else "default"
        return PingPongAction(payload=payload)

    def get_type(self) -> int:
        return 1

    def execute(self) -> str:
        return f"pong {self.payload}"
