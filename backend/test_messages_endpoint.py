import unittest
import mock
from parameterized import parameterized

# NOTE(brandon): due to GCP functions build architecture, we can't import the same Firestore
# module for both the GCP long running app and the serverless function. rather than spending
# time on an abstraction, a subset of DB logic was replicated into the function module.
from functions.sms.main import _FirestoreDB
from functions.sms import main as sms_function
from game_engine.firestore import FirestoreDB

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
_TEST_GAME_ID = '7rPwCJaiSkxYgDocGDw1'
_TEST_BOSTON_ROB_PLAYER_ID = '2ZPmDfX9q82KY5PVf1LH'
_TEST_TEAM_YELLOW_ID = 'Q09FeEtoIgjNI57Bnl1E'

_functions_gamedb = _FirestoreDB(
    json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=_TEST_GAME_ID)
_verify_gamedb = FirestoreDB(
    json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=_TEST_GAME_ID)

_TEST_DATA_JSON = """
{
   "users":{
       "2ZPmDfX9q82KY5PVf1LH":{
           "game_id":"7rPwCJaiSkxYgDocGDw1",
           "phone_number":"+15551234567"
       }
   },
   "games":{
      "7rPwCJaiSkxYgDocGDw1":{
         "count_teams":6,
         "count_players":2,
         "name":"test_game1"
      }
   },
   "games/7rPwCJaiSkxYgDocGDw1/players":{
      "2ZPmDfX9q82KY5PVf1LH":{
         "team_id":"Q09FeEtoIgjNI57Bnl1E",
         "active":true,
         "name":"Boston Rob",
         "tribe_id":"cbTgYdPh97K6rRTDdEPL",
         "phone_number":"+15551234567"
      }
   },
   "games/7rPwCJaiSkxYgDocGDw1/players/2ZPmDfX9q82KY5PVf1LH/ballots":{
       "W3PGNjMzWwsce7MXD46f":{
            "challenge_id":"bar",
            "options":{
                "A":1,
                "B":2,
                "C":3
            },
            "is_for_win": false,
            "timestamp":1e12
       }
   }
}
"""


class SMSEndpointTest(unittest.TestCase):

    def setUp(self):
        _functions_gamedb.import_collections(_TEST_DATA_JSON)

    def test_deactivate_player(self):
        player = _verify_gamedb.player_from_id(_TEST_BOSTON_ROB_PLAYER_ID)
        tribe = _verify_gamedb.tribe_from_id(player.tribe_id)
        team = _verify_gamedb.team_from_id(player.team_id)
        game_player_count = _verify_gamedb.count_players()
        tribe_player_count = _verify_gamedb.count_players(from_tribe=tribe)
        team_player_count = _verify_gamedb.count_players(from_team=team)
        _functions_gamedb.deactivate_player(
            _functions_gamedb.player_from_id(_TEST_BOSTON_ROB_PLAYER_ID))
        self.assertFalse(_verify_gamedb.player_from_id(
            _TEST_BOSTON_ROB_PLAYER_ID).active)
        self.assertEqual(_verify_gamedb.count_players(), game_player_count - 1)
        self.assertEqual(_verify_gamedb.count_players(
            from_tribe=tribe), tribe_player_count - 1)
        self.assertEqual(_verify_gamedb.count_players(
            from_team=team), team_player_count - 1)

    def test_find_ballot(self):
        self.assertEqual(
            {'A': 1, 'B': 2, 'C': 3},
            _functions_gamedb.find_ballot(
                player_id=_TEST_BOSTON_ROB_PLAYER_ID).get('options'))

    def test_find_player(self):
        self.assertEqual(_functions_gamedb.find_player(
            phone_number='+15551234567').get('name'), "Boston Rob")

    def test_player_from_id(self):
        self.assertEqual(
            _functions_gamedb.player_from_id(
                id=_TEST_BOSTON_ROB_PLAYER_ID).get('name'),
            'Boston Rob')

    def test_vote(self):
        _verify_gamedb.clear_votes()
        _functions_gamedb.vote(from_player_id=_TEST_BOSTON_ROB_PLAYER_ID,
                               to_player_id=_TEST_BOSTON_ROB_PLAYER_ID)
        vote_counts = _verify_gamedb.count_votes(
            from_team=_verify_gamedb.team_from_id(_TEST_TEAM_YELLOW_ID))
        self.assertEqual(
            vote_counts[_TEST_BOSTON_ROB_PLAYER_ID], 1
        )

    @parameterized.expand([
        ('A'),
        ('A '),
        (' A'),
        ('  A'),
        ('   A'),
    ])
    def test_normalize_vote_option(self, option_string):
        self.assertEqual(
            sms_function._normalize_vote_option(option_string), 'A')

    @parameterized.expand([
        ('a', True),
        ('b', True),
        ('c', True),
        ('d', True),
        ('A', True),
        ('B', True),
        ('C', True),
        ('D', True),
        ('A A', False),
        ('XXXX', False),
    ])
    def test_is_valid_vote_option(self, option_string, is_valid):
        self.assertEqual(
            sms_function._is_valid_vote_option(option_string), is_valid
        )

    @parameterized.expand([
        ('stop', True),
        ('quit', True),
        ('STOP', True),
        ('QUIT', True),
        ('XXXX', False)
    ])
    def test_is_quit_message(self, message, is_quit_message):
        self.assertEqual(
            sms_function._is_quit_message(message), is_quit_message
        )

    @parameterized.expand([
        ('+15551234567', 'A', '.+Your vote has been cast. Thanks!.+'),
        ('+1XXXX', 'A', '.+You\'re not in this game.+'),
        ('+15551234567', 'XXXX', '.+not a valid message.+'),
        ('+15551234567', 'QUIT', '.+You have left the game. Thanks for playing!.+'),
    ])
    def test_sms_http(self, from_phone_number, message, response_pattern):
        def fn(x):
            if x == 'From':
                return from_phone_number
            elif x == 'Body':
                return message
        request = mock.MagicMock()
        request.form.get = fn
        self.assertRegex(
            sms_function.sms_http(request),
            response_pattern
        )

    def test_game_id_from_phone_number(self):
        phone_number = '+15555555555'
        _verify_gamedb.add_user(json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, name='foo', tiktok='bar',
                                phone_number=phone_number, game_id=_TEST_GAME_ID)
        self.assertEqual(
            _functions_gamedb.game_id_from_phone_number(
                phone_number=phone_number),
            _TEST_GAME_ID
        )


if __name__ == '__main__':
    unittest.main()
