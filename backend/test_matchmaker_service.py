import unittest
import mock
from matchmaker_service import MatchmakerService
from game_engine.firestore import FirestoreDB
from game_engine.matchmaker import MatchMakerRoundRobin
import pprint
import json
import datetime
import time

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
_TEST_GAME_ID = '7rPwCJaiSkxYgDocGDw1'

_gamedb = FirestoreDB(
    json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=_TEST_GAME_ID)

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
json_config_path = _TEST_FIRESTORE_INSTANCE_JSON_PATH

_TEST_DATA_MATCHMAKER_JSON = """
{
   "games":{
      "7rPwCJaiSkxYgDocGDw1":{
         "count_teams":6,
         "count_players":8,
         "name":"test_game1",
         "country_code":"US",
         "game_has_started": false
      },
      "FFFFFFFFFFFFFFFFFFFF":{
         "count_teams":6,
         "count_players":5,
         "name":"test_game2",
         "country_code":"EU",
         "game_has_started": true
      }
   }
}
"""
class MatchmakerServiceTest(unittest.TestCase):

    def setUp(self):
        _gamedb.import_collections(_TEST_DATA_MATCHMAKER_JSON)
        pass


    def test_matchmaker_daemon(self):
        gamedb = FirestoreDB(json_config_path=json_config_path)
        service = MatchmakerService(matchmaker=MatchMakerRoundRobin(), gamedb=gamedb)
        service.start_matchmaker_daemon(sleep_seconds=1)
        time.sleep(2)
        service.set_stop()
        service.clear_stop()

        
        
if __name__ == '__main__':
    unittest.main()
