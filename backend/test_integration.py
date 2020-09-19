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

_SAVE_TEST_LOGS = True
_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
_TEST_TWILIO_SMS_CONFIG_PATH = '../twilio/stv-twilio-service-test.json'
_TEST_GAME_HASHTAG = '#NikeFit2020'
_TEST_SLEEP_INTERVAL = 3
_TEST_CHALLENGES = [
    Challenge(
        name='Fastest 10K bike time. Bonus points for the view :)', message='NOP'
    ),
    Challenge(
        name='Creative 1 mile run with friends.', message='NOP'
    ),
    Challenge(
        name='Make an at home jump rope video!', message='NOP'
    ),
    Challenge(
        name='Make video and tell us why cardio is important to you.', message='NOP'
    ),
    Challenge(
        name='Stand on a parked car and sing your favorite running song.', message='NOP'
    ),
    Challenge(
        name='Post a selfie in your new Nike running shoes.', message='NOP'
    ),
    Challenge(
        name='Most creative breathable home made mask for COVID-19.', message='NOP'
    ),
    Challenge(
        name='Crunches! How many can you do?', message='NOP'
    ),
    Challenge(
        name='Team push ups! Make a video doing pushups with a friend.', message='NOP'
    ),
    Challenge(
        name='Waterproof video swim. Post your water workout from the beach or pool.', message='NOP'
    ),
    Challenge(
        name='Make a video and tell us what being fit means to you.', message='NOP'
    ),
    Challenge(
        name='Make a video about your goals while sprinting at full speed.', message='NOP'
    ),
    Challenge(
        name='Shadow box! Make a video shadow boxing with a friend.', message='NOP'
    ),
    Challenge(
        name='Post highlights from your best 2 mile run time today.', message='NOP'
    ),
    Challenge(
        name='Find a Nike store with a purple pair of sneakers.', message='NOP'
    ),
    Challenge(
        name='Post your best, and safest, Just Do It video!', message='NOP'
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
            hashtag=_TEST_GAME_HASHTAG,
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
        save_check_start_time_fn = MatchmakerService._check_start_time
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
                game_wait_sleep_interval_sec=_TEST_SLEEP_INTERVAL,
                multi_tribe_min_tribe_size=2,
                engine_worker_thread_count=5,
                tribe_council_time_sec=_TEST_SLEEP_INTERVAL))
        # mock the MM Twilio client
        service._get_sms_notifier = mock.MagicMock(return_value=notification_emulator)
        try:
            service.start_matchmaker_daemon(sleep_seconds=1)
            # force schedule the game in MM (1).
            check_start_time_fn.return_value = True
            MatchmakerService._check_start_time = check_start_time_fn
            while gamedb.game_from_id(game_id).count_players > 1:
                time.sleep(_TEST_SLEEP_INTERVAL)
        finally:
            MatchmakerService._check_start_time = save_check_start_time_fn
            service.set_stop()
            test_dict = test_log_stream.to_dict()
            if _SAVE_TEST_LOGS:
                persisted_test_logs = test_log_stream.persist()
                log_message(persisted_test_logs)
                with open(f'game_logs/stream.{test_id}.json', 'w+') as f:
                    f.write(persisted_test_logs)
            active_players = list()
            for player in gamedb.stream_players(active_player_predicate_value=True):
                active_players.append(player)
            winner = active_players[0]
            found_winner_message = False
            for output in test_dict['outputs']:
                if 'You are the last survivor and WINNER' in output['message'] and output['name'] == winner.name:
                    found_winner_message = True
            self.assertTrue(found_winner_message)


if __name__ == '__main__':
    unittest.main()
