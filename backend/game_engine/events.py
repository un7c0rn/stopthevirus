import attr
from game_engine.database import Player, Challenge, Entry, Team, Tribe
from game_engine.common import Serializable, GameError
from game_engine.common import log_message
from game_engine.database import Database
from typing import Iterable, List
import boto3
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
import copy
from typing import Text, Union, Any, Dict
import uuid
import pprint

_THREAD_POOL_SIZE = 100


@attr.s
class SMSEvent(Serializable):
    game_id: Text = attr.ib()

    def message_content(self, gamedb: Database) -> Text:
        return str(self.__class__.__name__)

    def recipient_list(self, gamedb: Database) -> List[Text]:
        # TODO(brandon) get recipient phone numbers from game db
        # and return as a list.
        return ["555-555-5555"]

    @classmethod
    def from_json(cls, json_text: Text) -> Serializable:
        d = json.loads(json_text)
        event_type = d['class']
        if event_type == 'NotifyPlayerScoreEvent':
            return NotifyPlayerScoreEvent.from_dict(json_dict=d)
        elif event_type == 'NotifyTeamReassignmentEvent':
            return NotifyTeamReassignmentEvent.from_dict(json_dict=d)
        elif event_type == 'NotifySingleTeamCouncilEvent':
            return NotifySingleTeamCouncilEvent.from_dict(json_dict=d)
        elif event_type == 'NotifySingleTribeCouncilEvent':
            return NotifySingleTribeCouncilEvent.from_dict(json_dict=d)
        elif event_type == 'NotifyTribalChallengeEvent':
            return NotifyTribalChallengeEvent.from_dict(json_dict=d)
        elif event_type == 'NotifyMultiTribeCouncilEvent':
            return NotifyMultiTribeCouncilEvent.from_dict(json_dict=d)
        elif event_type == 'NotifyFinalTribalCouncilEvent':
            return NotifyFinalTribalCouncilEvent.from_dict(json_dict=d)
        elif event_type == 'NotifyPlayerVotedOutEvent':
            return NotifyPlayerVotedOutEvent.from_dict(json_dict=d)
        elif event_type == 'NotifyTribalCouncilCompletionEvent':
            return NotifyTribalCouncilCompletionEvent.from_dict(json_dict=d)
        elif event_type == 'NotifyWinnerAnnouncementEvent':
            return NotifyWinnerAnnouncementEvent.from_dict(json_dict=d)
        elif event_type == 'NotifyImmunityAwardedEvent':
            return NotifyImmunityAwardedEvent.from_dict(json_dict=d)

    @classmethod
    def from_dict(self, json_dict: Dict):
        pass


class EventQueue(object):
    def put(self, event: SMSEvent):
        pass

    def get(self) -> SMSEvent:
        return SMSEvent()


class EventQueueError(Exception):
    pass


class AmazonSQS(EventQueue):
    def __init__(self, json_config_path: Text) -> None:
        with open(json_config_path, 'r') as f:
            config = json.loads(f.read())
            self._url = config['url']
            self._client = boto3.client(
                'sqs',
                aws_access_key_id=config['aws_access_key_id'],
                aws_secret_access_key=config['aws_secret_access_key'],
                region_name='us-east-2'
            )

    def _delete_message(self, receipt_handle: Text) -> None:
        self._client.delete_message(QueueUrl=self._url,
                                    ReceiptHandle=receipt_handle)

    def get(self) -> SMSEvent:
        response = self._client.receive_message(
            QueueUrl=self._url,
            MessageAttributeNames=[
                'string',
            ],
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20)
        log_message(str(response))

        if 'Messages' in response:
            message = response['Messages'][0]
            message_body = message['Body']
            log_message(
                'Received event with message body {}'.format(message_body))
            self._delete_message(message['ReceiptHandle'])
            return SMSEvent.from_json(json_text=message_body)
        else:
            raise EventQueueError('Queue empty.')

    def put_fn(self, event: SMSEvent) -> None:
        # TODO(brandon) add retry logic and error handling.
        response = self._client.send_message(
            QueueUrl=self._url,
            MessageBody=event.to_json(),
            MessageGroupId=event.game_id,
            MessageDeduplicationId=str(uuid.uuid4())
        )
        log_message(response)

    def put(self, event: SMSEvent, blocking: bool = False) -> None:
        if blocking:
            return self.put_fn(event=event)
        else:
            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self.put_fn, event)


