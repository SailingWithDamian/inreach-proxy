import logging
from typing import Any

from django.core.management import BaseCommand, CommandParser

from inreach_proxy.models import EmailInbox, GarminConversations, Response, Request

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--inbox", required=True)
        parser.add_argument("--selector", default=None)

    def handle(self, *args: Any, **options: Any) -> None:
        """Clear existing transactions."""
        inbox = EmailInbox.objects.get(name=options["inbox"])
        conversation = GarminConversations.objects.get(inbox=inbox, selector=options["selector"])

        Response.objects.filter(conversation=conversation).delete()
        Request.objects.filter(conversation=conversation).delete()
