import email

from django.test import TestCase

from inreach_proxy.lib.processors.actions import GribFetchAction


class GribFetchRequestTestCase(TestCase):
    def testMatchesDefault(self):
        self.assertTrue(GribFetchAction.matches("grib"))

    def testMatchesVariable(self):
        self.assertTrue(GribFetchAction.matches("grib ECMWF"))

    def testDoesNotMatch(self):
        self.assertFalse(GribFetchAction.matches("forecast"))

    def testDefault(self):
        action = GribFetchAction.from_text("grib")
        self.assertIsNotNone(action)
        self.assertEqual(
            action.get_data(),
            {
                "area": "36N,52N,026W,005E",
                "grid": "0.25,0.25",
                "model": "GFS",
                "parameters": ["WIND"],
                "window": "24",
            },
        )

    def testFromText(self):
        action = GribFetchAction.from_text("grib ECMWF")
        self.assertIsNotNone(action)
        self.assertEqual(
            action.get_data(),
            {
                "area": "36N,52N,026W,005E",
                "grid": "0.25,0.25",
                "model": "ECMWF",
                "parameters": ["WIND"],
                "window": "24",
            },
        )

    def testFromEmail(self):
        message = email.message.EmailMessage()
        message.set_content("blah blah\ngrib GFS|38n,40n,25w,20w\n")

        action = GribFetchAction.from_email(message)
        self.assertIsNotNone(action)
        self.assertEqual(
            action.get_data(),
            {
                "area": "38N,40N,025W,020W",
                "grid": "0.25,0.25",
                "model": "GFS",
                "parameters": ["PRMSL", "WAVES", "WIND"],
                "window": "24,48,72,96",
            },
        )
