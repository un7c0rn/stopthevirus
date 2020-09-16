import unittest
import mock
from typing import Dict
from matchmaker_service import MatchmakerService
from game_engine.common import GameSchedule, ISODayOfWeek, STV_I18N_TABLE
from game_engine.firestore import FirestoreDB
from game_engine.matchmaker import MatchMakerRoundRobin
from game_engine.database import Challenge
from game_engine.common import GameOptions, GameSchedule, GameClockMode, STV_I18N_TABLE, ISODayOfWeek, log_message
from game_engine.twilio import FakeTwilioSMSNotifier
from game_engine.engine import Engine
from game_engine.emulated_player import EmulatedPlayer
import time
import uuid
from game_engine.common import log_message
from game_engine.common import GameIntegrationTestLogStream

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
_TEST_TWILIO_SMS_CONFIG_PATH = '../twilio/stv-twilio-service-test.json'

_TEST_CHALLENGES = [
    Challenge(
        name='Best AAAAAAA cell phone video', message='NOP'
    ),
    Challenge(
        name='Most creative one mile run', message='NOP'
    ),
    Challenge(
        name='Dopest hand made AAAAAAA T-Shirt Design', message='NOP'
    ),
    Challenge(
        name='Best livestream rant on AAAAAAA', message='NOP'
    ),
    Challenge(
        name='Best AAAAAAA G-Mix', message='NOP'
    ),
    Challenge(
        name='Craziest selfie in AAAAAAA', message='NOP'
    ),
    Challenge(
        name='Best acoustic replay of AAAAAAA', message='NOP'
    ),
    Challenge(
        name='Most creative AAAAAAA video', message='NOP'
    ),
    Challenge(
        name='Most innovative way to get in the AAAAAAA', message='NOP'
    ),
    Challenge(
        name='Most fire video of cracking this code AAAAAAA', message='NOP'
    ),
    Challenge(
        name='Make a video decoding the meaning of AAAAAAA', message='NOP'
    ),
    Challenge(
        name='Best way to social distance at AAAAAAA', message='NOP'
    ),
    Challenge(
        name='Most fire AAAAAAA', message='NOP'
    ),
    Challenge(
        name='Best AAAAAAA Karaoke', message='NOP'
    ),
    Challenge(
        name='Best AAAAAAA dance', message='NOP'
    ),
    Challenge(
        name='Most fire scene reenactment from of AAAAAAA', message='NOP'
    ),
]

_EMULATED_PLAYERS = [
    ('Liam', 'lusttforlife', '+10000000001'),
    ('Noah', 'velvetcanyon', '+10000000002'),
    ('Oliver', 'satiregram', '+10000000003'),
    ('William', 'everydaypursuits', '+10000000004'),
    ('Elijah', 'apartmenttherapy', '+10000000005'),
    ('James', 'doyoutravel', '+10000000006'),
    ('Benjamin', 'workparty', '+10000000007'),
    ('Lucas', 'plantifulsoul', '+10000000008'),
    ('Mason', 'therow', '+10000000009'),
    ('Ethan', 'whats_ur_sign', '+10000000000'),
]

_REAL_PLAYERS = [
    ('Brandon', 'un7c0rn', '+17742593288'),
]


class IntegrationTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_integration(self):
        test_id = str(uuid.uuid4())
        # Inject a game ID (test uuid) into the gamedb. use a globally unique country code to ensure
        # that only this game gets scheduled.
        game_id = FirestoreDB.add_game(
            json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH,
            hashtag=f'VIRUS.integration_test.{test_id}',
            country_code=f'US-{test_id}'
        )
        gamedb = FirestoreDB(
            json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=game_id)
        log_message(f'Running integration test for game {game_id}')

        # create an integration test subsystem log stream that specifically captures
        # game inputs and outputs at the SMS boundary.
        test_log_stream = GameIntegrationTestLogStream(
            game_id=game_id,
            test_id=test_id
        )

        # add test challenges
        for challenge in _TEST_CHALLENGES:
            gamedb.add_challenge(challenge=challenge)

        # if non-existent, create users associated with players. NOTE: critical for FE code
        # to create users when players sign up.
        for player_info in [*_EMULATED_PLAYERS, *_REAL_PLAYERS]:
            FirestoreDB.add_user(json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, name=player_info[0],
                                 tiktok=player_info[1], phone_number=player_info[2])

        # Inject players into gamedb. set the phone number of the players to a known, or emulated device.
        emulated_players = []
        for player_info in _EMULATED_PLAYERS:
            player = gamedb.player(name=player_info[0],
                                   tiktok=player_info[1], phone_number=player_info[2])
            emulated_players.append(
                EmulatedPlayer(id=player.id, name=player.name, tiktok=player.tiktok,
                               phone_number=player.phone_number, test_stream=test_log_stream, gamedb=gamedb)
            )
        for player_info in _REAL_PLAYERS:
            player = gamedb.player(name=player_info[0],
                                   tiktok=player_info[1], phone_number=player_info[2])

        # mock the scheduling method in MM service so that we can force schedule
        # after initialization.
        check_start_time_fn = mock.MagicMock()
        check_start_time_fn.return_value = False
        MatchmakerService._check_start_time = check_start_time_fn

        # create device emulator for Twilio SMS events. patch this
        # into the game engine class for the test.
        notification_emulator = FakeTwilioSMSNotifier(
            json_config_path=_TEST_TWILIO_SMS_CONFIG_PATH, game_id=game_id,
            emulated_devices=emulated_players)
        build_notifier_fn = mock.MagicMock()
        build_notifier_fn.return_value = notification_emulator
        Engine._get_sms_notifier = build_notifier_fn

        # Instantiate a local matchmaker service. make sure all services have the right configs,
        # e.g. twilio should be using the prod service phone number so that it can actually send messages.
        # set the clock mode on (2) to async so that game events happen immediately during testing.
        service = MatchmakerService(
            matchmaker=MatchMakerRoundRobin(), region=f'US-{test_id}', gamedb=gamedb, game_options=GameOptions(
                game_clock_mode=GameClockMode.ASYNC,
                game_wait_sleep_interval_sec=10,
                multi_tribe_min_tribe_size=2,
                engine_worker_thread_count=1,
                tribe_council_time_sec=10))
        try:
            service.start_matchmaker_daemon(sleep_seconds=1)
            # force schedule the game in MM (1).
            check_start_time_fn.return_value = True
            MatchmakerService._check_start_time = check_start_time_fn

            # at this point text messages should start streaming into the device(s) asynchronously.
            # respond to (6) manually, the SMS endpoint associated with the game instance phone number needs to receive requests and do the right thing with gamedb.
            # currently all user messages will receive response:
            # Sent from your Twilio trial account - Hello +{phone}, you said: {message}
            while True:
                time.sleep(5)
        finally:
            service.set_stop()
            persisted_test_logs = test_log_stream.persist()
            log_message(persisted_test_logs)
            with open(f'test_log_stream.{test_id}.json', 'w+') as f:
                f.write(persisted_test_logs)


if __name__ == '__main__':
    unittest.main()
