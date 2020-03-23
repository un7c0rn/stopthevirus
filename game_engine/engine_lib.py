from abc import ABC
from typing import Text, Dict
from enum import Enum
import threading
import json
import time
import logging

def get_unix_timestamp():
    return time.time()

# abstraction layer here in case we need remote logging.
def log_message(message):
    logging.info(message)

class EventType(Enum):
    NOP = 0
    NEW_PLAYER = 1
    CHALLENGE_CREATED = 2
    VOTE_TO_KICK_OFF = 3
    VOTE_TO_WIN = 4
    CHALLENGE_ENTRY_SUBMISSION = 5
    NEW_TEAM_ASSIGNMENT = 6
    NEW_CHALLENGE_ANNOUNCEMENT = 7
    VOTED_OUT_NOTIFICATION = 8
    TRIBAL_COUNCIL_ANNOUNCEMENT = 9

class GameState(Enum):
    IDLE = 0
    ENROLLMENT = 1
    TRIBAL_CHALLENGE = 2
    TRIBAL_COUNCIL = 3
    SCORING_ENTRIES = 4
    FINALE = 5

class GameDB(ABC):
    def __init__(self, host: Text=None, config_dict: Dict=None):
        pass

    def count_active_players(self):
        pass

    def next_challenge(self):
        pass

class Logger(ABC):
    def print(self, message):
        pass

class EventQueue(ABC):

    def __init__(self, config_dict: Dict=None):
        return 

    def get(self) -> [Event, None]:
        # TODO(brandon): connect to AWS SQS
        return None

class NotificationService(ABC):
    def __init__(self):
        self._inputq = EventQueue()

class GameConfig(object):

    @property
    def min_player_count(self):
        return 10

    @property
    def final_player_count(self):
        return 2
    