import unittest
import mock
from game_engine.firestore import FirestoreDB
import pprint
import json
from game_engine.events import AmazonSQS
from game_engine.events import *
from typing import Text
from game_engine.database import Player, Challenge
import botocore
import uuid
from contextlib import contextmanager

_TEST_AMAZON_SQS_CONFIG_PATH = '../amazon/stopthevirus-test.fifo.json'
_TEST_GAME_ID = '1234567'
_TEST_ASYNC = False

_TEST_PLAYER1 = Player(
    id='id/foo1',
    tiktok='tiktok/bar',
    email='email/foo',
    phone_number='sms/bar',
    tribe_id='tribe/foo',
    team_id='team/bar',
    active=True
)
_TEST_PLAYER2 = Player(
    id='id/foo2',
    tiktok='tiktok/bar',
    email='email/foo',
    phone_number='sms/bar',
    tribe_id='tribe/foo',
    team_id='team/bar',
    active=True
)
_TEST_CHALLENGE = Challenge(
    id='foo',
    name='bar'
)
_TEST_ENTRY = Entry(
    id='id/foo',
    likes=100,
    views=1000,
    player_id='player/foo',
    tribe_id='tribe/bar',
    challenge_id='challenge/foo',
    team_id='team/bar',
    url='https://www.tiktok.com/@ifrc/video/6816427450801736965'
)
_TEST_TEAM1 = Team(
    id='id/foo1',
    name='team/bar',
    size=5,
    tribe_id='tribe/foo'
)
_TEST_TEAM2 = Team(
    id='id/foo2',
    name='team/bar',
    size=5,
    tribe_id='tribe/foo'
)
_TEST_TRIBE1 = Tribe(
    id='id/foo1',
    name='SIDAMA',
    size=1e6
)
_TEST_TRIBE2 = Tribe(
    id='id/foo2',
    name='TIGRAWAY',
    size=500e3
)


@contextmanager
def aws_test_queue() -> AmazonSQS:
    sqs = AmazonSQS(json_config_path=_TEST_AMAZON_SQS_CONFIG_PATH)
    try:
        queue = sqs._client.create_queue(
            QueueName="{}.fifo".format(str(uuid.uuid4())),
            Attributes={
                "FifoQueue": "True"
            })
        sqs._url = queue['QueueUrl']
        yield sqs
    finally:
        sqs._client.delete_queue(QueueUrl=sqs._url)
        pass


