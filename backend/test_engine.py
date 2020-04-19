import unittest
import mock
from game_engine.firestore import FirestoreDB
import pprint
import json
from typing import Text
from game_engine.database import Player, Challenge, Entry, Team, Tribe
import botocore
import uuid
from game_engine.twilio import TwilioSMSNotifier
import mock
from twilio.rest import Client
from game_engine.engine import Engine
from game_engine.common import GameOptions
from game_engine.firestore import FirestoreDB
from game_engine import events
import random
import time

_TEST_AMAZON_SQS_CONFIG_PATH = '../amazon/stopthevirus.fifo.json'
_TEST_TWILIO_SMS_CONFIG_PATH = '../twilio/stv-twilio.json'
_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
_TEST_GAME_ID = '7rPwCJaiSkxYgDocGDw1'

# TODO(brandon) deduplicate into test common

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

_gamedb = FirestoreDB(
    json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=_TEST_GAME_ID)

_TEST_EVENTS = [
    events.NotifyTribalChallengeEvent(
        game_id=_TEST_GAME_ID,
        challenge=_TEST_CHALLENGE
    ),
    events.NotifyPlayerScoreEvent(
        game_id=_TEST_GAME_ID,
        player=_TEST_PLAYER1,
        challenge=_TEST_CHALLENGE,
        entry=_TEST_ENTRY,
        points=100
    ),
    events.NotifyTeamReassignmentEvent(
        game_id=_TEST_GAME_ID,
        player=_TEST_PLAYER1,
        team=_TEST_TEAM1
    ),
    events.NotifySingleTeamCouncilEvent(
        game_id=_TEST_GAME_ID,
        winning_player=_TEST_PLAYER1,
        losing_players=[_TEST_PLAYER1, _TEST_PLAYER2]
    ),
    events.NotifySingleTribeCouncilEvent(
        game_id=_TEST_GAME_ID,
        winning_teams=[_TEST_TEAM1],
        losing_teams=[_TEST_TEAM2]
    ),
    events.NotifyMultiTribeCouncilEvent(
        game_id=_TEST_GAME_ID,
        winning_tribe=_TEST_TRIBE1,
        losing_tribe=_TEST_TRIBE2
    ),
    events.NotifyFinalTribalCouncilEvent(
        game_id=_TEST_GAME_ID,
        finalists=[_TEST_PLAYER1, _TEST_PLAYER2]
    ),
    events.NotifyPlayerVotedOutEvent(
        game_id=_TEST_GAME_ID,
        player=_TEST_PLAYER1
    ),
    events.NotifyTribalCouncilCompletionEvent(
        game_id=_TEST_GAME_ID
    ),
    events.NotifyWinnerAnnouncementEvent(
        game_id=_TEST_GAME_ID,
        winner=_TEST_PLAYER2
    ),
    events.NotifyImmunityAwardedEvent(
        game_id=_TEST_GAME_ID,
        team=_TEST_TEAM2
    )
]


class EngineTest(unittest.TestCase):

    def test_event_processing(self):
        return

        engine = Engine(
            options=GameOptions(),
            # TODO(brandon) each game can instantiate its own queue
            # by game id
            sqs_config_path=_TEST_AMAZON_SQS_CONFIG_PATH,
            twilio_config_path=_TEST_TWILIO_SMS_CONFIG_PATH,
            gamedb=_gamedb
        )

        for event in _TEST_EVENTS:
            engine.add_event(event)
        
        time.sleep(60)

if __name__ == '__main__':
    unittest.main()
