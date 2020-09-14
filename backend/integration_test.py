import unittest
import mock
from matchmaker_service import MatchmakerService
from game_engine.common import GameSchedule, ISODayOfWeek, STV_I18N_TABLE
from game_engine.firestore import FirestoreDB
from game_engine.matchmaker import MatchMakerRoundRobin
from game_engine.database import Challenge
from game_engine.common import GameOptions, GameSchedule, GameClockMode, STV_I18N_TABLE, ISODayOfWeek, log_message
import time
import uuid
from game_engine.common import log_message

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'

_TEST_CHALLENGES = [
    Challenge(
        name='Most creative mask challenge!', message='This challenge is simple. NOP!'
    ),
    Challenge(
        name='Most creative mask challenge!', message='This challenge is simple. NOP!'
    ),
]

_TEST_PLAYERS = [
    # name, tiktok, phone_number
    ('player 0', 'unicorn', '+17742593288'),
    ('player 1', 'bixia', '+16172220773'),
    ('player 2', 'bixia', '+16172220773'),
    ('player 3', 'bixia', '+16172220773'),
    ('player 4', 'bixia', '+16172220773'),
]


class IntegrationTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_integration(self):
        seed = str(uuid.uuid4())
        # Inject a game ID (test uuid) into the gamedb. use a globally unique country code to ensure
        # that only this game gets scheduled.
        game_id = FirestoreDB.add_game(
            json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH,
            hashtag=f'VIRUS.integration_test.{seed}',
            country_code=f'US-{seed}'
        )
        gamedb = FirestoreDB(
            json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=game_id)
        log_message(f'Running integration test for game {game_id}')

        # add test challenges
        for challenge in _TEST_CHALLENGES:
            gamedb.add_challenge(challenge=challenge)

        # mock the scheduling method in MM service so that we can force schedule
        # after initialization.
        check_start_time_fn = mock.MagicMock()
        check_start_time_fn.return_value = False
        MatchmakerService._check_start_time = check_start_time_fn

        # Instantiate a local matchmaker service. make sure all services have the right configs,
        # e.g. twilio should be using the prod service phone number so that it can actually send messages.
        # set the clock mode on (2) to async so that game events happen immediately during testing.
        service = MatchmakerService(
            matchmaker=MatchMakerRoundRobin(), region=f'US-{seed}', gamedb=gamedb, game_options=GameOptions(game_clock_mode=GameClockMode.ASYNC, game_wait_sleep_interval_sec=30, multi_tribe_min_tribe_size=2))
        try:
            service.start_matchmaker_daemon(sleep_seconds=1)

            # Inject 10 players into gamedb with their game ID set to (2). set the phone number of the players to a known device, e.g. +17742593288.
            for player in _TEST_PLAYERS:
                # NOTE(brandon): this is the hard part. the system is dynamic so these phone numbers need to
                # respond to inbound messages at test time in order to simulate winner/loser selection and
                # ballots. players need to enter tiktok links and vote or the system doesn't work.
                gamedb.player(name=player[0],
                              tiktok=player[1], phone_number=player[2])

            # force schedule the game in MM (1).
            check_start_time_fn.return_value = True
            MatchmakerService._check_start_time = check_start_time_fn

            # at this point text messages should start streaming into the device(s) asynchronously.
            # respond to (6) manually, the SMS endpoint associated with the game instance phone number needs to receive requests and do the right thing with gamedb.
            # currently all user messages will receive response:
            # Sent from your Twilio trial account - Hello +{phone}, you said: {message}
            time.sleep(120)
        finally:
            service.set_stop()


if __name__ == '__main__':
    unittest.main()
