import logging
from typing import Any

from django.core.management import BaseCommand, CommandParser

from inreach_proxy.lib.business import create_request_for_action
from inreach_proxy.lib.processors.actions import VALID_ACTIONS
from inreach_proxy.models import EmailInbox, GarminConversations

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

        for valid_action in VALID_ACTIONS.values():
            if valid_action.matches(options["message"]):
                action = valid_action.from_text(options["message"])
                print(f"Found action: {action}")
                create_request_for_action(conversation, action)
