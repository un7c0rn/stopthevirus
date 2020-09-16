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
from parameterized import parameterized

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


_gamedb = FirestoreDB(
    json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH)


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

    @mock.patch.object(FirestoreDB, 'find_user', return_value=mock.MagicMock())
    def test_generate_teams(self, _):
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
        gamedb.find_user = mock.MagicMock(return_value=mock.MagicMock())
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

    @parameterized.expand([
        (MatchMakerRoundRobin, 10, GameOptions(
            target_team_size=5), 2, 2, 10, 1, 5, 5),
        (MatchMakerRoundRobin, 20, GameOptions(
            target_team_size=5), 2, 4, 20, 2, 10, 5),
        (MatchMakerRoundRobin, 100, GameOptions(
            target_team_size=10), 2, 10, 100, 5, 50, 10),
    ])
    def test_generate_tribes_count_initialization(self, algorithm_type,
                                                  number_of_joined_players,
                                                  game_options,
                                                  expected_game_count_tribes,
                                                  expected_game_count_teams,
                                                  expected_game_count_players,
                                                  expected_tribe_count_teams,
                                                  expected_tribe_count_players,
                                                  expected_team_count_players):
        # create a game
        game_id = FirestoreDB.add_game(
            json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, hashtag='hashtag/foo')
        _gamedb._game_id = game_id

        # generate mock players with an id attribute and add the players to the game
        players = list()
        for i in range(0, number_of_joined_players):
            name = 'name/foo'
            tiktok = 'tiktok/bar'
            phone_number = f'+1000000000{i}'
            player = _gamedb.player(
                name=name, tiktok=tiktok, phone_number=phone_number)
            FirestoreDB.add_user(json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH,
                                 name=name, tiktok=tiktok, phone_number=phone_number)
            players.append(player)

        # read counts for game, all tribes, all teams and verify that they are correct
        game_info_dict = algorithm_type.generate_tribes(
            game_id=game_id,
            players=players,
            game_options=game_options,
            gamedb=_gamedb
        )

        game = _gamedb.game_from_id(game_id)
        self.assertEqual(game.count_tribes, expected_game_count_tribes)
        self.assertEqual(game.count_teams, expected_game_count_teams)
        self.assertEqual(game.count_players, expected_game_count_players)

        for tribe in game_info_dict['tribes']:
            tribe_ref = _gamedb.tribe_from_id(
                tribe.id)
            self.assertEqual(tribe_ref.count_teams, expected_tribe_count_teams)
            self.assertEqual(tribe_ref.count_players,
                             expected_tribe_count_players)
        for team in game_info_dict['teams']:
            self.assertEqual(_gamedb.team_from_id(
                team.id).count_players, expected_team_count_players)


if __name__ == '__main__':
    unittest.main()
