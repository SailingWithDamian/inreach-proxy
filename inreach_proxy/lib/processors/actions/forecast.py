import dataclasses
import logging
from email.message import EmailMessage
from typing import Dict, Any, Optional

from inreach_proxy.lib.email import Outbound
from inreach_proxy.lib.helpers import get_message_plain_text_body
from inreach_proxy.lib.integrations.garmin import Garmin
from inreach_proxy.lib.processors.actions.base import BaseAction
from inreach_proxy.models import GarminConversations

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SpotForecastAction(BaseAction):
    latitude: str
    longitude: str

    @staticmethod
    def matches(text: str) -> bool:
        for line in text.splitlines():
            if line == "forecast" or line.startswith("forecast "):
                return True
        return False

    @staticmethod
    def from_email(message: EmailMessage, settings: Optional[Dict[Any, Any]] = None) -> "SpotForecastAction":
        for line in get_message_plain_text_body(message).splitlines():
            if line == "forecast" or line.startswith("forecast "):
                return SpotForecastAction.from_text(line, settings)

    @staticmethod
    def from_text(text: str, settings: Optional[Dict[Any, Any]] = None) -> "SpotForecastAction":
        arguments = text.split(" ")[1].strip().split(",") if " " in text else []
        if len(arguments) == 0 and settings:
            if map_share_key := settings.get("map_share_key"):
                latitude, longitude = Garmin().get_latest_position(map_share_key)
                arguments = [latitude, longitude]

        if len(arguments) < 2:
            logger.error(f"Invalid forecast request: {arguments}")
            return

        # Normalise
        if "." in arguments[0]:
            parts = arguments[0].split(".")
            arguments[0] = f'{parts[0].rjust(2, "0")}.{parts[1]}'
        else:
            arguments[0] = arguments[0].rjust(2, "0")

        if "." in arguments[1]:
            parts = arguments[1].split(".")
            arguments[1] = f'{parts[0].rjust(3, "0")}.{parts[1]}'
        else:
            arguments[1] = arguments[1].rjust(3, "0")

        return SpotForecastAction(
            latitude=arguments[0],
            longitude=arguments[1],
        )

    def get_type(self) -> int:
        return 0

    def execute_with_email(self, conversation: GarminConversations):
        request = f"send spot:{self.latitude},{self.longitude}\nquit\n"
        out = Outbound(conversation.inbox.smtp_host, conversation.inbox.username, conversation.inbox.password)
        out.send_email("query@saildocs.com", request, reply_address=conversation.address)
