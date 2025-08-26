import email

from django.test import TestCase

from inreach_proxy.lib.processors.actions import PingPongAction


class PingRequestTestCase(TestCase):
    def testMatchesDefault(self):
        self.assertTrue(PingPongAction.matches("ping"))

    def testMatchesVariable(self):
        self.assertTrue(PingPongAction.matches("ping pong"))

    def testDoesNotMatch(self):
        self.assertFalse(PingPongAction.matches("bob"))

    def testDefault(self):
        action = PingPongAction.from_text("ping")
        self.assertIsNotNone(action)
        self.assertEqual(action.execute(), "pong default")

    def testFromText(self):
        action = PingPongAction.from_text("ping bob")
        self.assertIsNotNone(action)
        self.assertEqual(action.execute(), "pong bob")

    def testFromEmail(self):
        message = email.message.EmailMessage()
        message.set_content("blah blah\nping test\n")

        action = PingPongAction.from_email(message)
        self.assertIsNotNone(action)
        self.assertEqual(action.execute(), "pong test")
