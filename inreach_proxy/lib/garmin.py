import hashlib
import logging
from typing import Optional
from urllib.parse import urlparse, parse_qs

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from inreach_proxy.models import GarminConversations

logger = logging.getLogger(__name__)


class GarminThread:
    def __init__(self, conversation: GarminConversations) -> None:
        self._conversation = conversation

        self.session = requests.session()
        adapter = HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1, allowed_methods=["POST"]))
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_external_id(self) -> Optional[str]:
        if self._conversation.reply_url:
            url = urlparse(self._conversation.reply_url)
            params = parse_qs(url.query)
            if external_id := params.get("extId"):
                return external_id[0]

        logger.error(f"Failed to find external id for {self._conversation.reply_url}")
        return None

    def _get_message_host(self) -> Optional[str]:
        if self._conversation.reply_url:
            url = urlparse(self._conversation.reply_url)
            if url.hostname == "eur.explore.garmin.com":
                return "eur.explore.garmin.com"
        return "explore.garmin.com"

    def get_reply_address(self):
        if self._conversation.selector:
            user = self._conversation.inbox.username.split("@")[0]
            domain = self._conversation.inbox.username.split("@")[1]
            return f"{user}+{self._conversation.selector}@{domain}"

        return self._conversation.inbox.username

    def send(self, text: str) -> bool:
        external_id = self._get_external_id()
        if not external_id:
            return False

        message_host = self._get_message_host()
        r = self.session.post(
            f"https://{message_host}/TextMessage/TxtMsg",
            timeout=10,
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "*/*",
                "Authority": message_host,
                "Origin": f"https://{message_host}",
                "Referer": f"https://{message_host}/TextMessage/TxtMsg?extId={external_id}",
                "X-Requested-With": "XMLHttpRequest",
            },
            data={
                "ReplyAddress": self.get_reply_address(),
                "ReplyMessage": text,
                "MessageId": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "Guid": external_id,
            },
        )
        if r.status_code != 200:
            logger.error(f"Failed to send message: {r.status_code}: {r.text} for '{text}'")
        else:
            logger.info(f"Garmin API returned: {r.status_code}: {r.text} for '{text}'")
        return r.status_code == 200


class GarminMapShare:
    def __init__(self, share_key: str, device_id: int) -> None:
        self._share_key = share_key
        self._device_id = device_id

        self.session = requests.session()
        adapter = HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1, allowed_methods=["POST"]))
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def send(self, text: str, reply_address: str) -> bool:
        if len(text) > 160:
            logger.error(f"Message is too long: {text}")
            return False

        r = self.session.post(
            f"https://share.garmin.com/{self._share_key}/Map/SendMessageToDevices",
            timeout=10,
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "*/*",
                "Origin": "https://share.garmin.com",
                "Referer": f"https://share.garmin.com/{self._share_key}",
                "X-Requested-With": "XMLHttpRequest",
            },
            data={
                "deviceIds": self._device_id,
                "messageText": text,
                "fromAddr": reply_address,
            },
        )
        if r.status_code != 200:
            logger.error(f"Failed to send message: {r.status_code}: {r.text}")
        else:
            logger.info(f"Garmin API returned: {r.status_code}: {r.text}")
        return r.status_code == 200
