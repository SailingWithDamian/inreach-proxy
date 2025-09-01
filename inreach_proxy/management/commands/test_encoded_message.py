import base64
import logging
import zlib
from datetime import datetime
from typing import Any

from django.core.management import BaseCommand

from inreach_proxy.lib.business import chunk_message
from inreach_proxy.lib.processors.responses.grib import Grib
from inreach_proxy.models import EmailInbox, GarminConversations

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        email_inbox = EmailInbox.objects.get(id=1)
        conversation = GarminConversations.objects.get(inbox=email_inbox, selector=None)
        # response = SpotForecast(received_time=datetime.fromisoformat('2025-09-01 14:33:31'), request_code='spot:038.39N,27.12W', text='abc123')
        response = Grib(
            received_time=datetime.fromisoformat("2025-09-01 15:45:22"),
            request_code="gfs:38.38N,38.40N,027.14W,027.11W|0.25,0.25|24|WIND",
            grib=b"",
        )
        requests = response.find_request_for_response(conversation)
        print(requests)
        return
        # latitude, longitude = Garmin().get_latest_position("GWTDT")
        # bearing = PredictWind().get_average_bearing("VistaMar")
        # print(
        #     [
        #         decimal_degress_to_dd_mm_ss(latitude, True),
        #         decimal_degress_to_dd_mm_ss(longitude, False),
        #         bearing,
        #     ]
        # )
        #
        # (
        #     min_latitude,
        #     max_latitude,
        #     min_longitude,
        #     max_longitude,
        # ) = calculate_bounding_box(latitude, longitude, bearing)
        #
        # print(
        #     [
        #         min_latitude,
        #         max_latitude,
        #         min_longitude,
        #         max_longitude,
        #     ]
        # )
        #
        # request = f'send gfs:{min_latitude},{max_latitude},{min_longitude},{max_longitude}\nquit\n'
        # print(request)
        #
        # email_inbox = EmailInbox.objects.get(id=1)
        # conversation = GarminConversations.objects.get(inbox=email_inbox, selector=None)
        # out = Outbound(conversation.inbox.smtp_host, conversation.inbox.username, conversation.inbox.password)
        # out.send_email("query@saildocs.com", request, reply_address=conversation.address)
        # return

        with open("/Users/damian/Downloads/gfs20250831192202524.grb", "rb") as fh:
            text = base64.b64encode(zlib.compress(fh.read())).decode()
        for message in chunk_message(text, "grib"):
            print(message)
