import firebase_admin
from firebase_admin import credentials, firestore
from game import Game
from game_engine.common import GameOptions
from game_engine.firestore import FirestoreDB
import time
import threading

_FIRESTORE_PROD_CONF_JSON_PATH = ''
_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
json_config_path = _TEST_FIRESTORE_INSTANCE_JSON_PATH



class MatchmakerService:
    def __init__(self, json_config_path=json_config_path, region="US", min_players=5, is_test=True):
        self._gamedb = FirestoreDB(json_config_path=json_config_path)
        self._min_players = min_players
        self._region=region
        self._is_test = is_test
        self._STOP = False
        self._daemon_started = False

    def matchmaker_function(self, sleep_seconds=60):
        print("HELLO")
        # do some logging here
        while not self._STOP:
            #games = self._gamedb.find_matchmaker_games(region=self._region)
            games = [{"id":"IM A GAME", "count_players":6}, {"id":"IM A GAME TOO", "count_players":4}]
            if len(games) >= 1:
                print(games)
                for game in games:
                    print(game)
                    if game["count_players"] >= self._min_players:
                        options = GameOptions()
                        g = Game(game_id=game["id"],options=options)
                        if self._is_test:
                            #start new process
                            pass
                        else:
                            #start on new GCP instance
                            pass
                        #g.play()
                        # Play the game
            time.sleep(sleep_seconds)
        print ("STOPPING")

    def start_matchmaker_daemon(self, sleep_seconds=60):
        if not self._daemon_started and not self._STOP:
            self._thread = threading.Thread(target=self.matchmaker_function, args=(sleep_seconds,))
            self._daemon_started = True
            self._thread.start()
        else:
            print("CAN ONLY RUN 1 DAEMON AT A TIME")

    def set_stop(self):
        print("TRYING TO STOP")
        self._STOP = True
        self._thread.join() # Wait for thread to finish executing/sleeping. This may take a long time
        self._daemon_started = False

    def set_run(self):
        self._STOP = False
        print("STOP CONDITION REMOVED")

