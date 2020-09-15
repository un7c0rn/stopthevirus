from twilio.rest import Client
from abc import ABC, abstractmethod
from game_engine.common import log_message
from typing import Union, Any, Dict, Iterable, List
import json
import phonenumbers
import re
import uuid
import json
from game_engine.common import log_message
from game_engine.emulated_player import EmulatedPlayer

# TODO(brandon) move this into this class and rename SMSNotification
from game_engine.events import SMSEventMessage


class SMSNotifier(ABC):

    @abstractmethod
    def send_bulk_sms(self, message: str, recipient_addresses: Iterable[str]) -> None:
        pass

    @abstractmethod
    def send_sms(self, message: str, recipient_address: str) -> None:
        pass


class TwilioSMSNotifier(SMSNotifier):

    def __init__(self, json_config_path: str, game_id: str):
        with open(json_config_path, 'r') as f:
            config = json.loads(f.read())
            self._client = Client(config['account_sid'], config['auth_token'])
            self._notify_service_sid = config['notify_service_sid']
            self._phone_number = config['phone_number']
            self._game_id = game_id

    def send(self, sms_event_messages: Iterable[SMSEventMessage]) -> None:
        for m in sms_event_messages:
            if len(m.recipient_phone_numbers) > 1:
                log_message(message='calling send_bulk_sms')
                self.send_bulk_sms(
                    message=m.content,
                    recipient_addresses=m.recipient_phone_numbers
                )
            elif len(m.recipient_phone_numbers) == 1:
                log_message(message='calling send_sms')
                self.send_sms(
                    message=m.content,
                    recipient_address=m.recipient_phone_numbers[0]
                )

    def _normalize_sms_address(self, sms_phone_number: str) -> str:
        number = phonenumbers.parse(sms_phone_number, 'US')
        return re.sub(r'[ \-]', '',
                      phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))

    def _normalize_sms_message(self, message: str) -> str:
        return message

    def _user_sms_identity(self, address: str) -> str:
        return str(uuid.uuid4())

    def send_bulk_sms(self, message: str, recipient_addresses: Iterable[str]) -> None:
        notification = self._client.notify.services(self._notify_service_sid).notifications.create(
            to_binding=[
                json.dumps({'binding_type': 'sms', 'address': self._normalize_sms_address(address)}) for address in recipient_addresses],
            body=self._normalize_sms_message(message))
        log_message(message=str(notification.sid), game_id=self._game_id,
                    additional_tags={"phone_number": self._phone_number})

    def send_sms(self, message: str, recipient_address: str) -> None:
        message = self._client.messages \
            .create(
                body=message,
                from_=self._phone_number,
                to=self._normalize_sms_address(recipient_address)
            )


class FakeTwilioSMSNotifier(TwilioSMSNotifier):
    def __init__(self, emulated_devices: List[EmulatedPlayer]):
        self._emulated_devices = emulated_devices
        self._emulated_addresses = [d.phone_number for d in emulated_devices]
        self._emulated_device_map = {}
        for d in emulated_devices:
            self._emulated_device_map[d.phone_number] = d

    def send_bulk_sms(self, message: str, recipient_addresses: Iterable[str]) -> None:
        super().send_bulk_sms(message=message, recipient_addresses=[
            [address for address in recipient_addresses if address not in self._emulated_addresses]
        ])
        for device in self._emulated_devices:
            device.message_handler(message=message)

    def send_sms(self, message: str, recipient_address: str) -> None:
        if recipient_address not in self._emulated_addresses:
            super().send_sms(message=message, recipient_address=recipient_address)
        else:
            device = self._emulated_device_map[recipient_address]
            device.message_handler(message=message)
