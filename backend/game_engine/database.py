from abc import ABC, abstractmethod, abstractclassmethod
import attr
from typing import Any, Iterable, Dict, Tuple, Optional
from game_engine.common import Serializable


class Data(ABC, Serializable):
    def get(self, key):
        return getattr(self, key)


@attr.s(eq=False)
class Game(Data):
    id: str = attr.ib(default='')
    name: str = attr.ib(default='')
    hashtag: str = attr.ib(default='')
    count_tribes: int = attr.ib(default=0)
    count_teams: int = attr.ib(default=0)
    count_players: int = attr.ib(default=0)


@attr.s(eq=False)
class Tribe(Data):
    id: str = attr.ib(default='')
    name: str = attr.ib(default='')
    active: bool = attr.ib(default=True)
    count_teams: int = attr.ib(default=0)
    count_players: int = attr.ib(default=0)


@attr.s(eq=False)
class Team(Data):
    id: str = attr.ib(default='')
    name: str = attr.ib(default='')
    tribe_id: str = attr.ib(default='')
    active: bool = attr.ib(default=True)
    count_players: int = attr.ib(default=0)


@attr.s(eq=False)
class Player(Data):
    id: str = attr.ib(default='')
    name: str = attr.ib(default='')
    tiktok: str = attr.ib(default='')
    email: str = attr.ib(default='')
    phone_number: str = attr.ib(default='')
    tribe_id: str = attr.ib(default='')
    team_id: str = attr.ib(default='')
    active: bool = attr.ib(default=True)


@attr.s(eq=False)
class User(Data):
    game_id: str = attr.ib(default='')
    id: str = attr.ib(default='')
    name: str = attr.ib(default='')
    phone_number = attr.ib(default='')
    tiktok = attr.ib(default='')


@attr.s(eq=False)
class Vote(Data):
    id: str = attr.ib(default='')
    from_id: str = attr.ib(default='')
    to_id: str = attr.ib(default='')
    is_for_win: bool = attr.ib(default=False)


@attr.s(eq=False)
class Ballot(Data):
    id: str = attr.ib(default='')
    challenge_id: str = attr.ib(default='')
    options: Dict = attr.ib(factory=dict)


@attr.s(eq=False)
class Challenge(Data):
    id: str = attr.ib(default='')
    name: str = attr.ib(default='')
    message: str = attr.ib(default='')
    complete: bool = attr.ib(default=False)


@attr.s(eq=False)
class Entry(Data):
    # An entry into a game challenge.
    id: str = attr.ib(default='')
    likes: int = attr.ib(default=0)
    views: int = attr.ib(default=0)
    player_id: str = attr.ib(default='')
    tribe_id: str = attr.ib(default='')
    challenge_id: str = attr.ib(default='')
    team_id: str = attr.ib(default='')
    url: str = attr.ib(default='')


class Database(ABC):

    @abstractmethod
    def batch_update_tribe(self, from_tribe: Tribe, to_tribe: Tribe) -> None:
        pass

    @abstractmethod
    def stream_entries(self, from_tribe: Tribe = None, from_team: Team = None, from_challenge: Challenge = None) -> Iterable[Entry]:
        pass

    @abstractmethod
    def stream_teams(self, from_tribe: Tribe,
                     team_size_predicate_value: [int, None] = None,
                     order_by_size=True,
                     descending=False
                     ) -> Iterable[Team]:
        pass

    @abstractmethod
    def stream_players(self, active_player_predicate_value=True) -> Iterable[Player]:
        pass

    @abstractmethod
    def count_players(self, from_tribe: Tribe) -> int:
        pass

    @abstractmethod
    def count_teams(self, from_tribe: Tribe = None, active_team_predicate_value=True) -> int:
        pass

    @abstractmethod
    def deactivate_player(self, player: Player) -> None:
        pass

    @abstractmethod
    def count_votes(self, from_team: Team, is_for_win: bool = False) -> Tuple[Player, int]:
        pass

    @abstractmethod
    def clear_votes(self) -> None:
        pass

    @abstractmethod
    def list_challenges(self, challenge_completed_predicate_value=False) -> Iterable[Challenge]:
        pass

    @abstractmethod
    def list_players(self, from_team: Team, active_player_predicate_value=True) -> Iterable[Player]:
        pass

    @abstractmethod
    def list_teams(self, active_team_predicate_value=True) -> Iterable[Team]:
        pass

    @abstractmethod
    def player(self, name: str) -> Player:
        pass

    @abstractmethod
    def player_from_id(self, id: str) -> Player:
        pass

    @abstractmethod
    def game_from_id(self, id: str) -> Game:
        pass

    @abstractmethod
    def tribe(self, name: str) -> Tribe:
        pass

    @abstractmethod
    def tribe_from_id(self, id: str) -> Tribe:
        pass

    @abstractmethod
    def team_from_id(self, id: str) -> Team:
        pass

    @abstractmethod
    def save(self, data: Data) -> None:
        pass

    @abstractmethod
    def ballot(self, player_id: str, challenge_id: str, options: Dict[str, str]) -> None:
        pass

    @abstractmethod
    def find_ballot(self, player: Player) -> Iterable[Ballot]:
        pass

    @abstractmethod
    def find_player(self, phone_number: str) -> Optional[Player]:
        pass

    @abstractmethod
    def find_user(self, phone_number: str) -> Optional[User]:
        pass
