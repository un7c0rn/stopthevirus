from engine_lib import GameDB, GameConfig, GameState
from engine_lib import NotificationService
import engine_lib
import threading
from typing import Dict, Tuple, List, Text
from abc import ABC
import attr
import logging
from database_lib import Player, Team, Tribe, Challenge, VotingReason
from database_lib import Vote, Database
import json

@attr.s
class Game(Database):
    is_enrollment_open: bool = attr.ib(default=True)

    def find_team(self, player: Player) -> Team:
        # TODO(brandon): implement team finding algorithm for players that don't have a 
        # team. this can also be used for merging, but needs to be fast.
        return Team(id='abcdefg', name='Yaberwalkees')

    @property
    def player_count(self):
        return 0

class Event(object):
    # Event objects each have handlers. a handler expects a game object
    # which contains game state and configuration information. The handler
    # returns an updated game object and a list of any new events to add
    # to the queue for processing.
    def handle(self, game: Game) -> Tuple[Game, List[Event]]:
        engine_lib.log_message("Handling {} {}".format(type(self).__name__, str(self)))

class InputEvent(Event):
    pass

class OutputEvent(Event):
    pass

@attr.s
class UserErrorEvent(Event):
    message: Text = attr.ib()
    email: Text = attr.ib()

    def handle(self, game: Game) -> Tuple[Game, List[Event]]:
        pass

@attr.s
class NewPlayerEvent(InputEvent):
    player: Player = attr.ib()

    def handle(self, game: Game) -> Tuple[Game, List[Event]]:
        super().handle(game)
        events = list()

        # New player events received during tribal council are placed back on the input event queue.
        if game.is_in_tribal_council:
            engine_lib.log_message("Player {} attempting to join during tribal council.".format(self.player))
            return (game, [self, UserErrorEvent(message="You must wait until tribal council ends "
            "in order to join the game!", email=self.player.email)])
        
        # When a NewPlayer event is received, the game engine creates an entry in GameDB.
        if game.is_enrollment_open:
            engine_lib.log_message("Player {} enrolled in game.".format(self.player))
            game.create_player(self.player)
        else:
            # NewPlayer events are only valid during the valid entry window. After the 
            # entry deadline, all NewPlayer events are ignored.
            player_count = game.player_count
            engine_lib.log_message("Maximum number of players reached {}.".format(player_count))
            events.append(UserErrorEvent(message=("We've reached the maximum number of players ({}). "
            "Please check again later.").format(player_count), email=self.player.email))
            return (game, events)

        # If a team is specified for the player, the player is placed on that team.
        # Otherwise, the algorithm finds a team and associates the player with that team in the DB. A new
        # team assignment event is placed on the output queue. 
        if not self.player.is_on_team:
            team = game.find_team(self.player)
            engine_lib.log_message("Algorithm identified team {} for player {}.".format(team, self.player))
            self.player.team_id = team.id
            self.player.save()
            events.append(NewTeamAssignmentEvent(player=self.player, team=team))
            return (game, events)

class ChallengeCreatedEvent(InputEvent):
    def handle(self, game: Game) -> Tuple[Game, List[Event]]:
    # When a NewChallengeCreation event is received, the gamer engine creates an entry in
    # GameDB. The NewChallengeCreation event must contain information that indicates when
    # the challenge starts, when the challenge should be announced, and when the deadline
    # for entry ends. All rules pertaining to the challenge must be included in the description.
    # When NewChallengeCreation events are received and are validated, the game engine creates a
    # NewChallengeAnnouncement and places it on the output queue. The notification service is
    # responsible for dequeuing the output event and making all participants aware of the daily
    # challenge information. In addition, the notification service must post new challenge
    # information to the web front end. New challenges should never be announced until the
    # completion of the tribal council associated with the previous challenge. The notification
    # service must wait for all VotedOutNotifications to be processed before sending a
    # NewChallengeAnnouncement. NewChallengeAnnouncements are sent to all active players.
        pass
    
class VoteToKickOffEvent(InputEvent):
    def handle(self, game: Game) -> Tuple[Game, List[Event]]:
    #     NewVoteOut events are ignored if the game engine state is not in tribal council state.
    # Tribal council state is controlled by the game clock. The game engine decides when to
    # cut off challenge entries and when to enter tribal council state. Voting Ceremony states
    # are synonymous with tribal challenge winner announcements. In other words, saying “BLUE
    # TRIBE WINS!” is the same as saying “RED TRIBE HAS TRIBAL COUNCIL!”.
        pass

