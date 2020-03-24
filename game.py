from game_engine.database import Database
from multiprocessing import Process
import attr
import threading
from typing import Any, Iterable, Dict, Text, Tuple, List
import game_engine
from game_engine.events import Event
from game_engine.engine import Engine
from game_engine.database import *
from game_engine import events
import time
import logging
import sys
from queue import Queue


def _unixtime():
    return time.time()


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def _log_message(message):
    logging.info(message)


@attr.s
class GameOptions(object):
    engine_worker_thread_count: int = attr.ib(default=5)
    engine_worker_sleep_interval_sec: int = attr.ib(default=1)
    game_wait_sleep_interval_sec: int = attr.ib(default=30)
    target_finalist_count: int = attr.ib(default=2)
    multi_tribe_min_tribe_size: int = attr.ib(default=10)
    multi_tribe_target_team_size: int = attr.ib(default=5)
    multi_tribe_council_time_sec: int = attr.ib(300)
    multi_tribe_team_immunity_threshold: float = attr.ib(0.1)


class Game(object):

    def __init__(self, options: GameOptions):
        self._options = options
        self._stop = threading.Event()

    def play(self, tribe1: Tribe, tribe2: Tribe) -> List[Player]:
        last_tribe_standing = self._play_multi_tribe(tribe1, tribe2)
        finalists = self._play_single_tribe(last_tribe_standing)
        # TODO(someone): should the finalist game be manual or completely automated
        # for the pick of who win's the money?

    def _play_multi_tribe(self, tribe1: Tribe, tribe2: Tribe) -> Tribe:
        while (tribe1.size() > self._options.multi_tribe_min_tribe_size and
               tribe2.size() > self._options.multi_tribe_min_tribe_size):
            self._wait_for_challenge()
            self._run_challenge()
            self._score_entries()
            self._run_multi_tribe_council()
            self._merge_teams()
        return self._merge_tribes()

    def _play_single_tribe(self, tribe: Tribe) -> List[Player]:
        while tribe.size() >= self._options.target_finalist_count:
            self._wait_for_challenge()
            self._run_challenge()
            self._score_entries()
            self._run_single_tribe_council()
            self._merge_teams()

        # TODO(brandon): return list of all players remaining
        return [Player()]

    def _get_voted_out_player(self, team: Team, gamedb: Database) -> Player:
        team_votes = gamedb.count_votes(from_team=team)
        voted_out_player = sorted(
            team_votes, key=lambda: item[1], reverse=True)[0][0]
        return voted_out_player

    # fraction of teams in losing tribe must vote
    def _run_multi_tribe_council(self, winning_tribe: Tribe, losing_tribe: Tribe, gamedb: Database, engine: Engine):
        teams = gamedb.stream_teams(from_tribe=losing_tribe)

        for team in teams:
            immunity_granted = random.random() < self._options.multi_tribe_immunity_threshold
            if not immunity_granted:
                non_immune_teams.append(team)
            else:
                engine.add_event(ImmunityNotificationEvent(team=team))

        # announce winner and tribal council for losing tribe
        engine.add_event(MultiTribeCouncilAnnouncementEvent(
            winning_tribe=winning_tribe, losing_tribe=losing_tribe))

        tribal_council_start_timestamp = _unixtime()
        gamedb.clear_votes()
        non_immune_teams = list()

        # wait for votes
        while (((_unixtime() - tribal_council_start_timestamp)
                < Game.TRIBAL_COUNCIL_INTERVAL_SEC) and not self._stop.is_set()):
            _log_message("Waiting for tribal council to end.")
            time.sleep(self._options.game_wait_sleep_interval_sec)

        # count votes
        for team in non_immune_teams:
            voted_out_player = self._get_voted_out_player(
                team=team, gamedb=gamedb)
            gamedb.deactivate_player(player=voted_out_player)
            engine.add_event(VotedOutNotificationEvent(player=player))

        # notify all players of what happened at tribal council
        engine.add_event(TribalCouncilCompletedEvent())

    # keep top K teams
    def _run_single_tribe_council(self, winning_teams: List[Team], losing_teams: List[Team],
                                  gamedb: Database, engine: Engine):

        # announce winner and tribal council for losing tribe
        engine.add_event(SingleTribeCouncilAnnouncementEvent(
            winning_teams=winning_teams, losing_teams=losing_teams))
        tribal_council_start_timestamp = _unixtime()
        gamdb.reset_all_votes()

        # wait for votes
        while (((_unixtime() - tribal_council_start_timestamp)
                < Game.TRIBAL_COUNCIL_INTERVAL_SEC) and not self._stop.is_set()):
            _log_message("Waiting for tribal council to end.")
            time.sleep(self._options.game_wait_sleep_interval_sec)

        # count votes
        for team in losing_teams:
            voted_out_player = self._get_voted_out_player(
                team=team, gamedb=gamedb)
            gamedb.deactivate_player(player=voted_out_player)
            engine.add_event(VotedOutNotificationEvent(player=player))

        # notify all players of what happened at tribal council
        engine.add_event(TribalCouncilCompletedEvent())

    def _merge_teams(self, target_team_size: int, tribe: Tribe, gamedb: Database, engine: Engine):
        # team merging is only necessary when the size of the team == 2
        # once a team size == 2, it should be merged with another team. the optimal
        # choice is to keep team sizes as close to the intended size as possible

        # find all teams with size = 2, these players need to be merged
        small_teams = gamedb.stream_teams(
            from_tribe=tribe, team_size_predicate_value=2)
        merge_candidates = Queue()

        for team in small_teams:
            _log_message("Deactivating team {}.".format(team))
            gamedb.deactivate_team(team)
            
            for player in gamedb.list_players(from_team=team):
                _log_message("Found merge candidate {}.".format(player))
                merge_candidates.put(player)

        sorted_teams = gamedb.stream_teams(
            from_tribe=tribe, order_by_size=True, descending=False)

        # round robin redistribution strategy
        # simplest case, could use more thought.
        visited = {}
        while not merge_candidates.empty():
            for team in sorted_teams:
                other_options_available = team.id not in visited
                visited[team.id] = True

                if (team.size >= target_team_size and other_options_available):
                    continue

                player = merge_candidates.get()
                _log_message("Merging player {} from team {} into team {}.".format(
                    player, player.team_id, team.id))
                player.team_id = team.id
                gamedb.save(player)

                # notify player of new team assignment
                engine.add_event(events.NotifyTeamReassignmentEvent(player=player,
                                                                    team=team))
                                                                    
    def _get_challenge(self, gamedb: Database) -> Challenge:
        available_challenges = gamedb.list_challenges(
            challenge_completed_predicate_value=False)
        return available_challenges[0]

    def _run_challenge(self, challenge: Challenge, engine: Engine):
        # wait for challenge to begin
        while (_unixtime() < challenge.start_timestamp) and not self._stop.is_set():
            _log_message("Waiting {}s for challenge to {} to begin.".format(
                challenge.start_timestamp - _unixtime(), challenge))
            time.sleep(self._options.game_wait_sleep_interval_sec)

        # notify players
        engine.add_event(
            events.NotifyTribalChallengeEvent(challenge=challenge))

        # wait for challenge to end
        while (_unixtime() < challenge.end_timestamp) and not self._stop.is_set():
            _log_message("Waiting {}s for challenge to {} to end.".format(
                challenge.end_timestamp - _unixtime(), challenge))
            time.sleep(self._options.game_wait_sleep_interval_sec)

    def _score_entries(self, tribe: Tribe, challenge: Challenge, gamedb: Database, engine: Engine):
        # trivial scorer for now.
        score = 0
        players = gamedb.count_players(from_tribe=tribe)
        entries = gamedb.stream_entries(
            from_tribe=tribe, from_challenge=challenge)

        # TODO(someone): parallelize w/ async multiprocess pool
        for entry in entries:
            points = entry.likes / entry.views
            player = gamedb.player_from_id(entry.player_id)
            engine.add_event(events.NotifyPlayerScoreEvent(
                player=player, challenge=challenge,
                entry=entry, points=points))
            score = score + points

        # tribe score = avg score of all tribe members
        return score / players

    def _merge_tribes(self, tribe1: Tribe, tribe2: Tribe, new_tribe_name: Text, gamedb: Database) -> Tribe:
        new_tribe = gamedb.tribe(name=new_tribe_name)
        gamedb.batch_update_tribe(from_tribe=tribe1, to_tribe=new_tribe)
        gamedb.batch_update_tribe(from_tribe=tribe2, to_tribe=new_tribe)
        return new_tribe
