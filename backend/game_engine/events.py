import attr
from game_engine.database import Player, Challenge, Entry, Team, Tribe
from game_engine.common import Serializable, GameError, GameOptions
from game_engine.common import log_message
from game_engine.common import STV_I18N_TABLE
from game_engine.database import Database
from game_engine import messages
from typing import Iterable, List
import boto3
import json
import sys
from concurrent.futures import ThreadPoolExecutor
import copy
from typing import Text, Union, Any, Dict
import uuid

_NOP_SMS_ADDRESS = "555-123-4567"


@attr.s
class SMSEventMessage(Serializable):
    content: Text = attr.ib()
    recipient_phone_numbers: List[Text] = attr.ib(factory=list)


@attr.s
class SMSEvent(Serializable):
    game_id: Text = attr.ib()
    game_options: GameOptions = attr.ib()

    def messages(self, gamedb: Database) -> List[SMSEventMessage]:
        return [
            SMSEventMessage(
                content=str(self.__class__.__name__),
                recipient_phone_numbers=[_NOP_SMS_ADDRESS]
            )
        ]

    @classmethod
    def from_json(cls, json_text: Text, game_options: GameOptions) -> Serializable:
        d = json.loads(json_text)
        d['game_options'] = game_options
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
    def __init__(self, json_config_path: Text, game_id: Text, game_options: GameOptions = None) -> None:
        self.game_id = game_id
        with open(json_config_path, 'r') as f:
            config = json.loads(f.read())
            self._url = config['url']
            self._client = boto3.client(
                'sqs',
                aws_access_key_id=config['aws_access_key_id'],
                aws_secret_access_key=config['aws_secret_access_key'],
                region_name='us-east-2'
            )
        # store a reference to game options for timezone specific
        # event deserialization from the AWS queue.
        self._game_options = game_options if game_options else GameOptions(
            game_schedule=STV_I18N_TABLE['US']
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

        if 'Messages' in response:
            message = response['Messages'][0]
            message_body = message['Body']
            log_message(
                message='Received event with message body {}'.format(message_body), game_id=self.game_id)
            self._delete_message(message['ReceiptHandle'])
            return SMSEvent.from_json(json_text=message_body, game_options=self._game_options)
        else:
            raise EventQueueError('Queue empty.')

    def put_fn(self, event: SMSEvent) -> None:
        try:
            # TODO(brandon) add retry logic and error handling.
            log_message(message="Putting {} on queue {}.".format(
                event.to_json(), self._url), game_id=self.game_id)
            response = self._client.send_message(
                QueueUrl=self._url,
                MessageBody=event.to_json(),
                MessageGroupId=event.game_id,
                MessageDeduplicationId=str(uuid.uuid4())
            )
        except Exception as e:
            log_message(
                messages=f'put_fn failed for event {event} with exception {str(e)}.')

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
            game_options=json_dict['game_options'],
            player=Player.from_dict(json_dict['player']),
            challenge=Challenge.from_dict(json_dict['challenge']),
            entry=Entry.from_dict(json_dict['entry']),
            points=json_dict['points']
        )

    def messages(self, gamedb: Database) -> List[SMSEventMessage]:
        return [
            SMSEventMessage(
                content=messages.NOTIFY_PLAYER_SCORE_EVENT_MSG_FMT.format(
                    header=messages.VIR_US_SMS_HEADER,
                    points=self.points,
                    time=self.game_options.game_schedule.localized_time_string(
                        self.game_options.game_schedule.daily_challenge_end_time
                    )
                ),
                recipient_phone_numbers=[
                    self.player.phone_number
                ]
            )
        ]