class VoteToWinEvent(InputEvent):
    def handle(self, game: Game) -> Tuple[Game, List[Event]]:
    #     NewVoteWin events are ignored if the game engine state is not in finalist state. Once the
    # game engine enters the finalist state, all players that have ever played the game are allowed
    # to vote for their favorite finalist. The game engine records NewVoteWin events for each
    # finalist in the gamedb. The final winner announcement will be made manually via Instagram
    # live by inspecting the database logs on the final day of the challenge
        pass

class ChallengeEntrySubmissionEvent(InputEvent):
    def handle(self, game: Game) -> Tuple[Game, List[Event]]:
    # When a NewChallengeEntrySubmission event is received, the game engine identifies the head
    # to head opponent and verifies that both submissions have been received. It also ensures that
    # both entries have been available for at least 1 hour. It scores the entries using the following
    # tentative formula: score = likes / views. This normalizes entries to control for time and
    # popularity. We want to reduce the effects of celebrity status on the ability to win. The
    # metrics such as likes, views, etc. are included in the NewChallengeEntrySubmission event from
    # the scraping service (5). The scraping service is a highly parallelized group of jobs that
    # continuously check for #STOPTHEVIRUS posts. All posts are submitted to the input event queue
    # as challenge entries. Posts by non-participants, or duplicate posts, are ignored by the game
    # engine. The way to enter a challenge is simply to post to Instagram using the hashtag
    # #STOPTHEVIRUS and to be a registered participant. Posts should tag the @stopthevirus IG
    # account to spread awareness of the game and objective. After all entries are scored and
    # the winning tribe is computed, a NewTribalCouncilAnnouncement is placed on the output queue.
    # The notification system uses these events to announce the winning tribe and to let the losing
    # tribe know when the tribal council voting window opens. Tribal council voting windows are open 
    # for 4 hours.
        pass

@attr.s
class NewTeamAssignmentEvent(OutputEvent):
    player: Player = attr.ib()
    team: Team = attr.ib()

    def handle(self, game: Game) -> Tuple[Game, List[Event]]:
        pass

class NewChallengeAnnouncement(OutputEvent):
    def handle(self, game: Game) -> Tuple[Game, List[Event]]:
        pass

class VotedOutNotificationEvent(OutputEvent):
    def handle(self, game: Game) -> Tuple[Game, List[Event]]:
        pass

class TribalCouncilAnnouncementEvent(OutputEvent):
    def handle(self, game: Game) -> Tuple[Game, List[Event]]:
        pass


class GameEngine(object):
    
    def __init__(self):
        self._gamedb = GameDB()
        self._notifier = NotificationService()
        self._inputq = EventQueue()
        self._state = GameState.IDLE
        self._stop = threading.Event()
        self._logger = Logger()
        self._debug_log = True
        self._config = GameConfig()

    def _log_message(self, message):
        if self._debug_log:
            self._logger.print(message)
    
    def _update_game_state(self, state):
        # TODO(brandon): guarantee atomic
        self._state = state

    def _process_event(self, event: Event, state: GameState) -> Event:
        
        output_event = Event()

        # the enrollment period lasts until the minimum number of players
        # join the game. subsequently, the game begins with a tribal
        # challenge.
        if self._state == GameState.ENROLLMENT or self._state == GameState.IDLE:
            if self._gamedb.count_active_players() >= self._config.min_player_count:
                self._state = GameState.TRIBAL_CHALLENGE
                # TODO(brandon): submit announcement event

        elif self._state == GameState.TRIBAL_CHALLENGE:
            # TODO(brandon): this is a bug because it always gets the next
            # challenge even when a challenge is active. fix.
            challenge = self._gamedb.next_challenge()
            if challenge.expiration_timestamp >= get_unix_timestamp():
                self._state = GameState.SCORING_ENTRIES
                # TODO(brandon): submit announcement event that
                # the challenge deadline has expired.

        elif self._state == GameState.TRIBAL_COUNCIL:
            # TODO(brandon): announce people voted out
            # TODO(brandon): merge small teams
            # TODO(brandon): merge tribes if either tribe size < N
            if self._gamedb.count_active_players() > self._config.final_player_count:
                challenge = self._gamedb.next_challenge()
                if challene.start_timestamp <= get_unix_timestamp():
                    self._state = GameState.TRIBAL_CHALLENGE
            else:
                # TODO(brandon): announce finalists
                self._state = GameState.FINALE

        elif self._state == GameState.SCORING_ENTRIES:
            self._gamedb.count_scores(challenge)
            # TODO(brandon): submit announcement event re: tribal
            # council for the losing tribe, and also announce the
            # winning tribe.
            self._state = GameState.TRIBAL_COUNCIL

        elif self._state == GameState.FINALE:
            pass

        return output_event

    def _background_worker():
        while not self._stop.is_set():
            event = self._inputq.get()
            self._log_message("dequeued event {}".format(event))
            self._process_event(event, self._state)
