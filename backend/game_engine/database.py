from abc import ABC, abstractmethod, abstractclassmethod
import attr
from typing import Any, Iterable, Dict, Tuple, Optional
from game_engine.common import Serializable


class Data(ABC, Serializable):
    pass


@attr.s
class Game(Data):
    id: str = attr.ib('')
    name: str = attr.ib('')
    hashtag: str = attr.ib('')
    size: int = attr.ib(default=0)


@attr.s
class Player(Data):
    id: str = attr.ib('')
    tiktok: str = attr.ib(default='')
    email: str = attr.ib(default='')
    phone_number: str = attr.ib(default='')
    tribe_id: str = attr.ib(default='')
    team_id: str = attr.ib(default='')
    active: bool = attr.ib(default=True)


@attr.s
class Vote(Data):
    id: str = attr.ib('')
    from_id: str = attr.ib('')
    to_id: str = attr.ib('')
    is_for_win: bool = attr.ib(default=False)


@attr.s
class Ballot(Data):
    id: str = attr.ib('')
    challenge_id: str = attr.ib('')
    options: Dict = attr.ib(factory=Dict)


@attr.s
class Team(Data):
    id: str = attr.ib('')
    name: str = attr.ib('')
    size: int = attr.ib(default=0)
    tribe_id: str = attr.ib('')
    active: bool = attr.ib(default=True)


@attr.s
class Tribe(Data):
    id: str = attr.ib('')
    name: str = attr.ib('')
    size: int = attr.ib(default=0)
    active: bool = attr.ib(default=True)
    count_players: int = attr.ib(default=0)
    count_teams: int = attr.ib(default=0)


@attr.s
class Challenge(Data):
    id: str = attr.ib('')
    name: str = attr.ib('')
    message: str = attr.ib('')
    # TODO(brandon): game schedules make these timestamps
    # obsolete.
    start_timestamp: int = attr.ib(default=0)
    end_timestamp: int = attr.ib(default=0)
    complete: bool = attr.ib(default=False)


@attr.s
class Entry(Data):
    # An entry into a game challenge.
    id: str = attr.ib('')
    likes: int = attr.ib('')
    views: int = attr.ib('')
    player_id: str = attr.ib('')
    tribe_id: str = attr.ib('')
    challenge_id: str = attr.ib('')
    team_id: str = attr.ib('')
    url: str = attr.ib('')


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
