from game_engine.database import Database, Data
import attr
from typing import Dict, Iterable, Text, Tuple
from game_engine.database import Player, Team, Tribe
from game_engine.database import Challenge, Entry, Vote
from multiprocessing import Pool
from itertools import product
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client, Increment, Query

@attr.s
class Counter(object):
    count: int = attr.ib(default=0)

class CloudFirestore(Database):

    def __init__(self, config: Dict):
        cred = credentials.Certificate("/Users/brandontory/Downloads/stopthevirus-test-firebase-adminsdk-64w2z-79ee2e270a.json")
        firebase_admin.initialize_app(cred)
        self._client = firestore.client()
        self._config = config
        self._process_pool_size = 100

    def batch_update_tribe(self, from_tribe: Tribe, to_tribe: Tribe) -> None:
        # very strange that firestore doesn't support SQL like update without having to
        # submit multiple requests. going to assume that this is relatively performant when run
        # using cloud functions. in general for a tribe size of 1M this would take 2000 requests
        # which is nothing at Google scale, but expensive with the pricing model. could implement
        # this entire thing using MySQL on AWS but the API is too painful. favoring
        # GCP for ease of use.
        def update_fn(stream: Iterable, client: Client, updates_dict: Dict, batch_size=500, counter=None):
            batch = client.batch()
            document_iter = iter(stream)
            for _ in range(batch_size):
                try:
                    document_ref = next(document_iter).reference
                    batch.update(document_ref, updates_dict)
                    if counter:
                        counter.count += 1
                except StopIteration:
                    break
            batch.commit()

        teams = self._client.collection('teams').where(
            'tribe_id', '==', from_tribe.id).stream()
        players = self._client.collection('players').where(
            'tribe_id', '==', from_tribe.id).stream()
        moved_players_counter = Counter()

        with Pool(processes=self._process_pool_size) as pool:
            pool.starmap(update_fn, product(
                teams, self._client, {"tribe_id": to_tribe.id}))
            pool.starmap(update_fn, product(
                players, self._client, {"tribe_id": to_tribe.id}))

        batch = self._client.batch()
        batch.update(self._client.collections('tribes').document(document_id=to_tribe.id), {
            'size': Increment(moved_players_counter)
        })

        batch.update(self._client.collections('tribes').document(document_id=from_tribe.id), {
            'size': Increment(moved_players_counter)
        })
        batch.commit()

    def stream_entries(self, from_tribe: Tribe = None, from_team: Team = None, from_challenge: Challenge = None) -> Iterable[Entry]:
        query = self._client.collection('entries')
        if from_challenge:
            query = query.where('challenge_id', '==', from_challenge.id)
        if from_tribe:
            query = query.where('tribe_id', '==', from_tribe.id)
        if from_team:
            query = query.where('team_id', '==', from_team.id)
        return query.stream()

    def stream_teams(self, from_tribe: Tribe,
                     team_size_predicate_value: [int, None] = None,
                     order_by_size=True,
                     descending=False
                     ) -> Iterable[Team]:
        query = self._client.collection('teams').where(
            'tribe_id', '==', from_tribe.id)
        if team_size_predicate_value:
            query = query.where('size', '==', team_size_predicate_value)
        if order_by_size:
            query = query.order_by(
                'size', direction=Query.DESCENDING if descending else Query.ASCENDING)
        return query.stream()

    def count_players(self, from_tribe: Tribe = None, from_team: Team = None) -> int:
        if from_tribe:
            return self._client.collection('tribes').where('tribe_id', '==', from_tribe.id).get('size')

        elif from_team:
            return self._client.collection('teams').where('team_id', '==', from_tribe.id).get('size')

    def count_teams(self, from_tribe: Tribe = None, active_team_predicate_value=True) -> int:
        # if from_tribe:
        #     return len([team for team in self._teams.values() if team.tribe_id == from_tribe.id and team.active == active_team_predicate_value])
        # else:
        #     return len([team for team in self._teams.values() if team.active == active_team_predicate_value])
        # if from_tribe:
        #     return self._client.collection('tribes').where('tribe_id', '==', from_tribe.id).get('size')

        # elif from_team:
        #     return self._client.collection('teams').where('team_id', '==', from_tribe.id).get('size')
        pass

    def deactivate_player(self, player: Player) -> None:
        # player.active = False
        # self._players[player.id].active = False
        # self._teams[player.team_id].size = self._teams[player.team_id].size - 1
        # self._tribes[player.tribe_id].size = self._tribes[player.tribe_id].size - 1
        pass

    def deactivate_team(self, team: Team) -> None:
        # team.active = False
        # self._teams[team.id].active = False
        # pprint.pprint(self._teams)
        pass

    def count_votes(self, from_team: Team = None, is_for_win: bool = False) -> Dict[Text, int]:
        # player_counts = {}

        # if from_team:
        #     for vote in self._votes.values():
        #         voter = self.player_from_id(vote.from_id)
        #         team = self._teams[voter.team_id]
        #         if team.id != from_team.id or not voter.active:
        #             continue

        #         if vote.to_id not in player_counts:
        #             player_counts[vote.to_id] = 1
        #         else:
        #             player_counts[vote.to_id] = player_counts[vote.to_id] + 1
        # else:
        #     for vote in self._votes.values():
        #         if not vote.is_for_win:
        #             continue

        #         if vote.to_id not in player_counts:
        #             player_counts[vote.to_id] = 1
        #         else:
        #             player_counts[vote.to_id] = player_counts[vote.to_id] + 1

        # return player_counts
        pass

    def clear_votes(self) -> None:
        # self._votes = {}
        pass

    def list_challenges(self, challenge_completed_predicate_value=False) -> Iterable[Challenge]:
        # return [challenge for challenge in self._challenges.values() if not challenge.complete]
        pass

    def list_players(self, from_team: Team, active_player_predicate_value=True) -> Iterable[Player]:
        # return [player for player in self._players.values() if player.team_id == from_team.id and player.active == active_player_predicate_value]
        pass

    def list_teams(self, active_team_predicate_value=True) -> Iterable[Team]:
        # return [team for team in self._teams.values() if team.active == active_team_predicate_value]
        pass

    def player(self, name: Text) -> Player:
        pass

    def player_from_id(self, id: Text) -> Player:
        # return self._players[id]
        pass

    def tribe(self, name: Text) -> Tribe:
        # tribe_id = uuid.uuid1()
        # tribe = Tribe(id=tribe_id, name=name)
        # self._tribes[tribe_id] = tribe
        # return tribe
        pass

    def team_from_id(self, id: Text) -> Team:
        # return self._teams[id]
        pass

    def tribe_from_id(self, id: Text) -> Tribe:
        # return self._tribes[id]
        pass

    def challenge_from_id(self, id: Text) -> Challenge:
        # return self._challenges[id]
        pass

    def save(self, data: Data) -> None:
        # if isinstance(data, Player):
        #     self._players[data.id] = data

        # if isinstance(data, Team):
        #     self._teams[data.id] = data
        pass
