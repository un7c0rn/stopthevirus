import unittest
import mock
from game_engine import matchmaker


class SimulatorTest(unittest.TestCase):

    def test_batch_update_tribe(self):
        matchmaker.GameSimulator.generate_game_environment(count_players=1000, team_size=5)
        
if __name__ == '__main__':
    unittest.main()
