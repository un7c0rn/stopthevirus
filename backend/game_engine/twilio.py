from twilio.rest import Client
from abc import ABC, abstractmethod
from game_engine.common import log_message
from typing import Text, Union, Any, Dict, Iterable
import json
import phonenumbers
import re
import uuid
import json

# TODO(brandon) move this into this class and rename SMSNotification
from game_engine.events import SMSEventMessage


class SMSNotifier(ABC):

    @abstractmethod
    def send_bulk_sms(self, message: Text, recipient_addresses: Iterable[Text]) -> None:
        pass

    @abstractmethod
    def send_sms(self, message: Text, recipient_address: Text) -> None:
        pass


class TwilioSMSNotifier(SMSNotifier):

    def __init__(self, json_config_path: Text, game_id: Text):
        with open(json_config_path, 'r') as f:
            config = json.loads(f.read())
            self._client = Client(config['account_sid'], config['auth_token'])
            self._notify_service_sid = config['notify_service_sid']
            self._phone_number = config['phone_number']
            self._game_id = game_id

    def send(self, sms_event_messages: Iterable[SMSEventMessage]) -> None:
        pass
        for m in sms_event_messages:
            if len(m.recipient_phone_numbers) > 1:
                print('invoking send_bulk_sms')
                self.send_bulk_sms(
                    message=m.content,
                    recipient_addresses=m.recipient_phone_numbers
                )
            elif len(m.recipient_phone_numbers) == 1:
                print('invoking send_sms')
                self.send_sms(
                    message=m.content,
                    recipient_address=m.recipient_phone_numbers[0]
                )

    def _normalize_sms_address(self, sms_phone_number: Text) -> Text:
        number = phonenumbers.parse(sms_phone_number, 'US')
        return re.sub(r'[ \-]', '',
                      phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))

    def _normalize_sms_message(self, message: Text) -> Text:
        return message

    def _user_sms_identity(self, address: Text) -> Text:
        return str(uuid.uuid4())

    def send_bulk_sms(self, message: Text, recipient_addresses: Iterable[Text]) -> None:
        notification = self._client.notify.services(self._notify_service_sid).notifications.create(
            to_binding=[
                json.dumps({'binding_type': 'sms', 'address': self._normalize_sms_address(address)}) for address in recipient_addresses],
            body=self._normalize_sms_message(message))
        log_message(message=str(notification.sid), game_id=self._game_id, additional_tags={"phone_number":self._phone_number})

    def send_sms(self, message: Text, recipient_address: Text) -> None:
        message = self._client.messages \
            .create(
                body=message,
                from_=self._phone_number,
                to=self._normalize_sms_address(recipient_address)
            )
