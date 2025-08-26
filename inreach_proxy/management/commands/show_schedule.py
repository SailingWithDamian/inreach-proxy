import logging
from typing import Any

from django.core.management import BaseCommand

from inreach_proxy.models import EmailInbox, GarminConversations, ScheduledRequest

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        """Show the current request/response statuses."""
        for inbox in EmailInbox.objects.all():
            for conversation in GarminConversations.objects.filter(inbox=inbox).order_by("selector"):
                print(f"{conversation.user}:")
                for scheduled_request in ScheduledRequest.objects.filter(conversation=conversation):
                    print(
                        f"    [{scheduled_request.get_group_display()}] {scheduled_request.get_action_display()} :: {scheduled_request.input}"
                    )
