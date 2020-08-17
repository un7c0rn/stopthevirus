from typing import Text
from game_engine import database
from game_engine.common import GameOptions
from game_engine.database import Player, Team
from game_engine.firestore import FirestoreTribe
from google.cloud.firestore_v1.document import DocumentReference
from game_engine.database import Database

import uuid
import names
import random
import math
from queue import Queue
import json
from abc import ABC, abstractmethod


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

class GameSimulator(object):

    # Compliments:
    # https://stackoverflow.com/questions/26226801/making-random-phone-number-xxx-xxx-xxxx
    @classmethod
    def random_phone_number(cls):
        n = '0000000000'
        while '9' in n[3:6] or n[3:6] == '000' or n[6] == n[7] == n[8] == n[9]:
            n = str(random.randint(10**9, 10**10-1))
        return n[:3] + '-' + n[3:6] + '-' + n[6:]

    @classmethod
    def generate_game_environment(cls, count_players: int, team_size: int) -> Text:
        tribes = []
        teams = []
        players = []
        game_id = str(uuid.uuid4())

        for _ in range(count_players):
            name = names.get_first_name().lower()
            player = database.Player(
                id=str(uuid.uuid4()),
                tiktok=name,
                email="{}@hostname.com".format(name),
                phone_number=GameSimulator.random_phone_number()
            )
            players.append(player)

        for tribe_name in [_DEFAULT_TRIBE_NAMES[int(n)] for n in random.sample(range(0, len(_DEFAULT_TRIBE_NAMES)), 2)]:
            tribe = database.Tribe(
                id=str(uuid.uuid4()),
                name="tribe/{}".format(tribe_name)
            )
            tribes.append(tribe)

        for n in range(0, math.floor(count_players / team_size)):
            team = database.Team(
                id=str(uuid.uuid4()),
                name="team/{}".format(n),
            )
            teams.append(team)

        count_tribes = len(tribes)
        count_teams = len(teams)
        for n, player in enumerate(players):
            tribe = tribes[n % count_tribes]
            team = teams[n % count_teams]
            player.tribe_id = tribe.id
            player.team_id = team.id
            team.tribe_id = tribe.id
            tribe.size += 1
            team.size += 1

        games_dict = {}
        players_dict = {}
        teams_dict = {}
        tribes_dict = {}

        games_dict[game_id] = {
            "count_teams": count_teams,
            "count_players": count_teams,
            "name": "game/{}".format(game_id)
        }

        for player in players:
            players_dict[player.id] = player.to_dict()
            del players_dict[player.id]['id']

        for team in teams:
            teams_dict[team.id] = team.to_dict()
            del teams_dict[team.id]['id']

        for tribe in tribes:
            tribes_dict[tribe.id] = tribe.to_dict()
            del tribes_dict[tribe.id]['id']

        environment = {
            "games": games_dict,
            "games/{}/players".format(game_id): players_dict,
            "games/{}/teams".format(game_id): teams_dict,
            "games/{}/tribes".format(game_id): tribes_dict
        }

        json_environment = json.dumps(environment)
        print(json_environment)
        return json_environment


class MatchMaker(object):

    def generate_game_invite_link(self, game_id: Text) -> Text:
        return "{}/join-game/{}".format(_VIR_US_FE_HOSTNAME, game_id)

    def generate_start_game_verification_link(self, game_id: Text, game_starter_user_id: Text) -> Text:
        return "{}?game_id={}&game_starter_user_id={}&verify=start_game".format(_VIR_US_BE_CALLBACK_HOSTNAME, game_id, game_starter_user_id)

    def generate_join_game_verification_link(self, game_id: Text, player_id: Text) -> Text:
        return "{}?game_id={}&player_id={}&verify=join_game".format(_VIR_US_BE_CALLBACK_HOSTNAME, game_id, player_id)

    def generate_game_info_link(self, game_id: Text) -> Text:
        return "{}/game-info/{}".format(_VIR_US_FE_HOSTNAME, game_id)

class MatchMakerInterface(ABC):

    @classmethod
    @abstractmethod
    def generate_teams(cls, game_id: Text, players: list, team_size: int) -> dict:
        # Take in game_id and list of Players and return a list of Teams
        return

    @classmethod
    @abstractmethod
    def generate_tribes(cls, game_id: Text, players: list, game_options: GameOptions) -> dict:
        # Take in game_id, list of Players, and gameOptions, and return a list of Teams and Tribes
        return

class MatchMakerRoundRobin(MatchMakerInterface):

    @classmethod
    def generate_teams(cls, game_id: Text, players: list, team_size: int) -> dict:
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
            team.size += 1

        teams_dict = {}
        for team in teams:
            teams_dict[team.id] = team.to_dict()
            del teams_dict[team.id]['id']
        return teams_dict

    @classmethod
    def generate_tribes(cls, game_id: Text, players: list, game_options: GameOptions, gamedb: Database) -> dict:
        tribes = []
        teams = []
        count_players = len(players)
        if count_players < game_options.target_team_size:
            raise MatchMakerError("Insufficient players for given team size")
        if count_players < game_options.multi_tribe_min_tribe_size * 2:
            raise MatchMakerError("Insufficient players to make 2 tribes")
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

        # randomly assign team, tribe to each player
        for n, player in enumerate(players):
            tribe = tribes[n % count_tribes]
            team = teams[n % count_teams]
            player.tribe_id = tribe.id
            player.team_id = team.id
            team.tribe_id = tribe.id
            tribe.size += 1
            team.size += 1

        # Save data
        for tribe in tribes:
            gamedb.save(tribe)
        
        for player in players:
            gamedb.save(player)

        for team in teams:
            gamedb.save(team)
        
        d = {}
        d['players'] = players
        d['teams'] = teams
        d['tribes'] = tribes
        return d
        