from email.message import EmailMessage
from typing import Optional, Dict, Any

from inreach_proxy.lib.models import ParsedEmail
from inreach_proxy.lib.parsers.garmin import GarminMessageParser
from inreach_proxy.lib.parsers.sail_docs import SailDocsMessageParser


def parse_message(message: EmailMessage, settings: Optional[Dict[Any, Any]]) -> ParsedEmail:
    if message["From"] == "query-reply@saildocs.com":
        return SailDocsMessageParser().process(message)

    return GarminMessageParser(settings).process(message)
