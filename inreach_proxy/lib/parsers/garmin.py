import logging
from email.message import EmailMessage
from email.utils import parseaddr
from typing import Optional, Dict, Any

from inreach_proxy.lib.helpers import get_message_plain_text_body
from inreach_proxy.lib.models import ParsedEmail
from inreach_proxy.lib.processors.actions import VALID_ACTIONS

logger = logging.getLogger(__name__)


class GarminMessageParser:
    def __init__(self, settings: Optional[Dict[Any, Any]]):
        self._settings = settings

    def _find_reply_url(self, text: str) -> Optional[str]:
        for line in text.splitlines():
            if "https://explore.garmin.com/textmessage/txtmsg" in line:
                return line.strip()
            if "https://eur.explore.garmin.com/textmessage/txtmsg" in line:
                return line.strip()
        return None

    def process(self, message: EmailMessage) -> ParsedEmail:
        _, from_address = parseaddr(message["From"])
        parsed_email = ParsedEmail(from_address=from_address)

        text = get_message_plain_text_body(message)
        if not text:
            logger.error(f"No message body found: {text}")
            return parsed_email

        garmin_reply_url = self._find_reply_url(text)
        if not garmin_reply_url:
            logger.error(f"Failed to find reply url in the message: {text}")
            return parsed_email

        plain_text_body = get_message_plain_text_body(message)

        parsed_email.garmin_reply_url = garmin_reply_url
        parsed_email.actions = [
            action.from_email(message, self._settings)
            for action in VALID_ACTIONS.values()
            if action.matches(plain_text_body)
        ]
        return parsed_email
