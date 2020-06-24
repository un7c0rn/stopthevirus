import firebase_admin
from firebase_admin import credentials, firestore
from game import Game
from game_engine.common import GameOptions, GameSchedule, STV_I18N_TABLE, ISODayOfWeek
from game_engine.database import Database
from game_engine.engine import Engine
from game_engine.firestore import FirestoreDB
from game_engine.matchmaker import MatchMakerInterface
from test_game import MockDatabase, MockPlayEngine
from google.cloud.firestore_v1.document import DocumentSnapshot
import time
import threading
import datetime
from game_engine import events
from multiprocessing import Process
import multiprocessing

_FIRESTORE_PROD_CONF_JSON_PATH = ''
_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
json_config_path = _TEST_FIRESTORE_INSTANCE_JSON_PATH
_AMAZON_SQS_PROD_CONF_JSON_PATH = '../amazon/stopthevirus.fifo.json'
_TEST_AMAZON_SQS_CONFIG_PATH = '../amazon/stopthevirus.fifo.json'
_TEST_TWILIO_SMS_CONFIG_PATH = '../twilio/stv-twilio.json'



class MatchmakerService:
    # Handles scheduling and communication with other services for starting games
    # TDOO(David): Add function to run all games that are supposed to be running at start(in MVP/test)
    def __init__(self, matchmaker: MatchMakerInterface, gamedb: Database, json_config_path=json_config_path, region="US", min_players=5, is_mvp=True):
        self._matchmaker = matchmaker
        self._gamedb = gamedb
        self._min_players = min_players
        self._region = region
        self._is_mvp = is_mvp
        self._stop = threading.Event()
        self._daemon_started = False

    def play_game(self, game: Game, players:list, is_test=True):
        print("playing a game")

        if is_test:
            database = MockDatabase()
            engine = MockPlayEngine().CreateEngine(database)
        else:
            database = FirestoreDB(json_config_path=json_config_path, game_id=game._game_id)#db needs to have correct game_id
            engine = Engine(options=game._options,
                            game_id=game._game_id,
                            sqs_config_path=_TEST_AMAZON_SQS_CONFIG_PATH,
                            twilio_config_path=_TEST_TWILIO_SMS_CONFIG_PATH,
                            gamedb=database
            )

        game_data = self._matchmaker.generate_teams_tribes(game_id=game._game_id, players=players, game_options=game._options, gamedb=database)
        tribes = game_data['tribes']
        print("TRIBES")
        print(tribes)
        # TODO notify users that game started 
        game.play(tribe1=tribes[0],
                tribe2=tribes[1],
                gamedb=database,
                engine=engine)


    def start_game(self, game: Game, players:list):
        if self._is_mvp:
            #start new process
            p = multiprocessing.Process(target=self.play_game, args=(game, players))
            p.start()
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
    
    def reschedule_game(self, game: DocumentSnapshot):
        print("RESCHEDULING GAME")

        game_dict = game.to_dict()
        
        now_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        print(now_date)

        if now_date != game_dict.get("last_checked_date"):
            if (game_dict.get("times_rescheduled") if game_dict.get("times_rescheduled") else 0) < game_dict.get("max_reschedules"):
                # Reschedule the game by setting current UTC date to last_checked_date. 
                # Server will then not check the game until following week
                # Assume times_rescheduled is optional and max_reschedules is True
                times_rescheduled = game_dict["times_rescheduled"] + 1 if game_dict.get("times_rescheduled") else 1
                field_updates = {
                    'last_checked_date': now_date,
                    'times_rescheduled': times_rescheduled
                }
                try:
                    game.reference.update(field_updates)
                    print("I RESCHEDULED THE GAME!")
                except:
                    print("Error rescheduling game")
            else:
                # Cancel the game
                field_updates = {
                    'to_be_deleted': True,
                }
                try:
                    game.reference.update(field_updates)
                    print("Cancelled the game (set to_be_deleted flag)")
                except:
                    print("Error cancelling game")
                pass





    def matchmaker_function(self, sleep_seconds=60, is_test=False):
        print("HELLO")
        # do some logging here
        while not self._stop.is_set():
            games = self._gamedb.find_matchmaker_games(region=self._region)
            if len(games) >= 1:
                for game in games:
                    game_dict = game.to_dict()
                    print(game_dict)
                    players_stream = game.reference.collection("players").stream()
                    players_list = []
                    for player in players_stream:
                        players_list.append(player)

                    schedule = STV_I18N_TABLE[self._region]
                    start_day = schedule.game_start_day_of_week
                    now = datetime.datetime.utcnow()
                    now_day = ISODayOfWeek(now.isoweekday())

                    now_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
                    if is_test:
                        now_day = ISODayOfWeek(5)
                    if now_day == start_day and now_date != game_dict.get("last_checked_date"): #TODO: Do these checks in query
                        if game_dict["count_players"] >= self._min_players:
                            print ("Starting game")
                            print(game_dict)
                            options = GameOptions(game_schedule=schedule, game_wait_sleep_interval_sec=1 if is_test else 30,
                            single_tribe_council_time_sec=1 if is_test else 300,# is there a way to get the default values from GameOptions?
                            single_team_council_time_sec=1 if is_test else 300,
                            final_tribal_council_time_sec=1 if is_test else 300,
                            multi_tribe_council_time_sec=1 if is_test else 300)
                            g = Game(game_id=game_dict["id"], options=options)
                            # Play the game
                            self.start_game(game=g, players=players_list)
                            #self.set_game_has_started(game=game)
                        else:
                            # Reschedule the game
                            print ("Rescheduling/cancelling game")
                            self.reschedule_game(game=game)
                                               
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

