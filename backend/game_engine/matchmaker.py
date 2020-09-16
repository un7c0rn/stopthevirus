from game_engine import database
from game_engine.common import GameOptions
from game_engine.database import Player, Team
from game_engine.firestore import FirestoreTribe
from google.cloud.firestore_v1.document import DocumentReference, DocumentSnapshot
from game_engine.database import Database

import uuid
import names
import random
import math
from queue import Queue
import json
from abc import ABC, abstractmethod
from typing import List

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


class MatchMakerError(Exception):
    pass


class MatchMaker(object):

    def generate_game_invite_link(self, game_id: str) -> str:
        return "{}/join-game/{}".format(_VIR_US_FE_HOSTNAME, game_id)

    def generate_start_game_verification_link(self, game_id: str, game_starter_user_id: str) -> str:
        return "{}?game_id={}&game_starter_user_id={}&verify=start_game".format(_VIR_US_BE_CALLBACK_HOSTNAME, game_id, game_starter_user_id)

    def generate_join_game_verification_link(self, game_id: str, player_id: str) -> str:
        return "{}?game_id={}&player_id={}&verify=join_game".format(_VIR_US_BE_CALLBACK_HOSTNAME, game_id, player_id)

    def generate_game_info_link(self, game_id: str) -> str:
        return "{}/game-info/{}".format(_VIR_US_FE_HOSTNAME, game_id)


class MatchMakerInterface(ABC):

    @classmethod
    @abstractmethod
    def generate_teams(cls, game_id: str, players: list, team_size: int) -> dict:
        # Take in game_id and list of Players and return a list of Teams
        return

    @classmethod
    @abstractmethod
    def generate_tribes(cls, game_id: str, players: list, game_options: GameOptions) -> dict:
        # Take in game_id, list of Players, and gameOptions, and return a list of Teams and Tribes
        return


class MatchMakerRoundRobin(MatchMakerInterface):

    @classmethod
    def generate_teams(cls, game_id: str, players: list, team_size: int) -> dict:
        teams = []
        count_players = len(players)
        if count_players < team_size:
            raise MatchMakerError("Insufficient players for given team size")
        for n in range(0, math.floor(count_players / team_size)):
            team = database.Team(
                id=str(uuid.uuid4()),
                name="team/{}".format(n),
            )
            teams.append(team)

        count_teams = len(teams)
        for n, player in enumerate(players):
            team = teams[n % count_teams]
            player.team_id = team.id
            team.count_players += 1

        teams_dict = {}
        for team in teams:
            teams_dict[team.id] = team.to_dict()
            del teams_dict[team.id]['id']
        return teams_dict

    @classmethod
    def generate_tribes(cls, game_id: str, players: List[DocumentSnapshot], game_options: GameOptions, gamedb: Database) -> dict:
        tribes = list()
        teams = list()
        count_players = len(players)
        if count_players < game_options.target_team_size:
            raise MatchMakerError("Insufficient players for given team size")
        if count_players < game_options.multi_tribe_min_tribe_size * 2:
            raise MatchMakerError("Insufficient players to make two tribes")
        # generate tribes
        for tribe_name in [_DEFAULT_TRIBE_NAMES[int(n)] for n in random.sample(range(0, len(_DEFAULT_TRIBE_NAMES)), 2)]:
            tribe = database.Tribe(
                id=str(uuid.uuid4()),
                name="tribe/{}".format(tribe_name)
            )
            tribes.append(tribe)

        # generate teams
        for n in range(0, math.floor(count_players / game_options.target_team_size)):
            team = database.Team(
                id=str(uuid.uuid4()),
                name="team/{}".format(n),
            )
            teams.append(team)

        count_tribes = len(tribes)
        count_teams = len(teams)
        team_to_tribe_map = {}

        # randomly assign team, tribe to each player
        mutable_players = set()
        for n, player in enumerate(players):
            mutable_player = gamedb.player_from_id(player.id)
            tribe = tribes[n % count_tribes]
            team = teams[n % count_teams]
            if team.id not in team_to_tribe_map:
                team_to_tribe_map[team.id] = tribe
                tribe.count_teams += 1
            mutable_player.tribe_id = tribe.id
            mutable_player.team_id = team.id
            team.tribe_id = tribe.id
            tribe.count_players += 1
            team.count_players += 1
            tribe.count_players += 1
            team.count_players += 1
            mutable_players.add(mutable_player)

        # Save data
        game = gamedb.game_from_id(game_id)
        game.count_tribes = count_teams
        game.count_teams = count_teams
        game.count_players = count_players
        gamedb.save(game)

        for tribe in tribes:
            gamedb.save(tribe)
        for player in mutable_players:
            gamedb.save(player)
        for team in teams:
            gamedb.save(team)

        d = {}
        d['players'] = players
        d['teams'] = teams
        d['tribes'] = tribes
        return d
