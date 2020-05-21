from game_engine.database import Database, Data
import attr
from typing import Dict, Iterable, Text, Tuple
from game_engine.database import Player, Team, Tribe
from game_engine.database import Challenge, Entry, Vote, Game
from multiprocessing import Pool
from itertools import product
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client, Increment, Query
from google.cloud.firestore_v1.document import DocumentReference
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
import copy
import json
import uuid

# TODO(brandon): change Data interface to use counters instead of size
# by convention.
_THREAD_POOL_SIZE = 100

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)



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


class FirestoreGame(FirestoreData, Game):
    pass


class FirestorePlayer(FirestoreData, Player):
    pass


class FirestoreVote(FirestoreData, Vote):
    pass


class FirestoreTeam(FirestoreData, Team):
    pass


class FirestoreTribe(FirestoreData, Tribe):
    pass


class FirestoreChallenge(FirestoreData, Challenge):
    pass


class FirestoreEntry(FirestoreData, Entry):
    pass


class FirestoreDataStream(object):
    def __init__(self, stream: Iterable):
        self._stream = stream

    def __iter__(self):
        return self

    def __next__(self):
        return FirestoreData(self._stream.__next__())


class FirestorePlayerStream(FirestoreDataStream):
    def __next__(self):
        return FirestorePlayer(self._stream.__next__())


class FirestoreVoteStream(FirestoreDataStream):
    def __next__(self):
        return FirestoreVote(self._stream.__next__())


class FirestoreTeamStream(FirestoreDataStream, Team):
    def __next__(self):
        return FirestoreTeam(self._stream.__next__())


class FirestoreChallengeStream(FirestoreDataStream):
    def __next__(self):
        return FirestoreChallenge(self._stream.__next__())


class FirestoreEntryStream(FirestoreDataStream):
    def __next__(self):
        return FirestoreEntry(self._stream.__next__())