@attr.s
class NotifyTeamReassignmentEvent(SMSEvent):
    player: Player = attr.ib()
    team: Team = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyTeamReassignmentEvent(
            game_id=json_dict['game_id'],
            game_options=json_dict['game_options'],
            player=Player.from_dict(json_dict['player']),
            team=Team.from_dict(json_dict['team'])
        )

    def messages(self, gamedb: Database) -> List[SMSEventMessage]:
        team_players = gamedb.list_players(from_team=self.team)
        return [
            SMSEventMessage(
                content=messages.NOTIFY_TEAM_REASSIGNMENT_EVENT_MSG_FMT.format(
                    header=messages.VIR_US_SMS_HEADER,
                    team=messages.players_as_formatted_list(
                        players=team_players),
                    date=self.game_options.game_schedule.tomorrow_localized_string,
                    time=self.game_options.game_schedule.localized_time_string(
                        self.game_options.game_schedule.daily_challenge_start_time)
                ),
                recipient_phone_numbers=[
                    self.player.phone_number
                ]
            )
        ]


@attr.s
class NotifySingleTeamCouncilEvent(SMSEvent):
    winning_player: Player = attr.ib()
    losing_players: Iterable[Player] = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifySingleTeamCouncilEvent(
            game_id=json_dict['game_id'],
            game_options=json_dict['game_options'],
            winning_player=Player.from_dict(json_dict['winning_player']),
            losing_players=[Player.from_dict(p)
                            for p in json_dict['losing_players']]
        )

    def messages(self, gamedb: Database) -> List[SMSEventMessage]:
        player_messages = []
        count_players = gamedb.count_players(
            from_tribe=gamedb.tribe_from_id(self.winning_player.tribe_id))
        for player in self.losing_players:
            options_map = messages.players_as_formatted_options_map(
                players=self.losing_players, exclude_player=player)
            # NOTE(brandon): we perform this synchronously to guarantee that ballots are
            # created in the DB before SMS messages go out to users.
            gamedb.ballot(
                player_id=player.id, options=options_map.options, challenge_id=None
            )
            player_messages.append(
                SMSEventMessage(
                    content=messages.NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_LOSING_MSG_FMT.format(
                        header=messages.VIR_US_SMS_HEADER,
                        winner=messages.format_tiktok_username(
                            self.winning_player.tiktok),
                        players=count_players,
                        time=self.game_options.game_schedule.localized_time_string(
                            self.game_options.game_schedule.daily_challenge_end_time),
                        options=options_map.formatted_string
                    ),
                    recipient_phone_numbers=player.phone_number
                )
            )

        options_map = messages.players_as_formatted_options_map(
            players=self.losing_players, exclude_player=self.winning_player)
        gamedb.ballot(
            player_id=self.winning_player.id, options=options_map.formatted_string, challenge_id=None
        )
        player_messages.append(
            SMSEventMessage(
                content=messages.NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_WINNING_MSG_FMT.format(
                    header=messages.VIR_US_SMS_HEADER,
                    players=count_players,
                    time=self.game_options.game_schedule.localized_time_string(
                        self.game_options.game_schedule.daily_challenge_end_time),
                    options=options_map.formatted_string
                ),
                recipient_phone_numbers=self.winning_player.phone_number
            )
        )

        return player_messages