class AmazonSQSTest(unittest.TestCase):

    def setUp(self):
        self._game_options = GameOptions()
        self._game_options.game_schedule = STV_I18N_TABLE['US']

    def test_notify_tribal_challenge_event(self):
        with aws_test_queue() as test_queue:
            test_queue.put(
                event=NotifyTribalChallengeEvent(
                    game_id=_TEST_GAME_ID,
                    game_options=self._game_options,
                    challenge=_TEST_CHALLENGE
                ),
                blocking=(not _TEST_ASYNC)
            )

            self.assertEqual(
                test_queue.get().to_dict(),
                {
                    "class": "NotifyTribalChallengeEvent",
                    "game_id": "1234567",
                    "game_options": None,
                    "challenge":
                    {
                        "class": "Challenge",
                        "id": "foo",
                        "name": "bar",
                        "message": "",
                        "start_timestamp": 0,
                        "end_timestamp": 0,
                        "complete": False
                    }
                }
            )

    def test_notify_player_score_event(self):
        with aws_test_queue() as test_queue:
            test_queue.put(
                event=NotifyPlayerScoreEvent(
                    game_id=_TEST_GAME_ID,
                    game_options=self._game_options,
                    player=_TEST_PLAYER1,
                    challenge=_TEST_CHALLENGE,
                    entry=_TEST_ENTRY,
                    points=100
                ),
                blocking=(not _TEST_ASYNC)
            )

            self.assertEqual(
                test_queue.get().to_dict(),
                {
                    "class": "NotifyPlayerScoreEvent",
                    "game_id": "1234567",
                    "game_options": None,
                    "player": {
                        "class": "Player",
                        "id": "id/foo1",
                        "tiktok": "tiktok/bar",
                        "email": "email/foo",
                        "phone_number": "sms/bar",
                        "tribe_id": "tribe/foo",
                        "team_id": "team/bar",
                        "active": True
                    },
                    "challenge": {
                        "class": "Challenge",
                        "id": "foo",
                        "name": "bar",
                        "message": "",
                        "start_timestamp": 0,
                        "end_timestamp": 0,
                        "complete": False
                    },
                    "entry": {
                        "class": "Entry",
                        "id": "id/foo",
                        "likes": 100,
                        "views": 1000,
                        "player_id": "player/foo",
                        "tribe_id": "tribe/bar",
                        "challenge_id": "challenge/foo",
                        "team_id": "team/bar",
                        "url": "https://www.tiktok.com/@ifrc/video/6816427450801736965"
                    },
                    "points": 100
                }
            )

    def test_notify_team_reassignment_event(self):
        with aws_test_queue() as test_queue:
            test_queue.put(
                event=NotifyTeamReassignmentEvent(
                    game_id=_TEST_GAME_ID,
                    game_options=self._game_options,
                    player=_TEST_PLAYER1,
                    team=_TEST_TEAM1
                ),
                blocking=(not _TEST_ASYNC)
            )

            self.assertEqual(
                test_queue.get().to_dict(),
                {
                    "class": "NotifyTeamReassignmentEvent",
                    "game_id": "1234567",
                    "game_options": None,
                    "player": {
                        "class": "Player",
                        "id": "id/foo1",
                        "tiktok": "tiktok/bar",
                        "email": "email/foo",
                        "phone_number": "sms/bar",
                        "tribe_id": "tribe/foo",
                        "team_id": "team/bar",
                        "active": True
                    },
                    "team": {
                        "class": "Team",
                        "id": "id/foo1",
                        "name": "team/bar",
                        "size": 5,
                        "tribe_id": "tribe/foo",
                        "active": True
                    }
                })

    def test_notify_single_team_council_event(self):
        with aws_test_queue() as test_queue:
            test_queue.put(
                event=NotifySingleTeamCouncilEvent(
                    game_id=_TEST_GAME_ID,
                    game_options=self._game_options,
                    winning_player=_TEST_PLAYER1,
                    losing_players=[_TEST_PLAYER1, _TEST_PLAYER2]
                ),
                blocking=(not _TEST_ASYNC)
            )

            self.assertEqual(
                test_queue.get().to_dict(),
                {
                    "class": "NotifySingleTeamCouncilEvent",
                    "game_id": "1234567",
                    "game_options": None,
                    "winning_player": {
                        "class": "Player",
                        "id": "id/foo1",
                        "tiktok": "tiktok/bar",
                        "email": "email/foo",
                        "phone_number": "sms/bar",
                        "tribe_id": "tribe/foo",
                        "team_id": "team/bar",
                        "active": True
                    },
                    "losing_players": [
                        {
                            "class": "Player",
                            "id": "id/foo1",
                            "tiktok": "tiktok/bar",
                            "email": "email/foo",
                            "phone_number": "sms/bar",
                            "tribe_id": "tribe/foo",
                            "team_id": "team/bar",
                            "active": True
                        },
                        {
                            "class": "Player",
                            "id": "id/foo2",
                            "tiktok": "tiktok/bar",
                            "email": "email/foo",
                            "phone_number": "sms/bar",
                            "tribe_id": "tribe/foo",
                            "team_id": "team/bar",
                            "active": True
                        }
                    ]
                })

    def test_notify_single_tribe_council_event(self):
        with aws_test_queue() as test_queue:
            test_queue.put(
                event=NotifySingleTribeCouncilEvent(
                    game_id=_TEST_GAME_ID,
                    game_options=self._game_options,
                    winning_teams=[_TEST_TEAM1],
                    losing_teams=[_TEST_TEAM2]
                ),
                blocking=(not _TEST_ASYNC)
            )

            self.assertEqual(
                test_queue.get().to_dict(),
                {
                    "class": "NotifySingleTribeCouncilEvent",
                    "game_id": "1234567",
                    "game_options": None,
                    "winning_teams": [
                        {
                            "class": "Team",
                            "id": "id/foo1",
                            "name": "team/bar",
                            "size": 5,
                            "tribe_id": "tribe/foo",
                            "active": True
                        }
                    ],
                    "losing_teams": [
                        {
                            "class": "Team",
                            "id": "id/foo2",
                            "name": "team/bar",
                            "size": 5,
                            "tribe_id": "tribe/foo",
                            "active": True
                        }
                    ]
                })

    def test_notify_multi_tribe_council_event(self):
        with aws_test_queue() as test_queue:
            test_queue.put(
                event=NotifyMultiTribeCouncilEvent(
                    game_id=_TEST_GAME_ID,
                    game_options=self._game_options,
                    winning_tribe=_TEST_TRIBE1,
                    losing_tribe=_TEST_TRIBE2
                ),
                blocking=(not _TEST_ASYNC)
            )

            self.assertEqual(
                test_queue.get().to_dict(),
                {
                    "class": "NotifyMultiTribeCouncilEvent",
                    "game_id": "1234567",
                    "game_options": None,
                    "winning_tribe": {
                        "class": "Tribe",
                        "id": "id/foo1",
                        "name": "SIDAMA",
                        "size": 1000000.0,
                        "active": True
                    },
                    "losing_tribe": {
                        "class": "Tribe",
                        "id": "id/foo2",
                        "name": "TIGRAWAY",
                        "size": 500000.0,
                        "active": True
                    }
                })

    def test_notify_final_tribal_council_event(self):
        with aws_test_queue() as test_queue:
            test_queue.put(
                event=NotifyFinalTribalCouncilEvent(
                    game_id=_TEST_GAME_ID,
                    game_options=self._game_options,
                    finalists=[_TEST_PLAYER1, _TEST_PLAYER2]
                ),
                blocking=(not _TEST_ASYNC)
            )

            self.assertEqual(
                test_queue.get().to_dict(),
                {
                    "class": "NotifyFinalTribalCouncilEvent",
                    "game_id": "1234567",
                    "game_options": None,
                    "finalists": [
                        {
                            "class": "Player",
                            "id": "id/foo1",
                            "tiktok": "tiktok/bar",
                            "email": "email/foo",
                            "phone_number": "sms/bar",
                            "tribe_id": "tribe/foo",
                            "team_id": "team/bar",
                            "active": True
                        },
                        {
                            "class": "Player",
                            "id": "id/foo2",
                            "tiktok": "tiktok/bar",
                            "email": "email/foo",
                            "phone_number": "sms/bar",
                            "tribe_id": "tribe/foo",
                            "team_id": "team/bar",
                            "active": True
                        }
                    ]
                })

    def test_notify_player_voted_out_event(self):
        with aws_test_queue() as test_queue:
            test_queue.put(
                event=NotifyPlayerVotedOutEvent(
                    game_id=_TEST_GAME_ID,
                    game_options=self._game_options,
                    player=_TEST_PLAYER1
                ),
                blocking=(not _TEST_ASYNC)
            )

            self.assertEqual(
                test_queue.get().to_dict(),
                {
                    "class": "NotifyPlayerVotedOutEvent",
                    "game_id": "1234567",
                    "game_options": None,
                    "player": {
                        "class": "Player",
                        "id": "id/foo1",
                        "tiktok": "tiktok/bar",
                        "email": "email/foo",
                        "phone_number": "sms/bar",
                        "tribe_id": "tribe/foo",
                        "team_id": "team/bar",
                        "active": True
                    }
                })

    def test_notify_tribal_council_completion_event(self):
        with aws_test_queue() as test_queue:
            test_queue.put(
                event=NotifyTribalCouncilCompletionEvent(
                    game_id=_TEST_GAME_ID,
                    game_options=self._game_options
                ),
                blocking=(not _TEST_ASYNC)
            )

            self.assertEqual(
                test_queue.get().to_dict(),
                {
                    "class": "NotifyTribalCouncilCompletionEvent",
                    "game_id": "1234567",
                    "game_options": None
                })

    def test_notify_winner_announcement_event(self):
        with aws_test_queue() as test_queue:
            test_queue.put(
                event=NotifyWinnerAnnouncementEvent(
                    game_id=_TEST_GAME_ID,
                    game_options=self._game_options,
                    winner=_TEST_PLAYER2
                ),
                blocking=(not _TEST_ASYNC)
            )

            self.assertEqual(
                test_queue.get().to_dict(),
                {
                    "class": "NotifyWinnerAnnouncementEvent",
                    "game_id": "1234567",
                    "game_options": None,
                    "winner": {
                        "class": "Player",
                        "id": "id/foo2",
                        "tiktok": "tiktok/bar",
                        "email": "email/foo",
                        "phone_number": "sms/bar",
                        "tribe_id": "tribe/foo",
                        "team_id": "team/bar",
                        "active": True
                    }
                })

    def test_notify_immunity_awarded_event(self):
        with aws_test_queue() as test_queue:
            test_queue.put(
                event=NotifyImmunityAwardedEvent(
                    game_id=_TEST_GAME_ID,
                    game_options=self._game_options,
                    team=_TEST_TEAM2
                ),
                blocking=(not _TEST_ASYNC)
            )

            self.assertEqual(
                test_queue.get().to_dict(),
                {
                    "class": "NotifyImmunityAwardedEvent",
                    "game_id": "1234567",
                    "game_options": None,
                    "team": {
                        "class": "Team",
                        "id": "id/foo2",
                        "name": "team/bar",
                        "size": 5,
                        "tribe_id": "tribe/foo",
                        "active": True
                    }
                })


if __name__ == '__main__':
    unittest.main()
