import logging
from typing import Any

from django.core.management import BaseCommand, CommandParser

from inreach_proxy.lib.processors.actions import VALID_ACTIONS
from inreach_proxy.models import EmailInbox, GarminConversations, ScheduledRequest

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--inbox", required=True)
        parser.add_argument("--selector", default=None)
        parser.add_argument("--group", default=0)
        parser.add_argument("message")

    def handle(self, *args: Any, **options: Any) -> None:
        """Schedule a request to be executed."""
        inbox = EmailInbox.objects.get(name=options["inbox"])
        conversation = GarminConversations.objects.get(inbox=inbox, selector=options["selector"])

        for database_id, valid_action in VALID_ACTIONS.items():
            if valid_action.matches(options["message"]):
                action = valid_action.from_text(options["message"])
                print(f"Ensuring scheduled request for: {action}")
                ScheduledRequest.objects.get_or_create(
                    conversation=conversation, group=options["group"], action=database_id, input=action.get_data()
                )
