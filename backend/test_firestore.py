import unittest
import mock
from game_engine.firestore import FirestoreDB
import pprint
import json
import datetime

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
_TEST_TRIBE_TIGRAWAY_ID = '77TMV9omdLeW7ORvuheX'
_TEST_TRIBE_SIDAMA_ID = 'cbTgYdPh97K6rRTDdEPL'
_TEST_GAME_ID = '7rPwCJaiSkxYgDocGDw1'
_TEST_TEAM_BLUE_ID = 'GQnxhYXnV86oJXLklbGB'
_TEST_TEAM_YELLOW_ID = 'Q09FeEtoIgjNI57Bnl1E'
_TEST_CHALLENGE_KARAOKE_ID = 'PTifdegtPAtUAgxtNoBK'
_TEST_CHALLENGE_KARAOKE_URL = 'https://www.youtube.com/watch?v=irVIUvDTTB0'
_TEST_YELLOW_TEAM_ACTIVE_PLAYER_ID = '2ZPmDfX9q82KY5PVf1LH'
_TEST_BOSTON_ROB_PLAYER_ID = '2ZPmDfX9q82KY5PVf1LH'
_TEST_COLLECTION_PATHS = ['games', 'games/7rPwCJaiSkxYgDocGDw1/players', 'games/7rPwCJaiSkxYgDocGDw1/teams',
                          'games/7rPwCJaiSkxYgDocGDw1/tribes', 'games/7rPwCJaiSkxYgDocGDw1/votes']

_gamedb = FirestoreDB(
    json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=_TEST_GAME_ID)


_TEST_DATA_JSON = """
{
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
         "tribe_id":"cbTgYdPh97K6rRTDdEPL"
      },
      "LXHpnrUA65FS25wGfJ00":{
         "active":true,
         "name":"Amber Brkich",
         "tribe_id":"cbTgYdPh97K6rRTDdEPL",
         "team_id":"Q09FeEtoIgjNI57Bnl1E"
      }
   },
   "games/7rPwCJaiSkxYgDocGDw1/teams":{
      "GQnxhYXnV86oJXLklbGB":{
         "count_players":0,
         "name":"BLUE",
         "tribe_id":"77TMV9omdLeW7ORvuheX",
         "size":0,
         "active":true
      },
      "Q09FeEtoIgjNI57Bnl1E":{
         "active":true,
         "count_players":2,
         "name":"YELLOW",
         "tribe_id":"cbTgYdPh97K6rRTDdEPL",
         "size":2
      },
      "Zpuv2bEn4WykPpIyNuJ5":{
         "count_players":0,
         "name":"GREEN",
         "tribe_id":"77TMV9omdLeW7ORvuheX",
         "size":0,
         "active":true
      },
      "hRt3wVz6ZtVEOhkeNlIn":{
         "count_players":0,
         "name":"RED",
         "tribe_id":"77TMV9omdLeW7ORvuheX",
         "size":0,
         "active":true
      }
   },
   "games/7rPwCJaiSkxYgDocGDw1/tribes":{
      "77TMV9omdLeW7ORvuheX":{
         "count_players":0,
         "name":"TIGRAWAY",
         "count_teams":4
      },
      "cbTgYdPh97K6rRTDdEPL":{
         "count_teams":1,
         "count_players":2,
         "name":"SIDAMA"
      }
   },
   "games/7rPwCJaiSkxYgDocGDw1/votes":{
      "AcuR476MF1O0tvI3bH8u":{
         "is_for_win":false,
         "team_id":"Q09FeEtoIgjNI57Bnl1E",
         "to_id":"2ZPmDfX9q82KY5PVf1LH",
         "from_id":"LXHpnrUA65FS25wGfJ00"
      },
      "G8u6obWxyHhXMD9cLuE0":{
         "team_id":"Q09FeEtoIgjNI57Bnl1E",
         "to_id":"2ZPmDfX9q82KY5PVf1LH",
         "from_id":"LXHpnrUA65FS25wGfJ00",
         "is_for_win":false
      },
      "K1umHRQpEorC9O2kdlRi":{
         "team_id":"Q09FeEtoIgjNI57Bnl1E",
         "to_id":"2ZPmDfX9q82KY5PVf1LH",
         "from_id":"LXHpnrUA65FS25wGfJ00",
         "is_for_win":false
      },
      "VnD8joQqsyBBFTYkkP56":{
         "from_id":"LXHpnrUA65FS25wGfJ00",
         "is_for_win":false,
         "team_id":"Q09FeEtoIgjNI57Bnl1E",
         "to_id":"2ZPmDfX9q82KY5PVf1LH"
      },
      "ptPg1MWPtKIHiElLKiLU":{
         "team_id":"Q09FeEtoIgjNI57Bnl1E",
         "to_id":"2ZPmDfX9q82KY5PVf1LH",
         "from_id":"LXHpnrUA65FS25wGfJ00",
         "is_for_win":false
      }
   },
   "games/7rPwCJaiSkxYgDocGDw1/challenges":{
      "PTifdegtPAtUAgxtNoBK":{
         "name" : "KARAOKE",
         "complete" : false
      },
      "caqZjCq6rREzqImUBFmV":{
         "name" : "MOST CREATIVE HOME CLEAN",
         "complete" : false
      }
   },
   "games/7rPwCJaiSkxYgDocGDw1/entries":{
      "Eajg3iXhalMbb42BktcG":{
         "likes" : 10,
         "views" : 10,
         "player_id" : "2ZPmDfX9q82KY5PVf1LH",
         "tribe_id" : "77TMV9omdLeW7ORvuheX",
         "challenge_id" : "PTifdegtPAtUAgxtNoBK",
         "team_id" : "GQnxhYXnV86oJXLklbGB",
         "url" : "https://www.youtube.com/watch?v=irVIUvDTTB0"
      }
   }
}
"""

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


