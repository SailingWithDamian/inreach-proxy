from django.test import TestCase

from inreach_proxy.lib.processors.responses.grib import Grib


class GribResponseTestCase(TestCase):
    def testMatches(self):
        self.assertTrue(
            Grib.matches(
                """
Grib extracted from file gfs-20250820-12z.grb dated 2025/08/20 17:26:14
request code: GFS:36n,52n,026w,005e|0.25,0.25|24,48,72,96|PRMSL,WAVES,WIND

Refer to notice & warnings sent 2025/08/20 14:45:20, for another copy send a (blank) email to: GribWarning@saildocs.com
            """
            )
        )

    def testDoesNotMatch(self):
        self.assertFalse(
            Grib.matches(
                """
Data extracted from file gfs-20250826-06z.grb dated 2025/08/26 11:13:30z
request code: spot:38.39N,27.13W

            """
            )
        )
