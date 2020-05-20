import unittest
import mock
from game_engine import events
import uuid
import game
from contextlib import contextmanager
from game_engine.matchmaker import GameSimulator
from game_engine.database import Player, Team

class MatchMakerRoundRobinTest(unittest.TestCase):

    def test_matchmaker(self):
        self.assertEqual(1,2)

if __name__ == '__main__':
    unittest.main()
