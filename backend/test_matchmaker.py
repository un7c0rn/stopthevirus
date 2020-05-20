import unittest
import mock
from game_engine import events
import uuid
import game
from contextlib import contextmanager
from game_engine.matchmaker import GameSimulator, MatchMakerRoundRobin
from game_engine.database import Player, Team
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

class MatchMakerRoundRobinTest(unittest.TestCase):

    @staticmethod
    def generate_players():
        players=[_TEST_PLAYER1]
        for x in range(2,21):
            player = copy.deepcopy(_TEST_PLAYER1)
            player.id='id/foo' + str(x)
            players.append(player)
        return players

    def test_matchmaker(self):
        players = self.generate_players()
        teams=MatchMakerRoundRobin.generate_teams(game_id=_TEST_GAME_ID, players=players, 
        team_size=_TEAM_SIZE)
        self.assertEqual(len(teams),2)

    def test_matchmaker_insufficient_players(self):
        players = [_TEST_PLAYER1]
        with self.assertRaises(Exception) as context:
            MatchMakerRoundRobin.generate_teams(game_id=_TEST_GAME_ID, players=players, 
            team_size=_TEAM_SIZE)
        self.assertTrue(context.exception)
    

if __name__ == '__main__':
    unittest.main()
