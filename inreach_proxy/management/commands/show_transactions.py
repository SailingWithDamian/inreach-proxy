import logging
from typing import Any

from django.core.management import BaseCommand, CommandParser
from django.db.models import Q

from inreach_proxy.models import EmailInbox, Request, GarminConversations, Response

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--all", action="store_true", default=False)

    def handle(self, *args: Any, **options: Any) -> None:
        """Show the current request/response statuses."""
        for inbox in EmailInbox.objects.all():
            for conversation in GarminConversations.objects.filter(inbox=inbox).order_by("selector"):
                print(f"{conversation.user}:")

                print("  Requests:")
                for request in Request.objects.filter(
                    Q(conversation=conversation) & Q(Q() if options["all"] else Q(status__in={0, 1}))
                ).order_by("status"):
                    print(
                        f"    [{request.id}] {request.created}: [{request.get_status_display()}] {request.get_action_display()} :: {request.input}"
                    )

                print("\n  Responses:")
                for response in Response.objects.filter(
                    Q(conversation=conversation) & Q(Q() if options["all"] else Q(status=0))
                ).order_by("status"):
                    print(
                        f'    {response.created}: [{response.get_status_display()}] {response.request.id if response.request else "DIRECT"} :: {response.message}'
                    )