@attr.s
class NotifySingleTribeCouncilEvent(SMSEvent):
    winning_teams: Iterable[Team] = attr.ib()
    losing_teams: Iterable[Team] = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifySingleTribeCouncilEvent(
            game_id=json_dict['game_id'],
            game_options=json_dict['game_options'],
            winning_teams=[Team.from_dict(v)
                           for v in json_dict['winning_teams']],
            losing_teams=[Team.from_dict(v)
                          for v in json_dict['losing_teams']]
        )

    def messages(self, gamedb: Database) -> List[SMSEventMessage]:
        player_messages = []
        for team in self.losing_teams:
            losing_players = []
            for losing_player in gamedb.list_players(from_team=team):
                losing_players.append(losing_player)

            # NOTE: UX isn't perfect here because we'll show the player's own name
            # as an option to vote out. For MVP this helps with scale because the alternative
            # requires sending a different message to every player (as opposed to every team)
            # which is about a 5x cost increase for SMS.
            recipient_phone_numbers = [p.phone_number for p in losing_players]
            options_map = messages.players_as_formatted_options_map(
                players=losing_players)
            # TODO(brandon): this is slow and expensive. batch the ballot writes to gamedb.
            for player in losing_players:
                gamedb.ballot(
                    player_id=player.id, options=options_map.options, challenge_id=None
                )

            player_messages.append(
                SMSEventMessage(
                    content=messages.NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_LOSING_MSG_FMT.format(
                        header=messages.VIR_US_SMS_HEADER,
                        time=self.game_options.game_schedule.localized_time_string(
                            self.game_options.game_schedule.daily_tribal_council_end_time
                        ),
                        options=options_map.formatted_string
                    ),
                    recipient_phone_numbers=recipient_phone_numbers
                )
            )

        winning_player_phone_numbers = []
        for team in self.winning_teams:
            winning_players = gamedb.list_players(from_team=team)
            winning_player_phone_numbers.extend(
                [p.phone_number for p in winning_players]
            )

        player_messages.append(
            SMSEventMessage(
                content=messages.NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_WINNING_MSG_FMT.format(
                    header=messages.VIR_US_SMS_HEADER,
                    time=self.game_options.game_schedule.localized_time_string(
                        self.game_options.game_schedule.daily_tribal_council_end_time
                    ),
                    challenge_time=self.game_options.game_schedule.localized_time_string(
                        self.game_options.game_schedule.daily_challenge_start_time
                    )
                ),
                recipient_phone_numbers=winning_player_phone_numbers
            )
        )
        return player_messages


@attr.s
class NotifyTribalChallengeEvent(SMSEvent):
    challenge: Challenge = attr.ib()

    def challenge_submission_link(self) -> Text:
        pass

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyTribalChallengeEvent(
            game_id=json_dict['game_id'],
            game_options=json_dict['game_options'],
            challenge=Challenge.from_dict(json_dict['challenge']),
        )

    def messages(self, gamedb: Database) -> List[SMSEventMessage]:
        player_messages = []
        players = gamedb.stream_players(active_player_predicate_value=True)
        # TODO(brandon): parallelize
        # NOTE(brandon) this is going to be problematic at scale. we're sending personalized links to
        # every player in the game, which costs 1 API call / player within Twilio. If we can make these links
        # standard then a single Notify API call can address all users in a single game. Non-critical for MVP.
        for player in players:
            player_messages.append(
                SMSEventMessage(
                    content=messages.NOTIFY_TRIBAL_CHALLENGE_EVENT_MSG_FMT.format(
                        header=messages.VIR_US_SMS_HEADER,
                        challenge=self.challenge.name,
                        # TODO(brandon) refactor into common routes location
                        link="https://{hostname}/challenge-submission/{player_id}/{game_id}/{challenge_id}".format(
                            hostname=messages.VIR_US_HOSTNAME,
                            game_id=self.game_id,
                            player_id=player.id,
                            challenge_id=self.challenge.id
                        ),
                        time=self.game_options.game_schedule.localized_time_string(
                            self.game_options.game_schedule.daily_challenge_end_time
                        )
                    ),
                    recipient_phone_numbers=[player.phone_number]
                ))
        return player_messages


