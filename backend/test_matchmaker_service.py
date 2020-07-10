import unittest
import mock
from matchmaker_service import MatchmakerService
from game_engine.common import STV_I18N_TABLE
from game_engine.firestore import FirestoreDB
from game_engine.matchmaker import MatchMakerRoundRobin
from test_game import MockDatabase
import pprint
import json
import datetime
import time

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
_TEST_GAME_ID = '7rPwCJaiSkxYgDocGDw1'

_gamedb = FirestoreDB(
    json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=_TEST_GAME_ID)

json_config_path = _TEST_FIRESTORE_INSTANCE_JSON_PATH

_TEST_DATA_MATCHMAKER_JSON = """
{
   "games":{
      "7rPwCJaiSkxYgDocGDw1":{
         "count_teams":6,
         "count_players":8,
         "name":"test_game1",
         "country_code":"US",
         "game_has_started": false,
         "last_checked_date": "",
         "to_be_deleted": false,
         "times_rescheduled": 0
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


    def test_matchmaker_daemon_happy(self, use_mock=False):
        # Test happy path
        if use_mock:
            gamedb = MockDatabase()
        else:
            gamedb = FirestoreDB(json_config_path=json_config_path)
        service = MatchmakerService(matchmaker=MatchMakerRoundRobin(), gamedb=gamedb)
        service.start_matchmaker_daemon(sleep_seconds=1)
        time.sleep(2)
        service.set_stop()
        service.clear_stop()

    def test_matchmaker_daemon_reschedule(self, use_mock=False):
        if use_mock:
            gamedb = MockDatabase()
        else:
            gamedb = FirestoreDB(json_config_path=json_config_path)
            
        service = MatchmakerService(matchmaker=MatchMakerRoundRobin(), gamedb=gamedb, min_players=9000)
        service.start_matchmaker_daemon(sleep_seconds=1)
        time.sleep(2)
        service.set_stop()
        service.clear_stop()

    def test_check_start_time(self):
        gamedb = FirestoreDB(json_config_path=json_config_path)
        service = MatchmakerService(matchmaker=MatchMakerRoundRobin(), gamedb=gamedb, min_players=9000)
        schedule = STV_I18N_TABLE['US']

        # Case 1: before start_time
        
        service._check_start_time(schedule=schedule, now_dt_with_tz=datetime.datetime.now(tz=schedule.game_time_zone))

        # Case 2: Within 24 hours after start_time

        # Case 3: 24 hours or more after start_time




        
        
if __name__ == '__main__':
    unittest.main()