@attr.s
class NotifyPlayerScoreEvent(SMSEvent):
    player: Player = attr.ib()
    challenge: Challenge = attr.ib()
    entry: Entry = attr.ib()
    points: int = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return cls(
            game_id=json_dict['game_id'],
            player=Player.from_dict(json_dict['player']),
            challenge=Challenge.from_dict(json_dict['challenge']),
            entry=Entry.from_dict(json_dict['entry']),
            points=json_dict['points']
        )


@attr.s
class NotifyTeamReassignmentEvent(SMSEvent):
    player: Player = attr.ib()
    team: Team = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyTeamReassignmentEvent(
            game_id=json_dict['game_id'],
            player=Player.from_dict(json_dict['player']),
            team=Team.from_dict(json_dict['team'])
        )


@attr.s
class NotifySingleTeamCouncilEvent(SMSEvent):
    winning_player: Player = attr.ib()
    losing_players: Iterable[Player] = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifySingleTeamCouncilEvent(
            game_id=json_dict['game_id'],
            winning_player=Player.from_dict(json_dict['winning_player']),
            losing_players=[Player.from_dict(p)
                            for p in json_dict['losing_players']]
        )


@attr.s
class NotifySingleTribeCouncilEvent(SMSEvent):
    winning_teams: Iterable[Team] = attr.ib()
    losing_teams: Iterable[Team] = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifySingleTribeCouncilEvent(
            game_id=json_dict['game_id'],
            winning_teams=[Team.from_dict(v)
                           for v in json_dict['winning_teams']],
            losing_teams=[Team.from_dict(v)
                          for v in json_dict['losing_teams']]
        )


@attr.s
class NotifyTribalChallengeEvent(SMSEvent):
    challenge: Challenge = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyTribalChallengeEvent(
            game_id=json_dict['game_id'],
            challenge=Challenge.from_dict(json_dict['challenge']),
        )


@attr.s
class NotifyMultiTribeCouncilEvent(SMSEvent):
    winning_tribe: Tribe = attr.ib()
    losing_tribe: Tribe = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyMultiTribeCouncilEvent(
            game_id=json_dict['game_id'],
            winning_tribe=Tribe.from_dict(json_dict['winning_tribe']),
            losing_tribe=Tribe.from_dict(json_dict['losing_tribe']),
        )


@attr.s
class NotifyFinalTribalCouncilEvent(SMSEvent):
    finalists: List[Player] = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyFinalTribalCouncilEvent(
            game_id=json_dict['game_id'],
            finalists=[Player.from_dict(v)
                       for v in json_dict['finalists']]
        )


@attr.s
class NotifyPlayerVotedOutEvent(SMSEvent):
    player: Player = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyPlayerVotedOutEvent(
            game_id=json_dict['game_id'],
            player=Player.from_dict(json_dict['player'])
        )


@attr.s
class NotifyTribalCouncilCompletionEvent(SMSEvent):

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyTribalCouncilCompletionEvent(
            game_id=json_dict['game_id'])


@attr.s
class NotifyWinnerAnnouncementEvent(SMSEvent):
    winner: Player = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyWinnerAnnouncementEvent(
            game_id=json_dict['game_id'],
            winner=Player.from_dict(json_dict['winner'])
        )


@attr.s
class NotifyImmunityAwardedEvent(SMSEvent):
    team: Team = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyImmunityAwardedEvent(
            game_id=json_dict['game_id'],
            team=Team.from_dict(json_dict['team'])
        )
