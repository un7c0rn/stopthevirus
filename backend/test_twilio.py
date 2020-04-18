import unittest
import mock
from game_engine.firestore import FirestoreDB
import pprint
import json
from typing import Text
from game_engine.database import Player, Challenge
import botocore
import uuid
from game_engine.twilio import TwilioSMSNotifier
import mock
from twilio.rest import Client

_TEST_TWILIO_SMS_CONFIG_PATH = '../twilio/stv-twilio-service-test.json'


def _twilio_client() -> TwilioSMSNotifier:
    return TwilioSMSNotifier(
        json_config_path=_TEST_TWILIO_SMS_CONFIG_PATH)


class TwilioSMSTest(unittest.TestCase):

    def test_normalize_sms_address(self):
        twilio = _twilio_client()
        self.assertEqual(twilio._normalize_sms_address(
            sms_phone_number='555-123-4567'
        ),
            '+15551234567')

        self.assertEqual(twilio._normalize_sms_address(
            sms_phone_number='001-541-754-3010'
        ),
            '+10015417543010')

        self.assertEqual(twilio._normalize_sms_address(
            sms_phone_number='19-49-89-636-48018'
        ),
            '+19498963648018')

        self.assertEqual(twilio._normalize_sms_address(
            sms_phone_number='191 541 754 3010'
        ),
            '+1915417543010')

    def test_normalize_sms_message(self):
        twilio = _twilio_client()
        self.assertEqual(twilio._normalize_sms_message(
            message='hello world'
        ),
            'hello world')

    def test_user_sms_identity(self):
        twilio = _twilio_client()
        self.assertRegex(twilio._user_sms_identity(
            address='19-49-89-636-48018'
        ),
            '[0-9\-a-z]+')

    @mock.patch('twilio.rest.Client.notify')
    def test_send_bulk_sms(self, notify):
        service = mock.MagicMock()
        notify.services = mock.MagicMock(return_value=service)
        twilio = _twilio_client()
        twilio.send_bulk_sms(
            message='message/foo',
            recipient_addresses=[
                '1915417543010',
                '10015417543010',
            ]
        )
        service.notifications.create.assert_called_with(
            to_binding=[
                "{\"binding_type\": \"sms\", \"address\": \"+1915417543010\"}",
                "{\"binding_type\": \"sms\", \"address\": \"+10015417543010\"}",
            ],
            body="message/foo"
        )

    @mock.patch('twilio.rest.Client.messages')
    def test_send_sms(self, messages):
        messages.create = mock.MagicMock()
        twilio = _twilio_client()
        twilio.send_sms(
            message='hello world!',
            recipient_address='10015417543010'
        )
        messages.create.assert_called_with(
            body='hello world!',
            from_=twilio._phone_number,
            to='+10015417543010'
        )


if __name__ == '__main__':
    unittest.main()
