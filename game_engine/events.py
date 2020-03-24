import attr
from game_engine.database import Player, Challenge, Entry, Team, Tribe
from typing import Iterable


class Event(object):
    def handle(self):
        pass


class EventQueue(object):
    def put(self, event: Event):
        pass

    def get(self) -> Event:
        return Event()


@attr.s
class NotifyPlayerScoreEvent(Event):
    player: Player = attr.ib()
    challenge: Challenge = attr.ib()
    entry: Entry = attr.ib()
    points: int = attr.ib()


@attr.s
class NotifyTribalChallengeEvent(Event):
    challenge: Challenge = attr.ib()


@attr.s
class NotifyTeamReassignmentEvent(Event):
    player: Player = attr.ib()
    team: Team = attr.ib()


@attr.s
class NotifySingleTribeCouncilEvent(Event):
    winning_teams: Iterable[Team] = attr.ib()
    losing_teams: Iterable[Team] = attr.ib()


@attr.s
class NotifyMultiTribeCouncilEvent(Event):
    winning_tribe: Tribe = attr.ib()
    losing_tribe: Tribe = attr.ib()

@attr.s
class NotifyPlayerVotedOutEvent(Event):
    player: Player = attr.ib()

@attr.s
class NotifyTribalCouncilCompletionEvent(Event):
    pass

@attr.s
class NotifyImmunityAwardedEvent(Event):
    team: Team = attr.ib()

# class Event(object):
#     # Event objects each have handlers. a handler expects a game object
#     # which contains game state and configuration information. The handler
#     # returns an updated game object and a list of any new events to add
#     # to the queue for processing.
#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#         engine_lib.log_message("Handling {} {}".format(type(self).__name__, str(self)))

# class InputEvent(Event):
#     pass

# class OutputEvent(Event):
#     pass

# @attr.s
# class UserErrorEvent(Event):
#     message: Text = attr.ib()
#     email: Text = attr.ib()

#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#         pass

# @attr.s
# class NewPlayerEvent(InputEvent):
#     player: Player = attr.ib()

#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#         super().handle(game)
#         events = list()

#         # New player events received during tribal council are placed back on the input event queue.
#         if game.is_in_tribal_council:
#             engine_lib.log_message("Player {} attempting to join during tribal council.".format(self.player))
#             return (game, [self, UserErrorEvent(message="You must wait until tribal council ends "
#             "in order to join the game!", email=self.player.email)])

#         # When a NewPlayer event is received, the game engine creates an entry in GameDB.
#         if game.is_enrollment_open:
#             engine_lib.log_message("Player {} enrolled in game.".format(self.player))
#             game.create_player(self.player)
#         else:
#             # NewPlayer events are only valid during the valid entry window. After the
#             # entry deadline, all NewPlayer events are ignored.
#             player_count = game.player_count
#             engine_lib.log_message("Maximum number of players reached {}.".format(player_count))
#             events.append(UserErrorEvent(message=("We've reached the maximum number of players ({}). "
#             "Please check again later.").format(player_count), email=self.player.email))
#             return (game, events)

#         # If a team is specified for the player, the player is placed on that team.
#         # Otherwise, the algorithm finds a team and associates the player with that team in the DB. A new
#         # team assignment event is placed on the output queue.
#         if not self.player.is_on_team:
#             team = game.find_team(self.player)
#             engine_lib.log_message("Algorithm identified team {} for player {}.".format(team, self.player))
#             self.player.team_id = team.id
#             self.player.save()
#             events.append(NewTeamAssignmentEvent(player=self.player, team=team))
#             return (game, events)

# @attr.s
# class ChallengeCreatedEvent(InputEvent):
#     challenge: Challenge = attr.ib()

#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#         super().handle(game)
#         events = list()

#         # When a NewChallengeCreation event is received, the game engine creates an entry in
#         # GameDB.
#         engine_lib.log_message("Created new challenge {}.".format(self.challenge))
#         game.create_challenge(self.challenge)

#         # The NewChallengeCreation event must contain information that indicates when
#         # the challenge starts, when the challenge should be announced, and when the deadline
#         # for entry ends. All rules pertaining to the challenge must be included in the description.
#         # When NewChallengeCreation events are received and are validated, the game engine creates a
#         # NewChallengeAnnouncement and places it on the output queue.
#         events.append(NewChallengeAnnouncement(challenge=self.challenge))
#         return (game, [events])

#         # The notification service is
#         # responsible for dequeuing the output event and making all participants aware of the daily
#         # challenge information. In addition, the notification service must post new challenge
#         # information to the web front end. New challenges should never be announced until the
#         # completion of the tribal council associated with the previous challenge. The notification
#         # service must wait for all VotedOutNotifications to be processed before sending a
#         # NewChallengeAnnouncement. NewChallengeAnnouncements are sent to all active players.

