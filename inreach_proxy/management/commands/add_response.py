import logging
from typing import Any

from django.core.management import BaseCommand, CommandParser

from inreach_proxy.models import EmailInbox, GarminConversations, Response

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--inbox", required=True)
        parser.add_argument("--selector", default=None)
        parser.add_argument("message")

    def handle(self, *args: Any, **options: Any) -> None:
        """Queue a message to be sent."""
        inbox = EmailInbox.objects.get(name=options["inbox"])
        conversation = GarminConversations.objects.get(inbox=inbox, selector=options["selector"])
        print(Response.objects.create(conversation=conversation, status=0, message=options["message"]))
