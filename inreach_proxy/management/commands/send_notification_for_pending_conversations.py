import logging
from typing import Any

from django.core.management import BaseCommand

from inreach_proxy.lib.garmin import GarminMapShare
from inreach_proxy.models import EmailInbox, GarminConversations

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        """Send a notification message for pending conversations."""
        for inbox in EmailInbox.objects.all():
            inbox_settings = inbox.settings or {}

            map_share_key = inbox_settings.get("map_share_key")
            if not map_share_key:
                print(f"[{inbox}] No map share key configured for inbox, skipping")
                continue

            device_id = inbox_settings.get("map_share_device_id")
            if not device_id:
                print(f"[{inbox}] No map share device id configured for inbox, skipping")
                continue

            garmin = GarminMapShare(map_share_key, device_id)
            for conversation in GarminConversations.objects.filter(inbox=inbox).order_by("selector"):
                if conversation.reply_url:
                    print(f"{conversation.user}: Has existing reply url: {conversation.reply_url}")
                    continue

                print(f"Sending setup notification from {conversation.address}")
                garmin.send("Please reply to setup this conversation in the proxy", conversation.address)
