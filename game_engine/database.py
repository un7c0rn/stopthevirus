from abc import ABC
from typing import Text, Dict
from enum import Enum
import threading
import json
import time
import logging
import attr
import engine_lib

class DatabaseObject(object):
    # TODO(brandon): consider using SQL ORM bindings
    # for these.
    # https://docs.sqlalchemy.org/en/14/orm/tutorial.html
    def save(self):
        pass

@attr.s
class Player(DatabaseObject):
    id: Text = attr.ib()
    instagram: Text = attr.ib()
    email: Text = attr.ib()
    tribe_id: Text = attr.ib()
    team_id: Text = attr.ib()

    def is_on_team(self):
        return self.team_id is not None

@attr.s
class Team(DatabaseObject):
    id: Text = attr.ib()
    name: Text = attr.ib()

@attr.s
class Tribe(DatabaseObject):
    id: Text = attr.ib()
    name: Text = attr.ib()

@attr.s
class Challenge(DatabaseObject):
    id: Text = attr.ib()
    name: Text = attr.ib()
    message: Text = attr.ib()
    start_timestamp: int = attr.ib()
    end_timestamp: int = attr.ib()

@attr.s
class ChallengeEntry(DatabaseObject):
    id: Text = attr.ib()
    likes: int = attr.ib()
    views: int = attr.ib()
    player_id: Text = attr.ib()
    challenge_id: Text = attr.ib()
    url: Text = attr.ib()

class VotingReason(Enum):
    KICKOFF = 1
    WIN_IT_ALL = 2

@attr.s
class Vote(DatabaseObject):
    from_id: Text = attr.ib()
    to_id: Text = attr.ib()
    reason: VotingReason = attr.ib(default=VotingReason.KICKOFF)

class Database(ABC):

    def get_players(self, team: Team):
        pass
        
    def get_teams_with_size(self, tribe: Tribe, team_size: int):
        pass

    def replace_tribe(self, tribe: Tribe, new_tribe: Tribe):
        # updates tribe id for all members of tribe to new_tribe
        pass

    def get_next_challenge(self) -> Challenge:
        # select oldest challenge that has not already been played
        # mark challenge played in db
        # TODO(brandon): gamedb interface get next challenge
      return Challenge(id='1234',
        name='Karaoke',
        message='These are the challenge rules',
        start_timestamp=engine_lib.get_unix_timestamp(),
        end_timestamp=engine_lib.get_unix_timestamp() + 5)

    def create_player(self, player: Player):
        pass

    def get_player(self, id: Text) -> Player:
        pass

    def create_team(self, team: Team):
        pass

    def get_team(self, id: Text) -> Team:
        pass

    def create_tribe(self, tribe: Tribe):
        pass

    def get_tribe(self, id: Text) -> Tribe:
        pass

    def create_challenge(self, challenge: Challenge):
        pass

    def get_challenge(self, id: Text) -> Challenge:
        pass

    def create_vote(self, vote: Vote):
        pass

    def get_vote(self, id: Text) -> Vote:
        pass