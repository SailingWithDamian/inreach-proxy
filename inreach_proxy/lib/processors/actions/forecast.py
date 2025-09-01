import dataclasses
import logging
from email.message import EmailMessage
from typing import Dict, Any, Optional, Tuple

from inreach_proxy.lib.email import Outbound
from inreach_proxy.lib.helpers import get_message_plain_text_body, decimal_degress_to_dd_mm_ss, normalise_dd_mm_ss
from inreach_proxy.lib.integrations.garmin import Garmin
from inreach_proxy.lib.processors.actions.base import BaseAction
from inreach_proxy.models import GarminConversations

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SpotForecastAction(BaseAction):
    _database_id: Optional[int] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None

    @staticmethod
    def resolve_position(settings: Optional[Dict[Any, Any]] = None) -> Tuple[Optional[str], Optional[str]]:
        if settings:
            if map_share_key := settings.get("map_share_key"):
                latitude, longitude = Garmin().get_latest_position(map_share_key)
                if latitude and longitude:
                    return (
                        decimal_degress_to_dd_mm_ss(latitude, True),
                        decimal_degress_to_dd_mm_ss(longitude, False),
                    )
        return None, None

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
                return SpotForecastAction.from_text(line, settings, True)

    @staticmethod
    def from_text(
        text: str, settings: Optional[Dict[Any, Any]] = None, resolve_position: bool = False
    ) -> "SpotForecastAction":
        arguments = text.split(" ")[1].strip().split(",") if " " in text else []
        # Note: Don't resolve the position using the map share here, otherwise the scheduled request will always
        # be for the same place, rather than the current place.
        if len(arguments) < 2:
            if resolve_position:
                # Resolve the current position (i.e. when this comes from an email and not a scheduled request)
                lat, long = SpotForecastAction.resolve_position(settings)
                return SpotForecastAction(latitude=lat, longitude=long)
            # Do not resolve the current position (i.e. when this comes from a scheduled request)
            return SpotForecastAction()

        return SpotForecastAction(
            latitude=normalise_dd_mm_ss(arguments[0], True),
            longitude=normalise_dd_mm_ss(arguments[1], False),
        )

    def get_type(self) -> int:
        return 0

    def execute_with_email(self, conversation: GarminConversations):
        if self._database_id and (not self.latitude or not self.longitude):
            # Resolve the current position (i.e. when this comes from a scheduled request)
            lat, long = SpotForecastAction.resolve_position(conversation.inbox.settings)
            if lat and long:
                self.latitude = lat
                self.longitude = long

        if not self.latitude or not self.longitude:
            logger.error(f"Failed to get latitude/longitude for forecast: {conversation.inbox.settings}")
            return

        request = f"send spot:{self.latitude},{self.longitude}\nquit\n"
        out = Outbound(conversation.inbox.smtp_host, conversation.inbox.username, conversation.inbox.password)
        out.send_email("query@saildocs.com", request, reply_address=conversation.address)
