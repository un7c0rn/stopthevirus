import firebase_admin
from firebase_admin import credentials, firestore
from game import Game
from game_engine import messages
from game_engine.common import GameOptions, GameSchedule, STV_I18N_TABLE, ISODayOfWeek, log_message
from game_engine.database import Database
from game_engine.engine import Engine
from game_engine.firestore import FirestoreDB
from game_engine.matchmaker import MatchMakerInterface
from game_engine.matchmaker import MatchMakerError
from game_engine.twilio import TwilioSMSNotifier
from game_engine.twilio import SMSNotifier
from test_game import MockDatabase, MockPlayEngine
from google.cloud.firestore_v1.document import DocumentSnapshot
from typing import Text
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
_TEST_TWILIO_SMS_CONFIG_PATH = '../twilio/stv-twilio-service-test.json'


def _twilio_client(game_id: Text) -> TwilioSMSNotifier:
    return TwilioSMSNotifier(
        json_config_path=_TEST_TWILIO_SMS_CONFIG_PATH,
        game_id=game_id)


class MatchmakerService:
    # Handles scheduling and communication with other services for starting games
    # TDOO(David): Add function to run all games that are supposed to be running at start(in MVP/test)
    def __init__(self, matchmaker: MatchMakerInterface, gamedb: Database, json_config_path: str = json_config_path,
                 region: str = "US", min_players: int = 5, is_mvp: bool = True, game_options: GameOptions = None):
        self._matchmaker = matchmaker
        self._gamedb = gamedb
        self._min_players = min_players
        self._region = region
        self._is_mvp = is_mvp
        self._stop = threading.Event()
        self._daemon_started = False
        self._game_options = game_options

    def _get_sms_notifier(self, game_id: str) -> SMSNotifier:
        return _twilio_client(game_id=game_id)

    def _notify_players(self, game_id: Text, players: list, message: Text):
        twilio = self._get_sms_notifier(game_id=game_id)
        
        # iterate over players and get their phone numbers
        recipient_phone_numbers = list(
            map(lambda player: player.to_dict().get("phone_number"), players))
        # filter out players with no phone number
        filtered_phone_numbers = list(
            filter(lambda number: not not number, recipient_phone_numbers))

        twilio.send_bulk_sms(
            message=message,
            recipient_addresses=filtered_phone_numbers
        )
        log_message(message="Notified players with message:{}".format(
            message), game_id=game_id)

    def _play_game(self, game: Game, game_snap: DocumentSnapshot, players: list, game_dict: dict, is_test: bool = False):
        log_message("Starting a game", game_id=game_dict.get(
            "id"), additional_tags=game_dict)

        if is_test:
            database = MockDatabase()
            engine = MockPlayEngine().CreateEngine(database)
        else:
            # NOTE(brandon): the game DB instance used by the matchmaker is for searching over all games. when we create
            # a game instance, we also supply new game DB and engine objects that have the specific game ID.
            database = FirestoreDB(
                json_config_path=json_config_path, game_id=game._game_id)
            engine = Engine(options=game._options,
                            game_id=game._game_id,
                            sqs_config_path=_TEST_AMAZON_SQS_CONFIG_PATH,
                            twilio_config_path=_TEST_TWILIO_SMS_CONFIG_PATH,
                            gamedb=database
                            )
        try:
            game_data = self._matchmaker.generate_tribes(
                game_id=game._game_id, players=players, game_options=game._options, gamedb=database)
            tribes = game_data['tribes']
            message = messages.NOTIFY_GAME_STARTED_EVENT_MSG_FMT.format(
                header=messages.game_sms_header(
                    hashtag=game_dict.get('hashtag')),
                game=game_dict.get('hashtag')
            )
            self._notify_players(game_id=game._game_id,
                                 players=players, message=message)
            if self._is_mvp:
                # NOTE(brandon): changing to thread for now. can't pickle non-primitive engine object.
                game_thread = threading.Thread(target=game.play, args=(
                    tribes[0], tribes[1], database, engine))
                game_thread.start()
            else:
                # start on new GCP instance
                pass
        except MatchMakerError as e:
            # Catches error from matchmaker algorithm
            message = "Matchmaker Error: {}".format(e)
            log_message(message=message,
                        game_id=game._game_id)
            self._set_game_has_started(
                game_snap=game_snap, game=game, value=False)
            self._notify_players(game_id=game._game_id,
                                 players=players, message=message)
            self._reschedule_or_cancel_game(
                game_snap=game_snap, game_dict=game_dict, players=players)

    def _start_game(self, game: Game, game_snap: DocumentSnapshot, players: list, game_dict: dict, is_test: bool = False):
        self._set_game_has_started(game_snap=game_snap, game=game)
        self._play_game(game=game, game_snap=game_snap,
                        players=players, game_dict=game_dict, is_test=is_test)

    def _set_game_has_started(self, game_snap: DocumentSnapshot, game: Game, value: bool = True):
        field_updates = {
            'game_has_started': value
        }
        try:
            game_snap.reference.update(field_updates)
            log_message(message="Set game_has_started field to {}".format(
                value), game_id=game._game_id)
        except Exception as e:
            log_message(message="Error setting game document game_has_started field to {}: {}".format(
                value, e), game_id=game._game_id)
            raise RuntimeError(str(e))

    def _reschedule_or_cancel_game(self, game_snap: DocumentSnapshot, game_dict: dict, players: list):
        log_message(message="Rescheduling or cancelling game",
                    game_id=game_dict.get("id"))

        now_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        if 'times_rescheduled' not in game_dict:
            game_dict['times_rescheduled'] = 0
        if 'max_reschedules' not in game_dict:
            game_dict['max_reschedules'] = 1

        if (game_dict.get("times_rescheduled") if game_dict.get("times_rescheduled") else 0) < game_dict.get("max_reschedules"):
            # Reschedule the game by setting current UTC date to last_checked_date.
            # Server will then not check the game until following week
            # Assume times_rescheduled is optional and max_reschedules is True
            times_rescheduled = game_dict["times_rescheduled"] + \
                1 if game_dict.get("times_rescheduled") else 1
            field_updates = {
                'last_checked_date': now_date,
                'times_rescheduled': times_rescheduled
            }
            try:
                game_snap.reference.update(field_updates)
                log_message(message="Game successfully rescheduled",
                            game_id=game_dict.get("id"))

                schedule = STV_I18N_TABLE[self._region]
                notif_message = messages.NOTIFY_GAME_RESCHEDULED_EVENT_MSG_FMT.format(
                    header=messages.game_sms_header(
                        hashtag=game_dict.get('hashtag')),
                    game=game_dict.get("hashtag"),
                    reason="insufficient players",
                    date=schedule.nextweek_localized_string,
                    time=schedule.localized_time_string(
                        schedule.daily_challenge_start_time
                    )
                )
                self._notify_players(game_id=game_dict.get(
                    "id"), players=players, message=notif_message)
            except Exception as e:
                log_message(message="Error rescheduling game: {}".format(
                    e), game_id=game_dict.get("id"))
        else:
            self._cancel_game(game_snap=game_snap, players=players)

    def _cancel_game(self, game_snap: DocumentSnapshot, players: list, reason: str = "insufficient players") -> None:
        # Cancel the game
        game_dict = game_snap.to_dict()
        field_updates = {
            'to_be_deleted': True,
        }
        game_snap.reference.update(field_updates)
        log_message(
            message="Cancelled the game (set to_be_deleted flag)", game_id=game_dict.get("id"))
        notif_message = messages.NOTIFY_GAME_CANCELLED_EVENT_MSG_FMT.format(
            header=messages.game_sms_header(hashtag=game_dict.get('hashtag')),
            game=game_dict.get("hashtag"),
            reason=reason
        )
        self._notify_players(game_id=game_dict.get(
            "id"), players=players, message=notif_message)

    def _check_start_time(self, schedule: GameSchedule,
                          now_dt_with_tz: datetime.datetime,
                          is_test: bool = False):
        start_day = schedule.game_start_day_of_week.value
        start_time = schedule.game_start_time

        localized_time = now_dt_with_tz.astimezone(schedule.game_time_zone)
        now_day = localized_time.isoweekday()
        now_time = localized_time.time()

        if is_test:
            now_day = start_day
            now_time = start_time

        return now_day == start_day and now_time >= start_time

    def _matchmaker_function(self, sleep_seconds: int = 60, is_test: bool = False):
        log_message("Starting matchmaker for region={}".format(self._region))
        while not self._stop.is_set():
            games = self._gamedb.find_matchmaker_games(region=self._region)
            if len(games) >= 1:
                for game_snap in games:
                    game_dict = game_snap.to_dict()
                    players_stream = game_snap.reference.collection(
                        "players").stream()
                    players_list = []
                    for player in players_stream:
                        players_list.append(player)

                    if self._region in STV_I18N_TABLE:
                        schedule = STV_I18N_TABLE[self._region]
                    else:
                        schedule = STV_I18N_TABLE['US']

                    try:
                        now_utc = datetime.datetime.utcnow().strftime('%Y-%m-%d')
                        if self._check_start_time(schedule=schedule, now_dt_with_tz=datetime.datetime.now().astimezone(),
                                                  is_test=is_test) and now_utc != game_dict.get("last_checked_date"):  # TODO: Do these checks in query

                            if game_dict["count_players"] >= self._min_players:
                                if self._game_options is None:
                                    self._game_options = GameOptions(
                                        game_schedule=schedule, game_wait_sleep_interval_sec=1 if is_test else 30)
                                g = Game(
                                    game_id=game_dict["id"], options=self._game_options)
                                self._start_game(
                                    game=g, game_snap=game_snap, players=players_list, game_dict=game_dict, is_test=is_test)
                            else:
                                self._reschedule_or_cancel_game(
                                    game_snap=game_snap, game_dict=game_dict, players=players_list)
                    except Exception as e:
                        log_message(
                            f"Game {str(game_dict)} is corrupt: {str(e)} Cancelling.")
                        self._cancel_game(game_snap=game_snap, players=players_list,
                                          reason="an internal data corruption error")

            time.sleep(sleep_seconds)
        log_message("Stopped matchmaker for region={}".format(self._region))

    def start_matchmaker_daemon(self, sleep_seconds: int = 60, is_test: bool = False):
        if not self._daemon_started and not self._stop.is_set():
            self._thread = threading.Thread(
                target=self._matchmaker_function, args=(sleep_seconds, is_test))
            self._daemon_started = True
            self._thread.start()
        else:
            log_message(
                "Failed to start new matchmaker for region={} (matchmaker already running)".format(self._region))

    def set_stop(self):
        log_message(
            "Received stop signal for matchmaker in region={}".format(self._region))
        self._stop.set()
        # Wait for thread to finish executing/sleeping. This may take a long time
        self._thread.join()
        self._daemon_started = False

    def clear_stop(self):
        self._stop.clear()
        log_message(
            "Cleared stop signal for matchmaker in region={}".format(self._region))
