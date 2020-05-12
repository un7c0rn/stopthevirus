from game_engine.database import Database
from game_engine import database
from game_engine.common import Serializable, GameError, GameOptions
from game_engine.events import *
from game_engine.firestore import FirestoreDB
from game import Game
import enum
import attr
from abc import ABC, abstractmethod
from typing import Text
from game_engine import database
import uuid
import names
import random
import math
from queue import Queue
import json

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
_VIR_US_FE_HOSTNAME = 'https://localhost:3000'
_VIR_US_BE_CALLBACK_HOSTNAME = 'https://localhost:3001'
_DEFAULT_TRIBE_NAMES = [
    "JUDAH",
    "ISSACHAR",
    "ZEBULUN",
    "REUBEN",
    "SIMEON",
    "GAD",
    "EPHRAIM",
    "MANESSEH",
    "BENJAMIN",
    "DAN",
    "ASHER",
    "NAPHTALI"
]


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
    from_phone_number: Text = attr.ib(default='')
    tiktok: Text = attr.ib(default='')
    player_id: Text = attr.ib(default='')
    game_id: Text = attr.ib(default='')
    game_hashtag: Text = attr.ib(default='')
    challenge_message: Text = attr.ib(default='')
    challenge_name: Text = attr.ib(default='')
    sms_message_content: Text = attr.ib(default='')
    is_vote_to_win: bool = attr.ib(default=False)
    tiktok_video_metadata: dict = attr.ib(factory=dict)


@attr.s
class GameRecording(object):
    frames: List[Frame] = attr.ib()

    @classmethod
    def random_phone_number(cls):
        n = '0000000000'
        while '9' in n[3:6] or n[3:6] == '000' or n[6] == n[7] == n[8] == n[9]:
            n = str(random.randint(10**9, 10**10-1))
        return n[:3] + '-' + n[3:6] + '-' + n[6:]

    @classmethod
    def create_players(cls, count_players: int) -> List[Player]:
        players = []

        for _ in range(count_players):
            name = names.get_first_name().lower()
            player = database.Player(
                id=str(uuid.uuid4()),
                tiktok=name,
                email="{}@hostname.com".format(name),
                phone_number=GameRecording.random_phone_number()
            )
            players.append(player)

    @classmethod
    def generate_randomized(cls, count_players: int, count_challenges: int) -> object:
        recording = GameRecording()
        players = GameRecording.create_players(count_players=count_players)
        game_id = str(uuid.uuid4())

        # (1) one player does start game frame
        game_initiator = players[random.randint(0, count_players)]
        recording.frames.append(
            Frame(type=FrameType.PLAYER_START_GAME,
                  from_phone_number=game_initiator.phone_number,
                  tiktok=game_initiator.tiktok)
        )

        # (2) one player does submit new challenge frame (xN)
        for _ in range(count_challenges):
            recording.frames.append(
                Frame(type=FrameType.PLAYER_SUBMIT_NEW_CHALLENGE,
                      player_id=game_initiator.id,
                      challenge_name="challenge/test/name/{}".format(
                          str(uuid.uuid4())),
                      challenge_message="challenge/test/message/{}".format(
                          str(uuid.uuid4())))
            )

        # (3) all other players do join game frame
        for player in players:
            if player.id == game_initiator.id:
                continue
            else:
                recording.frames.append(
                    Frame(type=FrameType.PLAYER_JOIN_GAME,
                          tiktok=player.tiktok,
                          phone_number=player.phone_number,
                          game_id=game_id
                          )
                )

        # (4) game start event
        recording.frames.append(
            Frame(type=FrameType.GAME_START_TIME,
                  game_id=game_id)
        )
        # (5) daily challenge start
        # (6) all active players submit entry
        # (7) daily challenge end
        # (8) tribal council start
        # (9) all active losing players vote, vote is random team member, vote is not self
        # (10) tribal council end
        # (11) repeat (5-10) until 2 finalists
        # (12) all players (active and deactivated) vote for winner
        # (13) winner announced


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


class SMSEndpoint(ABC):

    @abstractmethod
    def send_sms_message(self, from_phone_number: Text, content: Text) -> None:
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

    def submit_challenge(self, from_player_id: Text, challenge_name: Text, challenge_message: Text) -> None:
        self._verify_game_started()


class MockSMSEndpoint(SMSEndpoint):

    def send_sms_message(self, from_phone_number: Text, content: Text) -> None:
        pass


class GameAcceptanceTest(object):
    def __init__(self):
        options = GameOptions()
        self._game = Game(game_id=str(uuid.uuid4), options=options)
        self._frontend = MockFrontend()
        self._sms_endpoint = MockSMSEndpoint()

    def playback(self, recording: GameRecording) -> None:
        # As this test runs, text messages will be sent to users. By injecting a known
        # test phone number into a given user profile, testers can validate the user experience
        # for a given player against a known historical sequence of game actions.

        for frame in recording.frames:
            print("Simulating game frame {}".format(frame.to_json()))

            if frame.type == FrameType.PLAYER_START_GAME:
                self._frontend.start_game(
                    tiktok=frame.tiktok,
                    phone_number=frame.phone_number,
                    game_hashtag=frame.game_hashtag
                )

            elif frame.type == FrameType.PLAYER_JOIN_GAME:
                self._frontend.join_game(
                    tiktok=frame.tiktok,
                    phone_number=frame.phone_number,
                    game_id=frame.game_id
                )

            elif frame.type == FrameType.PLAYER_VOTE:
                self._sms_endpoint.send_sms_message(
                    from_phone_number=frame.from_phone_number,
                    content=frame.sms_message_content)

            elif frame.type == FrameType.PLAYER_SUBMIT_ENTRY:
                self._frontend.submit_entry(
                    likes=frame.tiktok_video_metadata['likes'],
                    views=frame.tiktok_video_metadata['views'],
                    url=frame.tiktok_video_metadata['url'],
                    player_id=frame.player_id,
                    tribe_id=frame.tribe_id,
                    challenge_id=frame.tribe_id,
                    team_id=frame.team_id,
                )

            elif frame.type == FrameType.PLAYER_SUBMIT_NEW_CHALLENGE:
                self._frontend.submit_challenge(
                    from_player_id=frame.player_id,
                    challenge_name=frame.challenge_name,
                    challenge_message=frame.challenge_message)

            elif frame.type == FrameType.PLAYER_QUIT:
                self._sms_endpoint.send_sms_message(
                    from_phone_number=frame.from_phone_number,
                    content=frame.sms_message_content)

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