@attr.s
class NotifyMultiTribeCouncilEvent(SMSEvent):
    winning_tribe: Tribe = attr.ib()
    losing_tribe: Tribe = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyMultiTribeCouncilEvent(
            game_id=json_dict['game_id'],
            game_options=json_dict['game_options'],
            winning_tribe=Tribe.from_dict(json_dict['winning_tribe']),
            losing_tribe=Tribe.from_dict(json_dict['losing_tribe']),
        )

    def message_content(self, gamedb: Database) -> Text:
        pass

    def messages(self, gamedb: Database) -> List[SMSEventMessage]:
        player_messages = []
        losing_teams = gamedb.stream_teams(from_tribe=self.losing_tribe)
        winning_teams = gamedb.stream_teams(from_tribe=self.winning_tribe)

        for team in losing_teams:
            losing_players = []

            # TODO(brandon): optimize this.
            for player in gamedb.list_players(from_team=team):
                losing_players.append(player)

            options_map = messages.players_as_formatted_options_map(
                players=losing_players)

            for player in losing_players:
                gamedb.ballot(
                    player_id=player.id, options=options_map.options, challenge_id=None
                )

            # NOTE: UX isn't perfect here because we'll show the player's own name
            # as an option to vote out. For MVP this helps with scale because the alternative
            # requires sending a different message to every player (as opposed to every team)
            # which is about a 5x cost increase for SMS.
            player_messages.append(
                SMSEventMessage(
                    content=messages.NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_LOSING_MSG_FMT.format(
                        header=messages.VIR_US_SMS_HEADER,
                        tribe=self.losing_tribe.name,
                        time=self.game_options.game_schedule.localized_time_string(
                            self.game_options.game_schedule.daily_tribal_council_end_time
                        ),
                        options=options_map.formatted_string
                    ),
                    recipient_phone_numbers=[
                        p.phone_number for p in losing_players]
                )
            )

        winning_player_phone_numbers = []
        for team in winning_teams:
            winning_players = gamedb.list_players(from_team=team)
            winning_player_phone_numbers.extend(
                [p.phone_number for p in winning_players]
            )

        player_messages.append(
            SMSEventMessage(
                content=messages.NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_WINNING_MSG_FMT.format(
                    header=messages.VIR_US_SMS_HEADER,
                    winning_tribe=self.winning_tribe.name,
                    losing_tribe=self.losing_tribe.name,
                    time=self.game_options.game_schedule.localized_time_string(
                        self.game_options.game_schedule.daily_tribal_council_end_time
                    ),
                    challenge_time=self.game_options.game_schedule.localized_time_string(
                        self.game_options.game_schedule.daily_challenge_start_time
                    )
                ),
                recipient_phone_numbers=winning_player_phone_numbers
            )
        )
        return player_messages


@attr.s
class NotifyFinalTribalCouncilEvent(SMSEvent):
    finalists: List[Player] = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyFinalTribalCouncilEvent(
            game_id=json_dict['game_id'],
            game_options=json_dict['game_options'],
            finalists=[Player.from_dict(v)
                       for v in json_dict['finalists']]
        )

    def message_content(self, gamedb: Database) -> Text:
        pass

    def messages(self, gamedb: Database) -> List[SMSEventMessage]:
        options_map = messages.players_as_formatted_options_map(
            players=self.finalists)
        # TODO(brandon): this is slow and expensive, but it should work.
        for player in gamedb.stream_players():
            gamedb.ballot(
                player_id=player.id,
                challenge_id=None,
                options=options_map.options,
                is_for_win=True
            )
        return [
            SMSEventMessage(
                content=messages.NOTIFY_FINAL_TRIBAL_COUNCIL_EVENT_MSG_FMT.format(
                    header=messages.VIR_US_HOSTNAME,
                    players=len(self.finalists),
                    game=gamedb.game_from_id(id=self.game_id).hashtag,
                    time=self.game_options.game_schedule.localized_time_string(
                        self.game_options.game_schedule.daily_tribal_council_end_time
                    ),
                    options=options_map.formatted_string
                ),
                recipient_phone_numbers=[p.phone_number for p in gamedb.stream_players(
                    active_player_predicate_value=True)]
            )
        ]


@attr.s
class NotifyPlayerVotedOutEvent(SMSEvent):
    player: Player = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyPlayerVotedOutEvent(
            game_id=json_dict['game_id'],
            game_options=json_dict['game_options'],
            player=Player.from_dict(json_dict['player'])
        )

    def message_content(self, gamedb: Database) -> Text:
        pass

    def messages(self, gamedb: Database) -> List[SMSEventMessage]:
        player_messages = []
        team = gamedb.team_from_id(id=self.player.team_id)
        teammate_phone_numbers = [p.phone_number for p in gamedb.list_players(
            from_team=team) if p.id != self.player.id]
        player_messages.append(
            SMSEventMessage(
                content=messages.NOTIFY_PLAYER_VOTED_OUT_TEAM_MSG_FMT.format(
                    header=messages.VIR_US_SMS_HEADER,
                    player=messages.format_tiktok_username(
                        self.player.tiktok),
                    time=self.game_options.game_schedule.localized_time_string(
                        self.game_options.game_schedule.daily_challenge_start_time
                    )),
                recipient_phone_numbers=teammate_phone_numbers
            )
        )
        player_messages.append(
            SMSEventMessage(
                content=messages.NOTIFY_PLAYER_VOTED_OUT_MSG_FMT.format(
                    header=messages.VIR_US_SMS_HEADER
                ),
                recipient_phone_numbers=[self.player.phone_number]
            )
        )
        return player_messages


