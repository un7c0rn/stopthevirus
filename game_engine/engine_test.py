import unittest
import mock
from engine import GameEngine
from engine_lib import Logger

class GameEngineTestCase(unittest.TestCase):
    def setUp(self):
        self._engine = GameEngine()

    @mock.patch.object(Logger, 'print')
    def test_log_message(self, print_fn):
        self._engine._log_message("test message")
        print_fn.assert_called_with("test message")
