from game_engine.database import Database
from game_engine import database
from game_engine.common import Serializable, GameError, GameOptions
from game_engine.events import *
from game_engine.firestore import FirestoreDB
import enum
import attr

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'


class TestError(Exception):
    pass


class InputType(enum.Enum):
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
class GameInput(Serializable):
    type: InputType = attr.ib()
    timestamp: int = attr.ib()


@attr.s
class GameRecording(object):
    inputs: List[GameInput] = attr.ib()


class NetlifyMock(object):
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
    def playback(self, recording: GameRecording) -> None:
        for input in recording.inputs:
            print("Simulating game input {}".format(input.to_json()))

            if input.type == InputType.PLAYER_START_GAME:
                # netlify DB write
                # direct DB write, adds new game and new player to DB
                # player is owner
                pass

            elif input.type == InputType.PLAYER_JOIN_GAME:
                # netlify DB write
                # direct DB write, adds new player and associates with game ID
                pass

            elif input.type == InputType.PLAYER_VOTE:
                # send SMS to endpoint with voting info
                pass

            elif input.type == InputType.PLAYER_SUBMIT_ENTRY:
                # netlify DB write
                # NOTE(brandon): behavior needs to change here. challenges
                # should be processed on the backend by a continuous job.
                pass

            elif input.type == InputType.PLAYER_SUBMIT_NEW_CHALLENGE:
                # netlify DB write
                pass

            elif input.type == InputType.PLAYER_QUIT:
                # sends quit message to the SMS endpoint
                pass

            elif input.type == InputType.GAME_START_TIME:
                # match maker generates teams using algo
                # game object is instantiated with tribes and game starts
                pass

            elif input.type == InputType.DAILY_CHALLENGE_START_TIME:
                # TODO(brandon) override game tribal council wait by setting process event
                pass

            elif input.type == InputType.DAILY_CHALLENGE_END_TIME:
                # TODO(brandon) override
                pass

            elif input.type == InputType.TRIBAL_COUNCIL_START_TIME:
                # TODO(brandon) override
                pass

            elif input.type == InputType.TRIBAL_COUNCIL_END_TIME:
                # TODO(brandon) override
                pass
