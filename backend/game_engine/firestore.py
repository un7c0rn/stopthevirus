from game_engine.database import Database, Data
import attr
from typing import Dict, Iterable, Tuple, Optional
from game_engine.database import Player, Team, Tribe
from game_engine.database import Challenge, Entry, Vote, Game, Ballot
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
import datetime
import time

# TODO(brandon): change Data interface to use counters instead of size
# by convention.
_THREAD_POOL_SIZE = 100

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class FirestoreData(Data):
    """This class wraps firebase objects with dynamically assigned
    properties in order to avoid having to call object.get(property)
    on every access."""

    def __init__(self, document: DocumentReference):
        setattr(self, 'id', document.id)
        document_dict = document.to_dict()
        if document_dict:
            for k, v in document_dict.items():
                setattr(self, k, v)


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


class FirestoreBallot(FirestoreData, Ballot):
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

    def __init__(self, json_config_path: str, game_id: str = None):
        cred = credentials.Certificate(json_config_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        self._game_id = game_id if game_id else self._create_game_id()
        self._client = firestore.client()
        self._thread_pool_size = _THREAD_POOL_SIZE

    def _create_game_id(self):
        return ""

    def import_collections(self, collections_json: str) -> None:
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

    def delete_collection(self, path, batch_size: int = 10):
        coll_ref = self._client.collection(path)
        docs = coll_ref.limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            print(f'Deleting doc {doc.id} => {doc.to_dict()}')
            doc.reference.delete()
            deleted = deleted + 1

        if deleted >= batch_size:
            return self.delete_collection(path, batch_size)

    @classmethod
    def add_game(cls, json_config_path: str, hashtag: str, country_code: str = 'US', max_reschedules: int = 5) -> str:
        cred = credentials.Certificate(json_config_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        client = firestore.client()
        game_ref = client.collection('games').document()
        game_ref.set({
            'count_players': 0,
            'count_teams': 0,
            'count_tribes': 0,
            'country_code': country_code,
            'game_has_started': False,
            'max_reschedules': max_reschedules,
            'times_rescheduled': 0,
            'last_checked_date': '2020-01-01',
            'game':  hashtag,
            'hashtag': hashtag,
            'id': game_ref.id
        })
        return str(game_ref.id)

    @classmethod
    def add_user(cls, json_config_path: str, name: str, tiktok: str, phone_number: str, game_id: str = None) -> None:
        cred = credentials.Certificate(json_config_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        client = firestore.client()
        users = client.collection('users').where(
            'phone_number', '==', phone_number).get()
        if len(users) == 0:
            user_ref = client.collection('users').document()
        else:
            user_ref = users[0].reference
        user_ref.set({
            'name': name,
            'tiktok': tiktok,
            'phone_number': phone_number,
            'id': user_ref.id,
            'game_id': game_id
        })
        return user_ref.id

    def add_challenge_entry(self, entry: Entry) -> None:
        entry_ref = self._client.collection('games/{}/entries').document()
        entry_ref.set({
            'likes': entry.likes,
            'views': entry.views,
            'player_id': entry.player_id,
            'tribe_id': entry.tribe_id,
            'challenge_id': entry.challenge_id,
            'team_id': entry.team_id,
            'url': entry.url
        })
        return str(entry_ref.id)

    def add_challenge(self, challenge: Challenge) -> None:
        challenge_ref = self._client.collection(
            f'games/{self._game_id}/challenges').document()
        challenge_ref.set({
            'name': challenge.name,
            'message': challenge.message,
            'start_timestamp': challenge.start_timestamp,
            'end_timestamp': challenge.end_timestamp,
            'complete': challenge.complete,
            'id': str(challenge_ref.id)
        })
        return str(challenge_ref.id)

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

        batch.update(self._client.document('games/{}/tribes/{}'.format(self._game_id, to_tribe.id)), {
            'size': Increment(player_count)
        })

        batch.update(self._client.document('games/{}/tribes/{}'.format(self._game_id, from_tribe.id)), {
            'count_players': Increment(-1 * player_count)
        })

        batch.update(self._client.document('games/{}/tribes/{}'.format(self._game_id, from_tribe.id)), {
            'count_teams': Increment(-1 * team_count)
        })

        batch.update(self._client.document('games/{}/tribes/{}'.format(self._game_id, from_tribe.id)), {
            'size': Increment(-1 * player_count)
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
        elif order_by_size:
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

    def count_votes(self, from_team: Team = None, is_for_win: bool = False) -> Dict[str, int]:
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
        challenge_list = []
        for doc in query.stream():
            fc = FirestoreChallenge(document=doc)
            challenge_list.append(fc)
        return challenge_list

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

    def game_from_id(self, id: str) -> Game:
        return FirestoreGame(self._client.document("games/{}".format(self._game_id)).get())

    def player_from_id(self, id: str) -> Player:
        return FirestorePlayer(self._client.document("games/{}/players/{}".format(self._game_id, id)).get())

    def team_from_id(self, id: str) -> Team:
        return FirestoreTeam(self._client.document("games/{}/teams/{}".format(self._game_id, id)).get())

    def tribe_from_id(self, id: str) -> Tribe:
        return FirestoreTribe(self._client.document("games/{}/tribes/{}".format(self._game_id, id)).get())

    def challenge_from_id(self, id: str) -> Challenge:
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
        batch.update(tribe_ref, {
            'size': Increment(-1)
        })
        batch.update(team_ref, {
            'count_players': Increment(-1)
        })
        batch.update(team_ref, {
            'size': Increment(-1)
        })
        batch.update(game_ref, {
            'count_players': Increment(-1)
        })
        users = self._client.collection("users").where(
            "phone_number", "==", player.phone_number).get()
        if len(users) > 0:
            user_ref = users[0].reference
            batch.update(user_ref, {
                'game_id': None
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
        elif isinstance(data, Tribe):
            self._client.document("games/{}/tribes/{}".format(self._game_id, data.id)).set(
                properties_dict
            )
        elif isinstance(data, Challenge):
            self._client.document("games/{}/challenges/{}".format(self._game_id, data.id)).set(
                properties_dict
            )

    def tribe(self, name: str) -> Tribe:
        tribe_ref = self._client.collection(
            "games/{}/tribes".format(self._game_id)).document()
        tribe_ref.set({
            'name': name,
            'count_players': 0,
            'count_teams': 0,
            'size': 0,
            'active': True,
            'id': tribe_ref.id
        })
        return FirestoreData(tribe_ref.get())

    def player(self, name: str, tiktok: str = None, phone_number: str = None) -> Player:
        batch = self._client.batch()
        player_ref = self._client.collection(
            "games/{}/players".format(self._game_id)).document()
        batch.set(player_ref, {
            'name': name,
            'active': True,
            'tiktok': tiktok,
            'phone_number': phone_number
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
        votes = self._client.collection(
            f'games/{self._game_id}/votes').stream()
        with ThreadPoolExecutor(max_workers=self._thread_pool_size) as executor:
            executor.submit(self._delete_vote_fn, votes)

    def find_matchmaker_games(self, region="US") -> list:
        games_list = []
        db = self._client
        games = db.collection('games').where('country_code', '==', region).where(
            'game_has_started', '==', False).stream()

        for game in games:
            try:
                # Avoid checking in query to allow for key to not exist
                if not game.to_dict().get("to_be_deleted"):
                    games_list.append(game)
            except:
                pass
        return games_list

    def ballot(self, player_id: str, challenge_id: str, options: Dict[str, str], is_for_win: bool = False) -> None:
        ballot_ref = self._client.collection(
            f'games/{self._game_id}/players/{player_id}/ballots'
        ).document()
        ballot_ref.set(
            {
                'challenge_id': challenge_id if challenge_id else '',
                'options': options,
                'timestamp': time.time(),
                'is_for_win': is_for_win
            }
        )
        return FirestoreData(ballot_ref.get())

    def find_ballot(self, player: Player) -> Iterable[Ballot]:
        query = self._client.collection(
            f'games/{self._game_id}/players/{player.id}/ballots').order_by(
                'timestamp', direction=Query.DESCENDING)
        return FirestoreBallot(query.get()[0])

    def find_player(self, phone_number: str) -> Optional[Player]:
        query = self._client.collection(
            f'games/{self._game_id}/players'
        ).where('phone_number', '==', phone_number)
        players = query.get()
        if len(players) > 0:
            return FirestorePlayer(players[0])
        else:
            return None