# @attr.s
# class VoteToKickOffEvent(InputEvent):
#     vote: Vote = attr.ib()

#     def _is_valid_vote(self, game):
#         team_x = game.get_team(self.vote.from_id)
#         team_y = game.get_team(self.vote.to_id)
#         return team_x == team_y

#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#         super().handle(game)

#         # NewVoteOut events are ignored if the game engine state is not in tribal council state.
#         # Tribal council state is controlled by the game clock. The game engine decides when to
#         # cut off challenge entries and when to enter tribal council state. Voting Ceremony states
#         # are synonymous with tribal challenge winner announcements. In other words, saying “BLUE
#         # TRIBE WINS!” is the same as saying “RED TRIBE HAS TRIBAL COUNCIL!”.
#         if game.is_in_tribal_council:
#             if not self._is_valid_vote(game):
#                 engine_lib.log_message("Ignoring non-team vote {}".format(self.vote))
#                 voter = game.get_player(self.vote.from_id)
#                 recipient = game.get_player(self.vote.to_id)
#                 return (game, [UserErrorEvent(message="You must vote out a member of your team."
#                 " {} is not on your team.".format(recipient.name), email=voter.email)])
#             else:
#                 engine_lib.log_message("Entered tribal council vote {}".format(self.vote))
#                 game.create_vote(self.vote)

#         else:
#             engine_lib.log_message("Ignored non-tribal council vote {}".format(self.vote))


# class VoteToWinEvent(InputEvent):
#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#     #     NewVoteWin events are ignored if the game engine state is not in finalist state. Once the
#     # game engine enters the finalist state, all players that have ever played the game are allowed
#     # to vote for their favorite finalist. The game engine records NewVoteWin events for each
#     # finalist in the gamedb. The final winner announcement will be made manually via Instagram
#     # live by inspecting the database logs on the final day of the challenge
#         pass

# class ChallengeEntrySubmissionEvent(InputEvent):
#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#     # When a NewChallengeEntrySubmission event is received, the game engine identifies the head
#     # to head opponent and verifies that both submissions have been received. It also ensures that
#     # both entries have been available for at least 1 hour. It scores the entries using the following
#     # tentative formula: score = likes / views. This normalizes entries to control for time and
#     # popularity. We want to reduce the effects of celebrity status on the ability to win. The
#     # metrics such as likes, views, etc. are included in the NewChallengeEntrySubmission event from
#     # the scraping service (5). The scraping service is a highly parallelized group of jobs that
#     # continuously check for #STOPTHEVIRUS posts. All posts are submitted to the input event queue
#     # as challenge entries. Posts by non-participants, or duplicate posts, are ignored by the game
#     # engine. The way to enter a challenge is simply to post to Instagram using the hashtag
#     # #STOPTHEVIRUS and to be a registered participant. Posts should tag the @stopthevirus IG
#     # account to spread awareness of the game and objective. After all entries are scored and
#     # the winning tribe is computed, a NewTribalCouncilAnnouncement is placed on the output queue.
#     # The notification system uses these events to announce the winning tribe and to let the losing
#     # tribe know when the tribal council voting window opens. Tribal council voting windows are open
#     # for 4 hours.
#         pass

# @attr.s
# class NewTeamAssignmentEvent(OutputEvent):
#     player: Player = attr.ib()
#     team: Team = attr.ib()

#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#         pass

# class NewChallengeAnnouncement(OutputEvent):
#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#         pass

# @attr.s
# class ScoreEvent(OutputEvent):
#     player: Player = attr.ib()
#     entry: ChallengeEntry = attr.ib()
#     points: int = attr.ib()

#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#         pass

# @attr.s
# class VotedOutNotificationEvent(OutputEvent):
#     player: Player = attr.ib

#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#         pass

# @attr.s
# class ImmunityNotificationEvent(OutputEvent):
#     team: Team = attr.ib()


# @attr.s
# class MultiTribeCouncilAnnouncementEvent(OutputEvent):
#     winning_tribe: Tribe
#     losing_tribe: Tribe

#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#         pass

# @attr.s
# class SingleTribeCouncilAnnouncementEvent(OutputEvent):
#     winning_teams: List[Team] = attr.ib()
#     losing_teams: List[Team] = attr.ib()

#     def handle(self, game: Game) -> Tuple[Game, List[Event]]:
#         pass

# @attr.s
# class TribalCouncilCompletedEvent(OutputEvent):
#     pass
