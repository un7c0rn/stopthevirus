import unittest
import mock
from matchmaker_service import MatchmakerService
import pprint
import json
import datetime
import time



class MatchmakerServiceTest(unittest.TestCase):

    def setUp(self):
        pass


    def test_matchmaker_daemon(self):
        service = MatchmakerService()
        service.start_matchmaker_daemon(sleep_seconds=1)
        #service.matchmaker_function(sleep_seconds=10)
        #time.sleep(2)
        service.set_stop()
        
        
if __name__ == '__main__':
    unittest.main()