@attr.s
class NotifyTribalCouncilCompletionEvent(SMSEvent):

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyTribalCouncilCompletionEvent(
            game_id=json_dict['game_id'],
            game_options=json_dict['game_options'])

    def message_content(self, gamedb: Database) -> Text:
        pass

    def messages(self, gamedb: Database) -> List[SMSEventMessage]:
        return [
            SMSEventMessage(
                content=messages.NOTIFY_TRIBAL_COUNCIL_COMPLETION_EVENT_MSG_FMT.format(
                    header=messages.VIR_US_SMS_HEADER,
                    date=self.game_options.game_schedule.tomorrow_localized_string,
                    time=self.game_options.game_schedule.localized_time_string(
                        self.game_options.game_schedule.daily_challenge_start_time
                    )
                ),
                recipient_phone_numbers=[p.phone_number for p in gamedb.stream_players(
                    active_player_predicate_value=True)]
            )
        ]


@attr.s
class NotifyWinnerAnnouncementEvent(SMSEvent):
    winner: Player = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyWinnerAnnouncementEvent(
            game_id=json_dict['game_id'],
            game_options=json_dict['game_options'],
            winner=Player.from_dict(json_dict['winner'])
        )

    def messages(self, gamedb: Database) -> List[SMSEventMessage]:
        game_hashtag = gamedb.game_from_id(id=self.game_id).hashtag
        return [
            SMSEventMessage(
                content=messages.NOTIFY_WINNER_ANNOUNCEMENT_EVENT_WINNER_MSG_FMT.format(
                    header=messages.VIR_US_SMS_HEADER,
                    game=game_hashtag
                ),
                recipient_phone_numbers=[self.winner.phone_number]
            ),
            SMSEventMessage(
                content=messages.NOTIFY_WINNER_ANNOUNCEMENT_EVENT_GENERAL_MSG_FMT.format(
                    header=messages.VIR_US_SMS_HEADER,
                    player=messages.format_tiktok_username(self.winner.tiktok),
                    game=game_hashtag
                ),
                recipient_phone_numbers=[p.phone_number for p in gamedb.stream_players(
                    active_player_predicate_value=False)]
            )
        ]


@attr.s
class NotifyImmunityAwardedEvent(SMSEvent):
    team: Team = attr.ib()

    @classmethod
    def from_dict(cls, json_dict: Dict) -> SMSEvent:
        return NotifyImmunityAwardedEvent(
            game_id=json_dict['game_id'],
            game_options=json_dict['game_options'],
            team=Team.from_dict(json_dict['team'])
        )

    def message_content(self, gamedb: Database) -> Text:
        return messages.NOTIFY_IMMUNITY_AWARDED_EVENT_MSG_FMT.format(
            header=messages.VIR_US_SMS_HEADER,
            date=self.game_options.game_schedule.tomorrow_localized_string,
            time=self.game_options.game_schedule.localized_time_string(
                self.game_options.game_schedule.daily_challenge_start_time
            )
        )

    def messages(self, gamedb: Database) -> List[SMSEventMessage]:
        return [
            SMSEventMessage(
                content=messages.NOTIFY_IMMUNITY_AWARDED_EVENT_MSG_FMT.format(
                    header=messages.VIR_US_SMS_HEADER,
                    date=self.game_options.game_schedule.tomorrow_localized_string,
                    time=self.game_options.game_schedule.localized_time_string(
                        self.game_options.game_schedule.daily_challenge_start_time
                    )
                ),
                recipient_phone_numbers=[
                    p.phone_number for p in gamedb.list_players(from_team=self.team)]
            )
        ]
