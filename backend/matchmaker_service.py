import firebase_admin
from firebase_admin import credentials, firestore
from game import Game
from game_engine.common import GameOptions, GameSchedule, STV_I18N_TABLE, ISODayOfWeek
from game_engine.firestore import FirestoreDB
from google.cloud.firestore_v1.document import DocumentSnapshot
import time
import threading
import datetime

_FIRESTORE_PROD_CONF_JSON_PATH = ''
_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
json_config_path = _TEST_FIRESTORE_INSTANCE_JSON_PATH

_test_games_data = [{
                    "count_teams":6,
                    "count_players":6,
                    "name":"test_game1",
                    "country_code":"US",
                    "game_has_started": False
                    },
                    {
                    "count_teams":6,
                    "count_players":4,
                    "name":"test_game2",
                    "country_code":"US",
                    "game_has_started": False
                    }
]


class MatchmakerService:
    def __init__(self, json_config_path=json_config_path, region="US", min_players=5, is_test=True):
        self._gamedb = FirestoreDB(json_config_path=json_config_path)
        self._min_players = min_players
        self._region=region
        self._is_test = is_test
        self._stop = threading.Event()
        self._daemon_started = False

    def start_game(self, game: Game):
        print(game)
        if self._is_test:
            #start new process
            pass
        else:
            #start on new GCP instance
            pass
        #g.play()

    def set_game_has_started(self, game: DocumentSnapshot):
        field_updates = {
            'game_has_started': True
        }
        try:
            game.reference.update(field_updates)
        except:
            print("Error setting game document game_has_started field to True")


    def matchmaker_function(self, sleep_seconds=60, is_test=False):
        print("HELLO")
        # do some logging here
        while not self._stop.is_set():
            games = self._gamedb.find_matchmaker_games(region=self._region)
            print(games)
            #games = _test_games_data
            if len(games) >= 1:
                for game in games:
                    game_dict = game.to_dict()
                    if game_dict["count_players"] >= self._min_players:
                        schedule = STV_I18N_TABLE[self._region]
                        start_day = schedule.game_start_day_of_week
                        now = datetime.datetime.now()
                        now_day = ISODayOfWeek(now.isoweekday())
                        if is_test:
                            now_day = ISODayOfWeek(5)
                        if now_day == start_day:
                            print ("Starting game")
                            options = GameOptions(game_schedule=schedule)
                            g = Game(game_id=game_dict["id"], options=options)
                            # Play the game
                            self.start_game(game=g)
                            self.set_game_has_started(game=game)
                            
            time.sleep(sleep_seconds)
        print ("STOPPING")

    def start_matchmaker_daemon(self, sleep_seconds=60):
        if not self._daemon_started and not self._stop.is_set():
            self._thread = threading.Thread(target=self.matchmaker_function, args=(sleep_seconds,True))
            self._daemon_started = True
            self._thread.start()
        else:
            print("CAN ONLY RUN 1 DAEMON AT A TIME")

    def set_stop(self):
        print("TRYING TO STOP")
        self._stop.set()
        self._thread.join() # Wait for thread to finish executing/sleeping. This may take a long time
        self._daemon_started = False

    def clear_stop(self):
        self._stop.clear()
        print("STOP CONDITION REMOVED")

