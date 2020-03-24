from abc import ABC, abstractmethod, abstractclassmethod
import attr
from typing import Any, Iterable, Dict, Text, Tuple

class Data(ABC):
    def save(self):
        pass

    def sync(self):
        pass

@attr.s
class Player(Data):
    id: Text = attr.ib()
    instagram: Text = attr.ib(default='')
    email: Text = attr.ib(default='')
    tribe_id: Text = attr.ib(default='')
    team_id: Text = attr.ib(default='')

@attr.s
class Team(Data):
    id: Text = attr.ib()
    name: Text = attr.ib()

@attr.s
class Tribe(Data):
    id: Text = attr.ib()
    name: Text = attr.ib()

@attr.s
class Challenge(Data):
    id: Text = attr.ib()
    name: Text = attr.ib()
    message: Text = attr.ib('')
    start_timestamp: int = attr.ib(0)
    end_timestamp: int = attr.ib(0)

@attr.s
class Entry(Data):
    # An entry into a game challenge.
    id: Text = attr.ib()
    likes: int = attr.ib()
    views: int = attr.ib()
    player_id: Text = attr.ib()
    tribe_id: Text = attr.ib()
    challenge_id: Text = attr.ib()
    url: Text = attr.ib('')

class Database(ABC):

    @abstractmethod
    def batch_update_tribe(self, from_tribe: Tribe, to_tribe: Tribe) -> None:
        pass

    @abstractmethod
    def stream_entries(self, from_tribe: Tribe, from_challenge: Challenge) -> Iterable[Entry]:
        pass

    @abstractmethod
    def stream_teams(self, from_tribe: Tribe, 
        team_size_predicate_value: [int, None]=None,
        order_by_size=True,
        descending=False
        ) -> Iterable[Team]:
        pass

    @abstractmethod
    def count_players(self, from_tribe: Tribe) -> int:
        pass

    @abstractmethod
    def deactivate_player(self, player: Player) -> None:
        pass

    @abstractmethod
    def count_votes(self, from_team: Team) -> Tuple[Player, int]:
        pass
    
    @abstractmethod 
    def clear_votes(self) -> None:
        pass

    @abstractmethod
    def list_challenges(self, challenge_completed_predicate_value=False) -> Iterable[Challenge]:
        pass

    @abstractmethod
    def list_players(self, from_team: Team) -> Iterable[Player]:
        pass

    @abstractmethod
    def player(self, name: Text) -> Player:
        pass

    @abstractmethod
    def player_from_id(self, id: Text) -> Player:
        pass

    @abstractmethod
    def tribe(self, name: Text) -> Tribe:
        pass

    @abstractmethod
    def tribe_from_id(self, id: Text) -> Tribe:
        pass