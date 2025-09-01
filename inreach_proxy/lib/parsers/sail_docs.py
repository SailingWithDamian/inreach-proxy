import logging
from email.message import EmailMessage
from email.utils import parsedate_to_datetime, parseaddr

from inreach_proxy.lib.helpers import get_message_plain_text_body, get_grib_attachment
from inreach_proxy.lib.models import ParsedEmail
from inreach_proxy.lib.processors.responses.grib import Grib
from inreach_proxy.lib.processors.responses.spot_forecast import SpotForecast

logger = logging.getLogger(__name__)


class SailDocsMessageParser:
    def _find_request_code(self, text: str) -> str:
        for line in text.splitlines():
            if line.startswith("request code:"):
                return line.split("request code:")[1].strip()
        return ""

    def process(self, message: EmailMessage) -> ParsedEmail:
        _, from_address = parseaddr(message["From"])
        parsed_email = ParsedEmail(from_address=from_address)

        body_text = get_message_plain_text_body(message)
        request_code = self._find_request_code(body_text)

        if Grib.matches(request_code):
            logger.info(f"Found request code that looks like a GRIB: {request_code}")
            attachment = get_grib_attachment(message)
            if not attachment:
                logger.error(f"Failed to find attachment on GRIB message: {request_code}")
                return parsed_email

            parsed_email.responses.append(
                Grib(
                    request_code=request_code,
                    received_time=parsedate_to_datetime(message["date"]),
                    grib=attachment,
                )
            )

        elif SpotForecast.matches(request_code):
            logger.info(f"Found request code that looks like a forecast: {request_code}")
            parsed_email.responses.append(
                SpotForecast(
                    request_code=request_code,
                    received_time=parsedate_to_datetime(message["date"]),
                    text=body_text,
                )
            )

        else:
            logger.info(f"Did not find matching request code: {request_code}")

        return parsed_email
