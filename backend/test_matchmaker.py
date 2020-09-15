import unittest
import mock
from game_engine import events
from game_engine.common import GameOptions
import uuid
import game
from contextlib import contextmanager
from game_engine.matchmaker import MatchMakerRoundRobin
from game_engine.database import Player, Team, Game
from game_engine.firestore import FirestoreDB
from test_game import MockDatabase

import copy

_TEST_GAME_ID = '7rPwCJaiSkxYgDocGDw1'
_TEST_PLAYER1 = Player(
    id=str(uuid.uuid4()),
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
    def generate_players(gamedb: MockDatabase = None):
        players = [_TEST_PLAYER1]
        for x in range(2, 21):
            player = copy.deepcopy(_TEST_PLAYER1)
            player.id = str(uuid.uuid4())
            players.append(player)
        if gamedb:
            for player in players:
                gamedb._players[player.id] = player
        return players

    def test_generate_teams(self):
        players = self.generate_players()
        teams = MatchMakerRoundRobin.generate_teams(game_id=_TEST_GAME_ID, players=players,
                                                    team_size=_TEAM_SIZE)
        self.assertEqual(len(teams), 2)

    def test_generate_teams_insufficient_players(self):
        players = [_TEST_PLAYER1]
        with self.assertRaises(Exception) as context:
            MatchMakerRoundRobin.generate_teams(game_id=_TEST_GAME_ID, players=players,
                                                team_size=_TEAM_SIZE)
        self.assertTrue(context.exception)

    def test_generate_tribes(self):
        gamedb = MockDatabase()
        gamedb._games[_TEST_GAME_ID] = Game()
        players = self.generate_players(gamedb=gamedb)
        options = GameOptions(target_team_size=_TEAM_SIZE)
        data = MatchMakerRoundRobin.generate_tribes(game_id=_TEST_GAME_ID, players=players,
                                                    game_options=options, gamedb=gamedb)

        players = data['players']
        teams = data['teams']
        tribes = data['tribes']

        self.assertEqual(len(players), 20)
        self.assertEqual(len(teams), 2)
        self.assertEqual(len(tribes), 2)


if __name__ == '__main__':
    unittest.main()
