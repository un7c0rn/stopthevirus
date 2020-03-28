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
from google.cloud.firestore_v1.document import DocumentReference
import logging
import sys

# TODO(brandon): change Data interface to use counters instead of size
# by convention.
_MULTIPROCESS_POOL_SIZE = 100

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def _log_message(message):
    logging.info(message)


@attr.s
class Counter(object):
    count: int = attr.ib(default=0)


class FirestoreData(Data):
    """This class wraps firebase objects with dynamically assigned
    properties in order to avoid having to call object.get(property)
    on every access."""

    def __init__(self, document: DocumentReference):
        self._document = document

    def __getattr__(self, name):
        if name == 'id':
            return self._document.id
        else:
            return self._document.get(name)


class FirestoreDataStream(object):
    def __init__(self, stream: Iterable):
        self._stream = stream

    def __iter__(self):
        return self

    def __next__(self):
        return FirestoreData(self._stream.__next__())


class FirestoreDB(Database):

    def __init__(self, json_config_path: Text, game_id: Text = None):
        cred = credentials.Certificate(json_config_path)
        firebase_admin.initialize_app(cred)
        self._game_id = game_id if game_id else self._create_game_id
        self._client = firestore.client()
        self._process_pool_size = _MULTIPROCESS_POOL_SIZE

    def _create_game_id(self) -> Text:
        return ""

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
            'count_players': Increment(moved_players_counter)
        })

        batch.update(self._client.collections('tribes').document(document_id=from_tribe.id), {
            'count_players': Increment(moved_players_counter)
        })
        batch.commit()

    def stream_entries(self, from_tribe: Tribe = None, from_team: Team = None,
                       from_challenge: Challenge = None) -> Iterable[Entry]:
        query = self._client.collection(
            'games/{}/entries'.format(self._game_id))
        if from_challenge:
            query = query.where('challenge_id', '==', from_challenge.id)
        if from_tribe:
            query = query.where('tribe_id', '==', from_tribe.id)
        if from_team:
            query = query.where('team_id', '==', from_team.id)
        return FirestoreDataStream(query.stream())

    def stream_teams(self, from_tribe: Tribe,
                     team_size_predicate_value: [int, None] = None,
                     order_by_size=True,
                     descending=False
                     ) -> Iterable[Team]:
        query = self._client.collection('games/{}/teams'.format(self._game_id)).where(
            'tribe_id', '==', from_tribe.id)
        if team_size_predicate_value:
            query = query.where('count_players', '==',
                                team_size_predicate_value)
        if order_by_size:
            query = query.order_by(
                'count_players', direction=Query.DESCENDING if descending else Query.ASCENDING)
        return FirestoreDataStream(stream=query.stream())

    def count_players(self, from_tribe: Tribe = None, from_team: Team = None) -> int:
        if from_tribe:
            return self._client.document('games/{}/tribes/{}'.format(self._game_id, from_tribe.id)).get().get('count_players')

        elif from_team:
            return self._client.document('games/{}/teams/{}'.format(self._game_id, from_team.id)).get().get('count_players')

    # TODO(brandon): remove active_team_predicate_value argument. unused and makes counters harder
    # at scale.
    def count_teams(self, from_tribe: Tribe = None, active_team_predicate_value=True) -> int:
        if from_tribe:
            query = self._client.document(
                'games/{}/tribes/{}'.format(self._game_id, from_tribe.id))
        else:
            query = self._client.document('games/{}'.format(self._game_id))
        return query.get().get('count_teams')

    def count_votes(self, from_team: Team = None, is_for_win: bool = False) -> Dict[Text, int]:
        player_counts = {}

        query = self._client.collection(
            'games/{}/votes'.format(self._game_id))
        if from_team:
            query = query.where('team_id', '==', from_team.id)

            for vote in FirestoreDataStream(query.stream()):
                voter = self.player_from_id(vote.from_id)
                team = self.team_from_id(voter.team_id)
                if team.id != from_team.id or not voter.active:
                    continue

                if vote.to_id not in player_counts:
                    player_counts[vote.to_id] = 1
                else:
                    player_counts[vote.to_id] = player_counts[vote.to_id] + 1
        else:
            for vote in FirestoreDataStream(query.stream()):
                if not vote.is_for_win:
                    continue

                if vote.to_id not in player_counts:
                    player_counts[vote.to_id] = 1
                else:
                    player_counts[vote.to_id] = player_counts[vote.to_id] + 1

        return player_counts

    def list_challenges(self, challenge_completed_predicate_value=False) -> Iterable[Challenge]:
        query = self._client.collection(
            'games/{}/challenges'.format(self._game_id)).where(
                'complete', '==', challenge_completed_predicate_value)
        return FirestoreDataStream(query.stream())

    def list_players(self, from_team: Team, active_player_predicate_value=True) -> Iterable[Player]:
        query=self._client.collection(
            'games/{}/players'.format(self._game_id)).where('team_id', '==', from_team.id).where(
                'active', '==', active_player_predicate_value)
        return FirestoreDataStream(query.stream())

    def list_teams(self, active_team_predicate_value=True) -> Iterable[Team]:
        query = self._client.collection(
            'games/{}/teams'.format(self._game_id)).where(
                'active', '==', active_team_predicate_value)
        return FirestoreDataStream(query.stream())

    def player_from_id(self, id: Text) -> Player:
        return FirestoreData(self._client.document("games/{}/players/{}".format(self._game_id, id)).get())

    def team_from_id(self, id: Text) -> Team:
        return FirestoreData(self._client.document("games/{}/teams/{}".format(self._game_id, id)).get())

    def tribe_from_id(self, id: Text) -> Tribe:
        return FirestoreData(self._client.document("games/{}/tribes/{}".format(self._game_id, id)).get())

    def challenge_from_id(self, id: Text) -> Challenge:
        return FirestoreData(self._client.document("games/{}/challenges/{}".format(self._game_id, id)).get())

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

    def save(self, data: Data) -> None:
        # if isinstance(data, Player):
        #     self._players[data.id] = data

        # if isinstance(data, Team):
        #     self._teams[data.id] = data
        pass

    def tribe(self, name: Text) -> Tribe:
        pass

    def player(self, name: Text) -> Player:
        pass

    def clear_votes(self) -> None:
        pass
