from twilio.twiml.messaging_response import MessagingResponse
from typing import Dict, Iterable, Tuple, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client, Increment, Query
from google.cloud.firestore_v1.document import DocumentReference
import re
import json
import os


class _FirestoreDB():
    def __init__(self, json_config_path: str = './stv-game-db-test-4c0ec2310b2e.json', game_id: str = None):
        cred = credentials.Certificate(json_config_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        self._game_id = game_id if game_id else ''
        self._client = firestore.client()

    def set_game_id(self, game_id: str):
        self._game_id = game_id

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

    def player_from_id(self, id: str):
        return self._client.document("games/{}/players/{}".format(self._game_id, id)).get()

    def deactivate_player(self, player: DocumentReference) -> None:
        batch = self._client.batch()
        player_ref = self._client.document(
            "games/{}/players/{}".format(self._game_id, player.id))
        tribe_ref = self._client.document(
            "games/{}/tribes/{}".format(self._game_id, player.get('tribe_id')))
        team_ref = self._client.document(
            "games/{}/teams/{}".format(self._game_id, player.get('team_id')))
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
        users = self._client.collection("users").where(
            "phone_number", "==", player.get("phone_number")).get()
        if len(users) > 0:
            user_ref = users[0].reference
            batch.update(user_ref, {
                'game_id': None
            })
        batch.commit()

    def find_ballot(self, player_id: str) -> DocumentReference:
        query = self._client.collection(
            f'games/{self._game_id}/players/{player_id}/ballots').order_by(
                'timestamp', direction=Query.DESCENDING)
        ballots = query.get()
        if len(ballots) > 0:
            return ballots[0]
        else:
            return None

    def find_player(self, phone_number: str) -> Optional[DocumentReference]:
        query = self._client.collection(
            f'games/{self._game_id}/players'
        ).where('phone_number', '==', phone_number)
        players = query.get()
        if len(players) > 0:
            return players[0]
        else:
            return None

    def vote(self, from_player_id: str, to_player_id: str, is_for_win: bool = False) -> None:
        player = self._client.document(
            "games/{}/players/{}".format(self._game_id, from_player_id)).get()
        team_id = player.get('team_id')
        vote_ref = self._client.collection(
            f'games/{self._game_id}/votes').document()
        vote_ref.set(
            {
                'from_id': from_player_id,
                'to_id': to_player_id,
                'is_for_win': is_for_win,
                'team_id': team_id
            }
        )

    def game_id_from_phone_number(self, phone_number: str) -> Optional[str]:
        query = self._client.collection('users').where(
            'phone_number', '==', phone_number)
        users = query.get()
        if len(users) > 0:
            return str(users[0].get('game_id'))
        else:
            return None


def _normalize_vote_option(message: str) -> str:
    return message.upper().replace(' ', '')


def _is_valid_vote_option(message: str) -> bool:
    return re.match('^(  +)?[A-Za-z]( +)?$', message) is not None


def _is_quit_message(message: str) -> bool:
    return re.match('^(quit|stop|QUIT|STOP)$', message) is not None


def sms_http(request):
    # 1. get the message and user phone number
    resp = MessagingResponse()
    number = request.form.get('From')
    message_body = request.form.get('Body')
    firestore = _FirestoreDB(json_config_path=os.path.join(
        os.path.dirname(__file__), 'stv-game-db-test-4c0ec2310b2e.json'))
    firestore.set_game_id(
        firestore.game_id_from_phone_number(phone_number=number))

    # 2. lookup the user in firestore by number
    player = firestore.find_player(phone_number=number)
    if not player:
        resp.message(
            """You're not in this game.""")
    else:
        # 3. determine whether the message is a valid voting option.
        if _is_valid_vote_option(message_body):
            # 4. if the message is a valid voting option, lookup the ballot for the vote caster.
            ballot = firestore.find_ballot(player_id=player.id)
            if not ballot:
                resp.message(
                    """An internal game error has occured, no ballot available.""")
                return str(resp)
            selection = _normalize_vote_option(message_body)
            options = ballot.get('options')
            if selection in options:
                vote_recipient_id = options[selection]
                firestore.vote(
                    from_player_id=player.id, to_player_id=options[selection], is_for_win=ballot.get('is_for_win'))
                resp.message(f'Your vote has been cast. Thanks!')
            else:
                resp.message(
                    f'\'{message_body}\' not a valid option. Please try again.')
        elif _is_quit_message(message_body):
            firestore.deactivate_player(
                firestore.player_from_id(id=player.id))
            resp.message('You have left the game. Thanks for playing!')
        else:
            resp.message(
                f'\'{message_body}\' is not a valid message. Please respond with one of the listed options.')

    return str(resp)
