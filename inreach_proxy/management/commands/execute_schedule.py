import logging
from typing import Any

from django.core.management import BaseCommand, CommandParser

from inreach_proxy.models import Request, ScheduledRequest

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--group", required=True)

    def handle(self, *args: Any, **options: Any) -> None:
        """Make requests from scheduled requests."""
        for scheduled_request in ScheduledRequest.objects.filter(group=options["group"]).prefetch_related(
            "conversation", "conversation__inbox"
        ):
            logger.info(
                f"[{scheduled_request.conversation.user}] Creating request for {scheduled_request.get_action_display()} :: {scheduled_request.input}"
            )

            Request.objects.create(
                conversation=scheduled_request.conversation,
                status=0,
                action=scheduled_request.action,
                input=scheduled_request.input,
            )
