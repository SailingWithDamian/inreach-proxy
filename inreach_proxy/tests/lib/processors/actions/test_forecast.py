import email

import requests_mock
from django.test import TestCase

from inreach_proxy.lib.processors.actions import SpotForecastAction
from inreach_proxy.tests.consts import PLACE_HOLDER_KML


class SpotForecastRequestTestCase(TestCase):
    def testMatchesDefault(self):
        self.assertTrue(SpotForecastAction.matches("forecast"))

    def testMatchesVariable(self):
        self.assertTrue(SpotForecastAction.matches("forecast 38N,025W"))

    def testDoesNotMatch(self):
        self.assertFalse(SpotForecastAction.matches("ping"))

    def testDefault(self):
        action = SpotForecastAction.from_text("forecast")

        self.assertIsNotNone(action)
        self.assertEqual(
            action.get_data(),
            {"latitude": None, "longitude": None},
        )

    def testFromText(self):
        action = SpotForecastAction.from_text("forecast 38N,025W")
        self.assertIsNotNone(action)
        self.assertEqual(
            action.get_data(),
            {
                "latitude": "38N",
                "longitude": "025W",
            },
        )

    def testFromEmail(self):
        message = email.message.EmailMessage()
        message.set_content("blah blah\nforecast\n")

        with requests_mock.Mocker() as m:
            m.get("https://share.garmin.com/Feed/Share/test", text=PLACE_HOLDER_KML)
            action = SpotForecastAction.from_email(message, {"map_share_key": "test"})

        self.assertIsNotNone(action)
        self.assertEqual(
            action.get_data(),
            {
                "latitude": "38.23N",
                "longitude": "027.8W",
            },
        )
