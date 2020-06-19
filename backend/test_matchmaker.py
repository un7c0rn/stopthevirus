import unittest
import mock
from game_engine import events
from game_engine.common import GameOptions
import uuid
import game
from contextlib import contextmanager
from game_engine.matchmaker import MatchMakerRoundRobin
from game_engine.database import Player, Team
from game_engine.firestore import FirestoreDB
from test_game import MockDatabase

import copy 

_TEST_GAME_ID = '7rPwCJaiSkxYgDocGDw1'
_TEST_PLAYER1 = Player(
    id='id/foo1',
    tiktok='tiktok/bar',
    email='email/foo',
    phone_number='sms/bar',
    active=True
)
_TEAM_SIZE = 10

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
json_config_path = _TEST_FIRESTORE_INSTANCE_JSON_PATH


class MatchMakerRoundRobinTest(unittest.TestCase):

    @staticmethod
    def generate_players():
        players=[_TEST_PLAYER1]
        for x in range(2,21):
            player = copy.deepcopy(_TEST_PLAYER1)
            player.id='id/foo' + str(x)
            players.append(player)
        return players

    def test_generate_teams(self):
        players = self.generate_players()
        options = GameOptions(target_team_size=_TEAM_SIZE)
        teams=MatchMakerRoundRobin.generate_teams(game_id=_TEST_GAME_ID, players=players, 
        team_size=_TEAM_SIZE)
        self.assertEqual(len(teams),2)

    def test_generate_teams_insufficient_players(self):
        players = [_TEST_PLAYER1]
        with self.assertRaises(Exception) as context:
            MatchMakerRoundRobin.generate_teams(game_id=_TEST_GAME_ID, players=players, 
            team_size=_TEAM_SIZE)
        self.assertTrue(context.exception)

    def test_generate_teams_tribes(self):
        gamedb = FirestoreDB(json_config_path=json_config_path, game_id=_TEST_GAME_ID)
        # gamedb = MockDatabase()
        players = self.generate_players()
        options = GameOptions(target_team_size=_TEAM_SIZE)
        data=MatchMakerRoundRobin.generate_teams_tribes(game_id=_TEST_GAME_ID, players=players, 
        game_options=options, gamedb=gamedb)
        players = data['players']
        teams = data['teams']
        tribes = data['tribes']
        for p in players:
            pass
        
        for t in tribes:
            pass

        for tm in teams:
            pass

        # print(data['tribes'])
        # print(data['teams'])
    

if __name__ == '__main__':
    unittest.main()
