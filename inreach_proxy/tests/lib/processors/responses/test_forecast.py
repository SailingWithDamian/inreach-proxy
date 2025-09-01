from email import policy
from email.parser import BytesParser

from django.conf import settings
from django.test import TestCase

from inreach_proxy.lib.parsers import SailDocsMessageParser
from inreach_proxy.lib.processors.responses.spot_forecast import SpotForecast


class SpotForecastResponseTestCase(TestCase):
    def testMatches(self):
        self.assertTrue(SpotForecast.matches("spot:38.39N,27.13W"))

    def testDoesNotMatch(self):
        self.assertFalse(
            SpotForecast.matches(
                """
Grib extracted from file ecmwf-20250825-00z.grb dated 2025/08/25 08:58:38
request code: ECMWF:36n,52n,026w,005e|0.25,0.25|24,48,72,96|PRMSL,WAVES,WIND

NOTICE:
            """
            )
        )

    def testForecastParsing(self):
        email_file = settings.BASE_DIR / "inreach_proxy" / "tests" / "data" / "forecast-2.eml"
        with email_file.open("rb") as fh:
            email_msg = BytesParser(policy=policy.default).parse(fh)
            parsed_email = SailDocsMessageParser().process(email_msg)

        self.assertEqual(len(parsed_email.responses), 1)
        self.assertTrue(isinstance(parsed_email.responses[0], SpotForecast))
        messages = parsed_email.responses[0].get_messages()

        self.assertEqual(len(messages), 3)
        self.assertEqual(
            messages[0],
            (
                "38.39N 027.13W\n"
                "08-27 12:00\n"
                "Wind: 10.4kts gust 12.4kts @ 338\n"
                "Sea: 1.1m interval 11.2s @ 331\n"
                "Pressure: 1027.1mb"
            ),
        )
        self.assertEqual(
            messages[1],
            (
                "38.39N 027.13W\n"
                "08-27 18:00\n"
                "Wind: 10.9kts gust 11.6kts @ 358\n"
                "Sea: 1.2m interval 11.2s @ 332\n"
                "Pressure: 1026.7mb"
            ),
        )
        self.assertEqual(
            messages[2],
            (
                "38.39N 027.13W\n"
                "08-28 00:00\n"
                "Wind: 8.0kts gust 8.6kts @ 343\n"
                "Sea: 1.1m interval 11.0s @ 331\n"
                "Pressure: 1027.9mb"
            ),
        )

    def testPartialForecastParsing(self):
        email_file = settings.BASE_DIR / "inreach_proxy" / "tests" / "data" / "forecast-1.eml"
        with email_file.open("rb") as fh:
            email_msg = BytesParser(policy=policy.default).parse(fh)
            parsed_email = SailDocsMessageParser().process(email_msg)

        self.assertEqual(len(parsed_email.responses), 1)
        self.assertTrue(isinstance(parsed_email.responses[0], SpotForecast))

        messages = parsed_email.responses[0].get_messages()
        self.assertEqual(len(messages), 3)
