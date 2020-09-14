import unittest
import mock
from game_engine.firestore import FirestoreDB
from game_engine.database import Entry
from dataclasses import dataclass
from functions.sms import main as sms_endpoint
import random

_VIEWS_LOWER_BOUND = 50
_VIEWS_UPPER_BOUND = 1e6


def _is_voting_option(self, message: str) -> bool:
    return "vote" in message.lower()


def _is_challenge(self, message: str) -> bool:
    return "challenge" in message.lower()


def _parse_challenge_id(self, message: str) -> str:
    return ""


def _parse_voting_options(self, message: str) -> List[str]:
    # TODO(brandon): write actual parser.
    return ['A', 'B', 'C']


@dataclass
class EmulatedPlayer:
    id: str,
    name: str
    tiktok: str
    phone_number: str
    test_stream: TestLogger
    gamedb: FirestoreDB

    def _select_vote_option(self, message: str) -> str:
        return random.choice(_parse_voting_options(message))

    def _entry_for_message(self, message: str) -> str:
        player = self.gamedb.player_from_id(self.id)
        views = random.randint(_VIEWS_LOWER_BOUND, _VIEWS_UPPER_BOUND)
        return Entry(
            likes=random.random() * views,
            views=views,
            player_id=self.id,
            tribe_id=player.tribe_id,
            challenge_id=self._parse_challenge_id(message)
            team_id=player.team_id,
            url=f'http://tiktok.com/@{self.tiktok}/{uuid.uuid4()}'
        )

    def message_handler(self, message: str) -> None:
        self.test_stream.user_received_sms(message=message)
        if _is_voting_option(message):
            body = self._select_vote_option(message)
            sms_request = {
                {
                    'From': self.phone_number,
                    'Body': body
                }
            }
            sms_endpoint.sms_http(request)
            test_stream.add_user_sent_sms(request=sms_request)
        elif _is_challenge(message):
            challenge_entry = self._entry_for_message(message)
            self.gamedb.add_challenge_entry(challenge_entry)
            self.test_stream.add_user_challenge_entry(challenge_entry)
        else:
            raise RuntimeError(
                f'Emulation mode does not support message \'{message}\'')
