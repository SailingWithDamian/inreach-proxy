from django.test import TestCase

from inreach_proxy.lib.processors.responses.spot_forecast import SpotForecast


class SpotForecastResponseTestCase(TestCase):
    def testMatches(self):
        self.assertTrue(
            SpotForecast.matches(
                """
Data extracted from file gfs-20250826-06z.grb dated 2025/08/26 11:13:30z
request code: spot:38.39N,27.13W

Forecast for 38°23N 027°08W (see notes below)
            """
            )
        )

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
        sf = SpotForecast(
            received_time=None,
            request_code="spot:38.39N,27.13W",
            text="""
Data extracted from file gfs-20250826-06z.grb dated 2025/08/26 11:13:30z
request code: spot:38.39N,27.13W

Forecast for 38°23N 027°08W (see notes below)
Date   Time  WIND DIR GUST  PRESS HTSGW DIRPW PERPW
        utc   kts deg  kts    hPa  mtrs   deg   sec
----------- ----- --- ---- ------ ----- ----- -----
08-26 12:00   6.5 345  7.0 1027.1   1.4   316  12.2
08-26 18:00   7.2 335  9.0 1026.2   1.4   321  11.9

08-27 00:00   7.7 349  8.6 1027.0   1.3   319  11.7
08-27 06:00   8.0 340 10.1 1025.8   1.1   327  11.3
08-27 12:00   8.2 337 10.1 1027.2   1.1   332  11.0
08-27 18:00  11.5 342 12.0 1026.7   1.2   323  11.7

08-28 00:00   7.7 351  9.0 1027.8   1.1   333  11.1
08-28 06:00   6.2 356  7.8 1027.1   1.0   336  10.8
08-28 12:00   4.8 354  5.9 1028.5   1.0   320  11.4
08-28 18:00   3.1 357  5.1 1026.7   1.1   325  11.5

08-29 00:00   2.5 040  3.3 1027.1   1.0   324  11.4
08-29 06:00   2.1 252  2.7 1025.1   0.9   321  11.1
08-29 12:00   6.5 264  6.7 1026.0   0.8   319  10.9
08-29 18:00  11.4 255 11.7 1023.7   0.8   316  10.5

08-30 00:00   9.9 274 10.7 1024.4   0.8   308  10.3
08-30 06:00   9.9 255 11.0 1022.8   0.8   303  10.1
08-30 12:00  12.8 255 13.5 1024.9   0.8   308   9.8
08-30 18:00   8.5 011 10.7 1025.2   0.7   309   9.2

08-31 00:00  10.3 031 10.1 1027.4   0.8   176  13.5
08-31 06:00   9.9 026  9.5 1027.0   0.8   284   9.7

Refer to notice & warnings sent 2025/08/26 14:47:57, for another copy send a (blank) email to: SpotWarning@saildocs.com

=====
Thanks for using Saildocs, an Internet document retrieval 
service for the bandwidth-impaired.  By using this service
you agree to the Saildocs terms and conditions (send a 
blank email to: terms@saildocs.com for a copy). 

Saildocs is a service of Sailmail, a membership-owned email 
service built by cruising sailors for cruising sailors. 
Sailmail provides world-wide email via marine-band radio, 
internet and satellite including support for the Iridium GO!

For more information on SailMail see the web page at www.sailmail.com 
or send a query to the office at sysop@sailmail.com. 
More information on Saildocs is available by sending an email to 
info@saildocs.com, this will return the how-to document (about 5K).""",
        )
        messages = sf.get_messages()

        self.assertEqual(len(messages), 3)
        self.assertEqual(
            messages[0],
            """38.39N 27.13W 08-26 12:00:
6.5kts G:7.0 @ 345
1.4m/12.2s @ 316
1027.1mb

38.39N 27.13W 08-26 18:00:
7.2kts G:9.0 @ 335
1.4m/11.9s @ 321
1026.2mb""",
        )

        self.assertEqual(
            messages[1],
            """38.39N 27.13W 08-27 00:00:
7.7kts G:8.6 @ 349
1.3m/11.7s @ 319
1027.0mb

38.39N 27.13W 08-27 06:00:
8.0kts G:10.1 @ 340
1.1m/11.3s @ 327
1025.8mb""",
        )

        self.assertEqual(
            messages[2],
            """38.39N 27.13W 08-27 12:00:
8.2kts G:10.1 @ 337
1.1m/11.0s @ 332
1027.2mb

38.39N 27.13W 08-27 18:00:
11.5kts G:12.0 @ 342
1.2m/11.7s @ 323
1026.7mb""",
        )
