import unittest
import mock
from unittest.mock import patch
from matchmaker_service import MatchmakerService
from game_engine.common import GameSchedule, ISODayOfWeek, STV_I18N_TABLE
from game_engine.firestore import FirestoreDB
from game_engine.matchmaker import MatchMakerRoundRobin
from test_game import MockDatabase
import pprint
import json
import datetime
import time
import pytz

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


@patch.object(MatchmakerService, '_set_game_has_started', return_value=None)
@patch.object(MatchmakerService, '_play_game', return_value=None)
@patch.object(MatchmakerService, '_reschedule_or_cancel_game', return_value=None)
class MatchmakerServiceTest(unittest.TestCase):

    def setUp(self):
        _gamedb.import_collections(_TEST_DATA_MATCHMAKER_JSON)
        pass

    def test_matchmaker_daemon_happy(self, use_mock=False, *_):
        # Test happy path
        if use_mock:
            gamedb = MockDatabase()
        else:
            gamedb = FirestoreDB(json_config_path=json_config_path)
        service = MatchmakerService(
            matchmaker=MatchMakerRoundRobin(), gamedb=gamedb)
        service.start_matchmaker_daemon(sleep_seconds=1, is_test=True)
        time.sleep(2)
        service.set_stop()
        service.clear_stop()

    def test_matchmaker_daemon_reschedule(self, use_mock=False, *_):
        if use_mock:
            gamedb = MockDatabase()
        else:
            gamedb = FirestoreDB(json_config_path=json_config_path)

        service = MatchmakerService(
            matchmaker=MatchMakerRoundRobin(), gamedb=gamedb, min_players=9000)
        service.start_matchmaker_daemon(sleep_seconds=1, is_test=True)
        time.sleep(2)
        service.set_stop()
        service.clear_stop()

    def test_check_start_time(self, *_):
        gamedb = FirestoreDB(json_config_path=json_config_path)
        service = MatchmakerService(
            matchmaker=MatchMakerRoundRobin(), gamedb=gamedb, min_players=9000)

        mock_schedule = GameSchedule(
            country='United States',
            country_code='US',
            game_time_zone=pytz.timezone('America/New_York'),
            game_start_day_of_week=ISODayOfWeek.Friday,
            game_start_time=datetime.time(hour=12),
            daily_challenge_start_time=datetime.time(hour=12),
            daily_challenge_end_time=datetime.time(hour=18),
            daily_tribal_council_start_time=datetime.time(hour=19),
            daily_tribal_council_end_time=datetime.time(hour=21),
        )

        # Case 1: before start_time
        mock_time = datetime.datetime(
            year=2020, month=7, day=10, hour=mock_schedule.game_start_time.hour-1)
        result = service._check_start_time(
            schedule=mock_schedule, now_dt_with_tz=mock_schedule.game_time_zone.localize(mock_time))
        self.assertEqual(result, False)

        # Case 1.5: after start_time, but on a previous day

        mock_time = datetime.datetime(
            year=2020, month=7, day=9, hour=mock_schedule.game_start_time.hour)
        result = service._check_start_time(
            schedule=mock_schedule, now_dt_with_tz=mock_schedule.game_time_zone.localize(mock_time))
        self.assertEqual(result, False)

        # Case 2: On same day as start_day and after start_time
        mock_time = datetime.datetime(
            year=2020, month=7, day=10, hour=mock_schedule.game_start_time.hour+5)
        result = service._check_start_time(
            schedule=mock_schedule, now_dt_with_tz=mock_schedule.game_time_zone.localize(mock_time))
        self.assertEqual(result, True)

        # Case 2.5: On same day as start_day and after start_time, but in different timezone
        mock_time = datetime.datetime(
            year=2020, month=7, day=10, hour=mock_schedule.game_start_time.hour+5)
        result = service._check_start_time(schedule=mock_schedule, now_dt_with_tz=pytz.timezone(
            "Asia/Tokyo").localize(mock_time))
        self.assertEqual(result, False)

        # Case 3: Day following start_day and after start_time
        mock_time = datetime.datetime(
            year=2020, month=7, day=11, hour=mock_schedule.game_start_time.hour)
        result = service._check_start_time(
            schedule=mock_schedule, now_dt_with_tz=mock_schedule.game_time_zone.localize(mock_time))
        self.assertEqual(result, False)

        mock_time = datetime.datetime(
            year=2020, month=7, day=13, hour=mock_schedule.game_start_time.hour)
        result = service._check_start_time(
            schedule=mock_schedule, now_dt_with_tz=mock_schedule.game_time_zone.localize(mock_time))
        self.assertEqual(result, False)

        # Case 4: 1 Week after, on the right time/date
        mock_time = datetime.datetime(
            year=2020, month=7, day=17, hour=mock_schedule.game_start_time.hour)
        result = service._check_start_time(
            schedule=mock_schedule, now_dt_with_tz=mock_schedule.game_time_zone.localize(mock_time))
        self.assertEqual(result, True)


if __name__ == '__main__':
    unittest.main()
