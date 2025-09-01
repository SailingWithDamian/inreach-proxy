import logging
from email.message import EmailMessage
from email.utils import parseaddr
from typing import Optional, Dict, Any

from inreach_proxy.lib.models import ParsedEmail
from inreach_proxy.lib.parsers.garmin import GarminMessageParser
from inreach_proxy.lib.parsers.sail_docs import SailDocsMessageParser

logger = logging.getLogger(__name__)


def parse_message(message: EmailMessage, settings: Optional[Dict[Any, Any]]) -> ParsedEmail:
    _, from_address = parseaddr(message["From"])
    if from_address == "query-reply@saildocs.com":
        logger.info(f"Using SailDocsParser based on {from_address}")
        return SailDocsMessageParser().process(message)

    logger.info(f"Using GarminMessageParser based on {from_address}")
    return GarminMessageParser(settings).process(message)