class FirestoreDBTest(unittest.TestCase):

    def setUp(self):
        _gamedb.import_collections(_TEST_DATA_JSON)

    def test_batch_update_tribe(self):
        sidama_tribe = _gamedb.tribe_from_id(_TEST_TRIBE_SIDAMA_ID)
        tigraway_tribe = _gamedb.tribe_from_id(_TEST_TRIBE_TIGRAWAY_ID)
        sidama_player_count = _gamedb.count_players(from_tribe=sidama_tribe)
        sidama_team_count = _gamedb.count_teams(from_tribe=sidama_tribe)
        tigraway_player_count = _gamedb.count_players(
            from_tribe=tigraway_tribe)
        tigraway_team_count = _gamedb.count_teams(
            from_tribe=tigraway_tribe)
        _gamedb.batch_update_tribe(
            from_tribe=sidama_tribe, to_tribe=tigraway_tribe)
        self.assertEqual(_gamedb.count_players(from_tribe=sidama_tribe), 0)
        self.assertEqual(_gamedb.count_teams(from_tribe=sidama_tribe), 0)
        self.assertEqual(_gamedb.count_players(
            from_tribe=tigraway_tribe), sidama_player_count + tigraway_player_count)
        self.assertEqual(_gamedb.count_teams(
            from_tribe=tigraway_tribe), sidama_team_count + tigraway_team_count)
        self.assertListEqual(
            [team.name for team in _gamedb.stream_teams(from_tribe=sidama_tribe)], [])
        self.assertListEqual([team.name for team in _gamedb.stream_teams(from_tribe=tigraway_tribe)], [
            'BLUE', 'GREEN', 'RED', 'YELLOW'
        ])

    def test_stream_teams(self):
        teams = _gamedb.stream_teams(
            from_tribe=_gamedb.tribe_from_id(_TEST_TRIBE_TIGRAWAY_ID))
        self.assertListEqual([team.name for team in teams], [
                             'BLUE', 'GREEN', 'RED'])

    def test_stream_entries(self):
        entries = _gamedb.stream_entries(from_tribe=_gamedb.tribe_from_id(_TEST_TRIBE_TIGRAWAY_ID),
                                         from_team=_gamedb.team_from_id(
            _TEST_TEAM_BLUE_ID),
            from_challenge=_gamedb.challenge_from_id(_TEST_CHALLENGE_KARAOKE_ID))
        self.assertListEqual([entry.url for entry in entries], [
                             _TEST_CHALLENGE_KARAOKE_URL])

    def test_count_players(self):
        self.assertEqual(_gamedb.count_players(from_tribe=_gamedb.tribe_from_id(
            _TEST_TRIBE_SIDAMA_ID)), 2)

        self.assertEqual(_gamedb.count_players(
            from_team=_gamedb.team_from_id(_TEST_TEAM_YELLOW_ID)), 2)

    def test_count_teams(self):
        self.assertEqual(_gamedb.count_teams(from_tribe=_gamedb.tribe_from_id(
            _TEST_TRIBE_TIGRAWAY_ID)), 4)

        self.assertEqual(_gamedb.count_teams(), 6)

    def test_count_votes(self):
        votes = _gamedb.count_votes(from_team=_gamedb.team_from_id(
            _TEST_TEAM_YELLOW_ID), is_for_win=False)
        self.assertDictEqual(votes, {
            _TEST_YELLOW_TEAM_ACTIVE_PLAYER_ID: 5
        })

        votes = _gamedb.count_votes(is_for_win=True)
        self.assertDictEqual(votes, {})

    def test_list_challenges(self):
        challenges = _gamedb.list_challenges(
            challenge_completed_predicate_value=False)
        self.assertListEqual([challenge.name for challenge in challenges], [
            'KARAOKE',
            'MOST CREATIVE HOME CLEAN'
        ])

        challenges = _gamedb.list_challenges(
            challenge_completed_predicate_value=True)
        self.assertListEqual([challenge.name for challenge in challenges], [])

    def test_list_players(self):
        players = _gamedb.list_players(
            from_team=_gamedb.team_from_id(_TEST_TEAM_YELLOW_ID))
        self.assertListEqual([player.name for player in players], [
            'Boston Rob',
            'Amber Brkich'
        ])

        players = _gamedb.list_players(from_team=_gamedb.team_from_id(_TEST_TEAM_YELLOW_ID),
                                       active_player_predicate_value=False)
        self.assertListEqual([player.name for player in players], [])

    def test_list_teams(self):
        teams = _gamedb.list_teams()
        self.assertListEqual([team.name for team in teams], [
            'BLUE', 'YELLOW', 'GREEN', 'RED'
        ])

        players = _gamedb.list_players(from_team=_gamedb.team_from_id(_TEST_TEAM_YELLOW_ID),
                                       active_player_predicate_value=False)
        self.assertListEqual([player.name for player in players], [])

    def test_player_from_id(self):
        self.assertEqual(_gamedb.player_from_id(
            _TEST_BOSTON_ROB_PLAYER_ID).name, 'Boston Rob')

    def test_team_from_id(self):
        self.assertEqual(_gamedb.team_from_id(_TEST_TEAM_BLUE_ID).name, 'BLUE')

    def test_tribe_from_id(self):
        self.assertEqual(_gamedb.tribe_from_id(
            _TEST_TRIBE_TIGRAWAY_ID).name, 'TIGRAWAY')

    def test_challenge_from_id(self):
        self.assertEqual(_gamedb.challenge_from_id(
            _TEST_CHALLENGE_KARAOKE_ID).name, 'KARAOKE')

    def test_deactivate_player(self):
        player = _gamedb.player_from_id(_TEST_BOSTON_ROB_PLAYER_ID)
        tribe = _gamedb.tribe_from_id(player.tribe_id)
        team = _gamedb.team_from_id(player.team_id)
        game_player_count = _gamedb.count_players()
        tribe_player_count = _gamedb.count_players(from_tribe=tribe)
        team_player_count = _gamedb.count_players(from_team=team)
        _gamedb.deactivate_player(player)
        self.assertFalse(_gamedb.player_from_id(
            _TEST_BOSTON_ROB_PLAYER_ID).active)
        self.assertEqual(_gamedb.count_players(), game_player_count - 1)
        self.assertEqual(_gamedb.count_players(
            from_tribe=tribe), tribe_player_count - 1)
        self.assertEqual(_gamedb.count_players(
            from_team=team), team_player_count - 1)

    def test_deactivate_team(self):
        team = _gamedb.team_from_id(_TEST_TEAM_BLUE_ID)
        tribe = _gamedb.tribe_from_id(team.tribe_id)
        game_team_count = _gamedb.count_teams()
        tribe_team_count = _gamedb.count_teams(from_tribe=tribe)
        _gamedb.deactivate_team(team)
        self.assertFalse(_gamedb.team_from_id(_TEST_TEAM_BLUE_ID).active)
        self.assertEqual(_gamedb.count_teams(), game_team_count - 1)
        self.assertEqual(_gamedb.count_teams(
            from_tribe=tribe), tribe_team_count - 1)

    def test_save_player(self):
        player = _gamedb.player_from_id(_TEST_BOSTON_ROB_PLAYER_ID)
        player.name = 'Asap Ferg'
        self.assertEqual(_gamedb.player_from_id(
            _TEST_BOSTON_ROB_PLAYER_ID).name, 'Boston Rob')
        _gamedb.save(player)
        self.assertEqual(_gamedb.player_from_id(
            _TEST_BOSTON_ROB_PLAYER_ID).name, 'Asap Ferg')

    def test_save_team(self):
        team = _gamedb.team_from_id(_TEST_TEAM_BLUE_ID)
        team.name = 'AQUA'
        self.assertEqual(_gamedb.team_from_id(
            _TEST_TEAM_BLUE_ID).name, 'BLUE')
        _gamedb.save(team)
        self.assertEqual(_gamedb.team_from_id(
            _TEST_TEAM_BLUE_ID).name, 'AQUA')

    def test_tribe(self):
        tribe = _gamedb.tribe(name='name/foo')
        try:
            self.assertEqual(_gamedb.tribe_from_id(
                tribe.id).name, 'name/foo')
            self.assertIsNotNone(tribe.id)
        finally:
            _gamedb._client.document(
                "games/{}/tribes/{}".format(_gamedb._game_id, tribe.id)).delete()

    def test_player(self):
        game_player_count = _gamedb.count_players()
        player = _gamedb.player(name='name/foo')
        try:
            self.assertEqual(_gamedb.player_from_id(
                player.id).name, 'name/foo')
            self.assertEqual(_gamedb.count_players(), game_player_count + 1)
            self.assertIsNotNone(player.id)
        finally:
            _gamedb._client.document(
                "games/{}/players/{}".format(_gamedb._game_id, player.id)).delete()

    def test_clear_votes(self):
        _gamedb.clear_votes()
        self.assertEqual(_gamedb.count_votes(), {})

    def test_find_matchmaker_games(self):
        _gamedb.import_collections(_TEST_DATA_MATCHMAKER_JSON)
        games = _gamedb.find_matchmaker_games(region="US")
        self.assertEqual(len(games), 1)

        # EU game has already started
        games = _gamedb.find_matchmaker_games(region="EU")
        self.assertEqual(len(games), 0)
        
        
if __name__ == '__main__':
    unittest.main()
