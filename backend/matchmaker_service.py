import firebase_admin
from firebase_admin import credentials, firestore
from game_engine.firestore import FirestoreDB
import time
import threading

_FIRESTORE_PROD_CONF_JSON_PATH = ''
_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
json_config_path = _TEST_FIRESTORE_INSTANCE_JSON_PATH



class MatchmakerService:
    def __init__(self, json_config_path=json_config_path, region="US"):
        self._gamedb = FirestoreDB(json_config_path=json_config_path, game_id=123)
        self._region=region
        self._STOP = False
        self._daemon_started = False

    def matchmaker_function(self, sleep_seconds=60):
        print("HELLO")
        # do some logging here
        while not self._STOP:
            #games = self._gamedb.find_matchmaker_games(region=self._region)
            games = ["IM A GAME", "IM A GAME TOO"]
            if len(games) >= 1:
                print(games)
            time.sleep(sleep_seconds)
        print ("STOPPING")

    def start_matchmaker_daemon(self, sleep_seconds=60):
        if not self._daemon_started:
            thread = threading.Thread(target=self.matchmaker_function, args=(sleep_seconds,))
            self._daemon_started = True
            thread.start()
        else:
            print("CAN ONLY RUN 1 DAEMON AT A TIME")

    def set_stop(self):
        print("TRYING TO STOP")
        self._STOP = True
        self._daemon_started = False

    def set_run(self):
        self._STOP = False
        print("STOP CONDITION REMOVED")

