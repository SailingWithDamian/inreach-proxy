import logging
from typing import Any

from django.core.management import BaseCommand, CommandParser

from inreach_proxy.models import EmailInbox, GarminConversations

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--all", action="store_true", default=False)

    def handle(self, *args: Any, **options: Any) -> None:
        """Show the currently configured inboxes/conversations."""
        for inbox in EmailInbox.objects.all():
            print(f"{inbox.name}:")
            for conversation in GarminConversations.objects.filter(inbox=inbox).order_by("selector"):
                if conversation.reply_url:
                    print(f"  [OK] {conversation.user} ({conversation.address})")
                else:
                    print(f"  [PENDING] {conversation.user} ({conversation.address})")
