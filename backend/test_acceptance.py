from game_engine.database import Database
from game_engine import database
from game_engine.common import Serializable, GameError, GameOptions
from game_engine.events import *
from game_engine.firestore import FirestoreDB
from game import Game
import enum
import attr
from abc import ABC, abstractmethod

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'


class TestError(Exception):
    pass


class FrameType(enum.Enum):
    PLAYER_START_GAME = 0
    PLAYER_JOIN_GAME = 1
    PLAYER_VOTE = 2
    PLAYER_SUBMIT_ENTRY = 3
    PLAYER_SUBMIT_NEW_CHALLENGE = 4
    PLAYER_QUIT = 5
    GAME_START_TIME = 6
    DAILY_CHALLENGE_START_TIME = 7
    DAILY_CHALLENGE_END_TIME = 8
    TRIBAL_COUNCIL_START_TIME = 9
    TRIBAL_COUNCIL_END_TIME = 10


@attr.s
class Frame(Serializable):
    type: FrameType = attr.ib()
    timestamp: int = attr.ib()


@attr.s
class GameRecording(object):
    frames: List[Frame] = attr.ib()


class Frontend(ABC):

    @abstractmethod
    def start_game(self, tiktok: Text, phone_number: Text, game_hashtag: Text):
        pass

    @abstractmethod
    def join_game(self, tiktok: Text, phone_number: Text, game_id: Text) -> None:
        pass

    @abstractmethod
    def submit_entry(self, likes: int, views: int, player_id: Text, tribe_id: Text,
                     challenge_id: Text, team_id: Text, url: Text) -> None:
        pass

    @abstractmethod
    def submit_challenge(self):
        pass


class MockFrontend(Frontend):
    def __init__(self):
        self._gamedb = None

    def start_game(self, tiktok: Text, phone_number: Text, game_hashtag: Text):
        game_id = FirestoreDB.add_game(json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH,
                                       hashtag=game_hashtag
                                       )
        self._gamedb = FirestoreDB(
            json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=game_id)
        self.join_game(
            tiktok=tiktok, phone_number=phone_number, game_id=game_id)

    def _verify_game_started(self):
        if not self._gamedb:
            raise TestError('Must call start_game to create a game_id.')

    def join_game(self, tiktok: Text, phone_number: Text, game_id: Text) -> None:
        name = tiktok
        self._verify_game_started()
        self._gamedb.player(name=name, tiktok=tiktok,
                            phone_number=phone_number)

    def submit_entry(self, likes: int, views: int, player_id: Text, tribe_id: Text,
                     challenge_id: Text, team_id: Text, url: Text) -> None:
        self._verify_game_started()
        self._gamedb.add_challenge_entry(
            database.Entry(likes=likes, views=views, player_id=player_id, tribe_id=tribe_id,
                           challenge_id=challenge_id, team_id=team_id, url=url)
        )

    def submit_challenge(self):
        self._verify_game_started()


class GameAcceptanceTest(object):
    def __init__(self):
        options = GameOptions()
        self._game = Game(game_id=str(uuid.uuid4), options=options)
        self._frontend = MockFrontend()

    def playback(self, recording: GameRecording) -> None:
        # As this test runs, text messages will be sent to users. By injecting a known
        # test phone number into a given user profile, testers can validate the user experience
        # for a given player against a known historical sequence of game actions.

        for frame in recording.frames:
            print("Simulating game frame {}".format(frame.to_json()))

            if frame.type == FrameType.PLAYER_START_GAME:
                # TODO(brandon): populate from frame
                self._frontend.start_game(
                    tiktok='',
                    phone_number='',
                    game_hashtag=''
                )

            elif frame.type == FrameType.PLAYER_JOIN_GAME:
                self._frontend.join_game(
                    tiktok='',
                    phone_number='',
                    game_id=''
                )

            elif frame.type == FrameType.PLAYER_VOTE:
                # send SMS to endpoint with voting info
                pass

            elif frame.type == FrameType.PLAYER_SUBMIT_ENTRY:
                # NOTE(brandon): behavior needs to change here. challenges
                # should be processed on the backend by a continuous job to improve
                # user experience (post-MVP).

                # TODO(brandon): populate from frame info.
                self._frontend.submit_entry(
                    likes=0,
                    views=0,
                    player_id='',
                    tribe_id='',
                    challenge_id='',
                    team_id='',
                    url=''
                )

            elif frame.type == FrameType.PLAYER_SUBMIT_NEW_CHALLENGE:
                # TODO(brandon): populate from frame info.
                self._frontend.submit_challenge()

            elif frame.type == FrameType.PLAYER_QUIT:
                # sends quit message to the SMS endpoint
                pass

            elif frame.type == FrameType.GAME_START_TIME:
                self._game.set_game_start_event()

            elif frame.type == FrameType.DAILY_CHALLENGE_START_TIME:
                self._game.set_challenge_start_event()

            elif frame.type == FrameType.DAILY_CHALLENGE_END_TIME:
                self._game.set_challenge_end_event()

            elif frame.type == FrameType.TRIBAL_COUNCIL_START_TIME:
                self._game.set_tribal_council_start_event()

            elif frame.type == FrameType.TRIBAL_COUNCIL_END_TIME:
                self._game.set_tribal_council_end_event()
