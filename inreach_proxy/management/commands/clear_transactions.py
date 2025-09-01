import logging
from typing import Any

from django.core.management import BaseCommand

from inreach_proxy.models import Response, Request

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        """Clear existing transactions."""
        Response.objects.all().delete()
        Request.objects.all().delete()
