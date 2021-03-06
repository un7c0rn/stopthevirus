import unittest
import mock
from game_engine.firestore import FirestoreDB
from game_engine.database import Entry
from dataclasses import dataclass
from functions.sms import main as sms_endpoint
import random
from game_engine.common import GameIntegrationTestLogStream
from typing import List
import uuid
import re
from game_engine.common import log_message

_VIEWS_LOWER_BOUND = 50
_VIEWS_UPPER_BOUND = 1e6


def _is_voting_option(message: str) -> bool:
    return re.search('(Reply by.+with the letter of the player you\'re voting out)'
                     '|(Reply by.+with the letter of the player you\'re voting to WIN!)',
                     message, flags=re.I) is not None


def _is_challenge(message: str) -> bool:
    return re.search('Post a video to your TikTok feed.+',
                     message, flags=re.I) is not None


def _challenge_id_from_message(message: str) -> str:
    return re.search('[^\/]+\/challenge-submission\/[^\/]+\/[^\/]+\/([a-zA-Z0-9]+)', message).group(1)


def _parse_voting_options(message: str) -> List[str]:
    return re.findall('^([A-Z])\.', message, flags=re.MULTILINE)


@dataclass
class EmulatedPlayer:
    id: str
    name: str
    tiktok: str
    phone_number: str
    test_stream: GameIntegrationTestLogStream
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
            challenge_id=_challenge_id_from_message(message=message),
            team_id=player.team_id,
            url=f'http://tiktok.com/@{self.tiktok}/{str(uuid.uuid4())}'
        )

    def message_handler(self, message: str) -> None:
        self.test_stream.add_user_received_sms(
            user_name=self.name, message=message)
        if _is_voting_option(message):
            body = self._select_vote_option(message)
            sms_request = mock.MagicMock()

            def get_fn(field):
                if field == 'From':
                    return self.phone_number
                if field == 'Body':
                    return body
            sms_request.form.get = get_fn
            sms_endpoint.sms_http(sms_request)
            self.test_stream.add_user_sent_sms(request={
                'From': self.phone_number,
                'Body': body
            })
        elif _is_challenge(message):
            challenge_entry = self._entry_for_message(message)
            self.gamedb.add_challenge_entry(challenge_entry)
            self.test_stream.add_user_challenge_entry(challenge_entry)