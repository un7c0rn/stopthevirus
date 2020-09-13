import unittest
import mock
from matchmaker_service import MatchmakerService
from game_engine.common import GameSchedule, ISODayOfWeek, STV_I18N_TABLE
from game_engine.firestore import FirestoreDB
from game_engine.matchmaker import MatchMakerRoundRobin
from game_engine.common import GameOptions, GameSchedule, GameClockMode, STV_I18N_TABLE, ISODayOfWeek, log_message

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'


def _create_game(hashtag: str) -> str:
    # TODO(brandon): ensure key fields are always populated
    # country_code "US"
    # game_has_started false
    # last_checked_date "2020-09-13"
    # max_reschedules 10
    # times_rescheduled 0
    return "0AiU57hnYjCeEUIE0yXE"


def _create_player(game_id: str, phone: str, tiktok: str) -> str:
    return "44cBCjZDHFrLM13FarHo"


class IntegrationTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_integration(self):
        # Inject a game ID (test uuid) into the gamedb.
        # TODO(brandon): this model is wrong. the matchmaker should not require a game identifier (i.e. gamedb should be None)
        print('here!')
        game_id = _create_game(hashtag='VIRUS.acceptance_test')
        print('here!')
        gamedb = FirestoreDB(
            json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=game_id)
        print('here!')

        # Instantiate a local matchmaker service. make sure all services have the right configs,
        # e.g. twilio should be using the prod service phone number so that it can actually send messages.
        # set the clock mode on (2) to async so that game events happen immediately during testing.
        service = MatchmakerService(
            matchmaker=MatchMakerRoundRobin(), gamedb=gamedb, game_options=GameOptions(game_clock_mode=GameClockMode.ASYNC))
        print('here!')
        service.start_matchmaker_daemon(sleep_seconds=1)
        print('here!')

        # Inject 10 players into gamedb with their game ID set to (2). set the phone number of the players to a known device, e.g. +17742593288.
        for _ in range(0, 10):
            _create_player(game_id=game_id,
                           phone='+17742593288', tiktok='unicorn')
        print('here!')

        # force schedule the game in MM (1).
        check_start_time_fn = mock.MagicMock()
        check_start_time_fn.return_value = True
        service._check_start_time = check_start_time_fn
        print('done!')

        # at this point text messages should start streaming into the device(s) asynchronously.
        # respond to (6) manually, the SMS endpoint associated with the game instance phone number needs to receive requests and do the right thing with gamedb.
        # currently all user messages will receive response:
        # Sent from your Twilio trial account - Hello +{phone}, you said: {message}


if __name__ == '__main__':
    unittest.main()