class FirestoreDB(Database):

    def __init__(self, json_config_path: Text, game_id: Text = None):
        cred = credentials.Certificate(json_config_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        self._game_id = game_id if game_id else self._create_game_id
        self._client = firestore.client()
        self._thread_pool_size = _THREAD_POOL_SIZE

    def import_collections(self, collections_json: Text) -> None:
        """Function for restoring test DB data."""

        batch = self._client.batch()
        collections_dict = json.loads(collections_json)
        for path in collections_dict:
            for document_id in collections_dict[path]:
                document_ref = self._client.document(
                    "{}/{}".format(path, document_id))
                properties_dict = collections_dict[path][document_id]
                properties_dict['id'] = document_id
                batch.set(document_ref, properties_dict, merge=True)
        batch.commit()

    def export_collections(self, collection_paths):
        """Function for persisting test DB data."""

        paths = collection_paths
        collections = dict()
        dict4json = dict()
        doc_count = 0

        for path in paths:
            collections[path] = self._client.collection(path).stream()
            dict4json[path] = {}
            for document in collections[path]:
                docdict = document.to_dict()
                dict4json[path][document.id] = docdict
                doc_count += 1

        return json.dumps(dict4json)

    def _create_game_id(self) -> Text:
        return ""

    def _tribe_update_fn(self, stream: Iterable, updates_dict: Dict, batch_size=500):
        batch = self._client.batch()
        document_iter = iter(stream)
        for _ in range(batch_size):
            try:
                document_ref = next(document_iter).reference
                batch.update(document_ref, updates_dict)
            except StopIteration:
                break
        batch.commit()

    def batch_update_tribe(self, from_tribe: Tribe, to_tribe: Tribe) -> None:
        # TODO(brandon): consider strengthening this because if the server crashes
        # mid-merge the counts will be difficult to fix.
        teams = self._client.collection('games/{}/teams'.format(self._game_id)).where(
            'tribe_id', '==', from_tribe.id).stream()
        players = self._client.collection('games/{}/players'.format(self._game_id)).where(
            'tribe_id', '==', from_tribe.id).stream()
        player_count = self.count_players(from_tribe=from_tribe)
        team_count = self.count_teams(from_tribe=from_tribe)

        with ThreadPoolExecutor(max_workers=self._thread_pool_size) as executor:
            executor.submit(self._tribe_update_fn, teams,
                            {"tribe_id": to_tribe.id})
            executor.submit(self._tribe_update_fn, players,
                            {"tribe_id": to_tribe.id})

        batch = self._client.batch()
        batch.update(self._client.document('games/{}/tribes/{}'.format(self._game_id, to_tribe.id)), {
            'count_players': Increment(player_count)
        })

        batch.update(self._client.document('games/{}/tribes/{}'.format(self._game_id, to_tribe.id)), {
            'count_teams': Increment(team_count)
        })

        batch.update(self._client.document('games/{}/tribes/{}'.format(self._game_id, from_tribe.id)), {
            'count_players': Increment(-1 * player_count)
        })

        batch.update(self._client.document('games/{}/tribes/{}'.format(self._game_id, from_tribe.id)), {
            'count_teams': Increment(-1 * team_count)
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
        return FirestoreEntryStream(query.stream())

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
        return FirestoreTeamStream(stream=query.stream())

    def stream_players(self, active_player_predicate_value=True) -> Iterable[Player]:
        query = self._client.collection('games/{}/players'.format(self._game_id)).where(
            'active', '==', active_player_predicate_value
        )
        return FirestorePlayerStream(stream=query.stream())

    def count_players(self, from_tribe: Tribe = None, from_team: Team = None) -> int:
        if from_tribe:
            return self._client.document('games/{}/tribes/{}'.format(self._game_id, from_tribe.id)).get().get('count_players')

        elif from_team:
            return self._client.document('games/{}/teams/{}'.format(self._game_id, from_team.id)).get().get('count_players')
        else:
            return self._client.document('games/{}'.format(self._game_id)).get().get('count_players')

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

            for vote in FirestoreVoteStream(query.stream()):
                voter = self.player_from_id(vote.from_id)
                team = self.team_from_id(voter.team_id)
                if team.id != from_team.id or not voter.active:
                    continue

                if vote.to_id not in player_counts:
                    player_counts[vote.to_id] = 1
                else:
                    player_counts[vote.to_id] = player_counts[vote.to_id] + 1
        else:
            for vote in FirestoreVoteStream(query.stream()):
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
        return FirestoreChallengeStream(query.stream())

    def list_players(self, from_team: Team, active_player_predicate_value=True) -> Iterable[Player]:
        query = self._client.collection(
            'games/{}/players'.format(self._game_id)).where('team_id', '==', from_team.id).where(
                'active', '==', active_player_predicate_value)
        return FirestorePlayerStream(query.stream())

    def list_teams(self, active_team_predicate_value=True) -> Iterable[Team]:
        query = self._client.collection(
            'games/{}/teams'.format(self._game_id)).where(
                'active', '==', active_team_predicate_value)
        return FirestoreTeamStream(query.stream())

    def game_from_id(self, id: Text) -> Player:
        return FirestoreGame(self._client.document("games/{}".format(self._game_id)).get())

    def player_from_id(self, id: Text) -> Player:
        return FirestorePlayer(self._client.document("games/{}/players/{}".format(self._game_id, id)).get())

    def team_from_id(self, id: Text) -> Team:
        return FirestoreTeam(self._client.document("games/{}/teams/{}".format(self._game_id, id)).get())

    def tribe_from_id(self, id: Text) -> Tribe:
        return FirestoreTribe(self._client.document("games/{}/tribes/{}".format(self._game_id, id)).get())

    def challenge_from_id(self, id: Text) -> Challenge:
        return FirestoreChallenge(self._client.document("games/{}/challenges/{}".format(self._game_id, id)).get())

    def deactivate_player(self, player: Player) -> None:
        batch = self._client.batch()
        player_ref = self._client.document(
            "games/{}/players/{}".format(self._game_id, player.id))
        tribe_ref = self._client.document(
            "games/{}/tribes/{}".format(self._game_id, player.tribe_id))
        team_ref = self._client.document(
            "games/{}/teams/{}".format(self._game_id, player.team_id))
        game_ref = self._client.document("games/{}".format(self._game_id))

        batch.update(player_ref, {
            'active': False
        })

        batch.update(tribe_ref, {
            'count_players': Increment(-1)
        })

        batch.update(team_ref, {
            'count_players': Increment(-1)
        })

        batch.update(game_ref, {
            'count_players': Increment(-1)
        })

        batch.commit()

    def deactivate_team(self, team: Team) -> None:
        batch = self._client.batch()
        team_ref = self._client.document(
            "games/{}/teams/{}".format(self._game_id, team.id))
        tribe_ref = self._client.document(
            "games/{}/tribes/{}".format(self._game_id, team.tribe_id))
        game_ref = self._client.document("games/{}".format(self._game_id))

        batch.update(team_ref, {
            'active': False
        })

        batch.update(tribe_ref, {
            'count_teams': Increment(-1)
        })

        batch.update(game_ref, {
            'count_teams': Increment(-1)
        })

        batch.commit()

    def save(self, data: Data) -> None:
        properties_dict = copy.deepcopy(data.__dict__)
        if '_document' in properties_dict:
            del properties_dict['_document']
        if isinstance(data, Player):
            self._client.document("games/{}/players/{}".format(self._game_id, data.id)).set(
                properties_dict
            )
        elif isinstance(data, Team):
            self._client.document("games/{}/teams/{}".format(self._game_id, data.id)).set(
                properties_dict
            )

    def tribe(self, name: Text) -> Tribe:
        tribe_ref = self._client.collection(
            "games/{}/tribes".format(self._game_id)).document()
        tribe_ref.set({
            'name': name,
            'count_players': 0,
            'count_teams': 0
        })
        return FirestoreData(tribe_ref.get())

    def player(self, name: Text) -> Player:
        batch = self._client.batch()
        player_ref = self._client.collection(
            "games/{}/players".format(self._game_id)).document()
        batch.set(player_ref, {
            'name': name,
            'active': True
        })

        game_ref = self._client.document("games/{}".format(self._game_id))
        batch.update(game_ref, {
            'count_players': Increment(1)
        })

        batch.commit()
        return FirestoreData(player_ref.get())

    def _delete_vote_fn(self, stream: Iterable, batch_size=500):
        batch = self._client.batch()
        document_iter = iter(stream)
        for _ in range(batch_size):
            try:
                document_ref = next(document_iter).reference
                batch.delete(document_ref)
            except StopIteration:
                break
        batch.commit()

    def clear_votes(self) -> None:
        votes = self._client.collection('votes').stream()
        with ThreadPoolExecutor(max_workers=self._thread_pool_size) as executor:
            executor.submit(self._delete_vote_fn, votes)
