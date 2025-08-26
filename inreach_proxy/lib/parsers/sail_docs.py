import base64
import logging
import zlib
from email.message import EmailMessage
from email.utils import parsedate_to_datetime, parseaddr

from inreach_proxy.lib.helpers import get_message_plain_text_body
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
            attachment = message.get_payload(1).get_payload()
            parsed_email.responses.append(
                Grib(
                    request_code=request_code,
                    received_time=parsedate_to_datetime(message["date"]),
                    compressed_grib=base64.b64encode(zlib.compress(attachment)),
                )
            )

        if SpotForecast.matches(request_code):
            parsed_email.responses.append(
                SpotForecast(
                    request_code=request_code,
                    received_time=parsedate_to_datetime(message["date"]),
                    text=body_text,
                )
            )

        return parsed_email
