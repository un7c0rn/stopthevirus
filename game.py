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
import random
import pprint
import heapq

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
    target_team_size: int = attr.ib(default=5)
    target_finalist_count: int = attr.ib(default=2)
    single_tribe_council_time_sec: int = attr.ib(300)
    multi_tribe_min_tribe_size: int = attr.ib(default=10)
    multi_tribe_target_team_size: int = attr.ib(default=5)
    multi_tribe_council_time_sec: int = attr.ib(300)
    multi_tribe_team_immunity_likelihood: float = attr.ib(0.0)
    merge_tribe_name: Text = attr.ib(default='A$APMOB')
    single_tribe_top_k_threshold: float = attr.ib(default=0.5)


class Game(object):

    def __init__(self, options: GameOptions):
        self._options = options
        self._stop = threading.Event()

    def play(self, tribe1: Tribe, tribe2: Tribe, gamedb: Database, engine: Engine) -> List[Player]:
        last_tribe_standing = self._play_multi_tribe(tribe1=tribe1, tribe2=tribe2,
                                                     gamedb=gamedb, engine=engine)
        finalists = self._play_single_tribe(
            tribe=last_tribe_standing, gamedb=gamedb, engine=engine)
        _log_message("The finalists are {}.".format(pprint.pformat(finalists)))

    def _play_multi_tribe(self, tribe1: Tribe, tribe2: Tribe, gamedb: Database, engine: Engine) -> Tribe:
        while (tribe1.size > self._options.multi_tribe_min_tribe_size and
               tribe2.size > self._options.multi_tribe_min_tribe_size):
            challenge = self._get_challenge(gamedb=gamedb)
            self._run_challenge(challenge=challenge, engine=engine)
            tribe1_score = self._score_entries_tribe_aggregate(tribe=tribe1, challenge=challenge,
                                               gamedb=gamedb, engine=engine)
            tribe2_score = self._score_entries_tribe_aggregate(tribe=tribe2, challenge=challenge,
                                               gamedb=gamedb, engine=engine)

            if tribe1_score > tribe2_score:
                winning_tribe = tribe1
                losing_tribe = tribe2
            else:
                winning_tribe = tribe2
                losing_tribe = tribe1

            self._run_multi_tribe_council(winning_tribe=winning_tribe, losing_tribe=losing_tribe,
                                          gamedb=gamedb, engine=engine)
            self._merge_teams(target_team_size=self._options.target_team_size, tribe=losing_tribe,
                              gamedb=gamedb, engine=engine)

        return self._merge_tribes(tribe1=tribe1, tribe2=tribe2, new_tribe_name=self._options.merge_tribe_name,
                                  gamedb=gamedb)

    def _play_single_tribe(self, tribe: Tribe, gamedb: Database, engine: Engine) -> List[Player]:
        while tribe.size >= self._options.target_finalist_count:
            challenge = self._get_challenge(gamedb=gamedb)
            self._run_challenge(challenge=challenge, engine=engine)
            winning_teams, losing_teams = self._score_entries_top_k_teams(k=self._options.single_tribe_top_k_threshold,
                tribe=tribe, challenge=challenge, gamedb=gamedb, engine=engine)
            self._run_single_tribe_council(winning_teams=winning_teams, losing_teams=losing_teams,
                                           gamedb=gamedb, engine=engine)
            self._merge_teams(target_team_size=self._options.target_team_size, tribe=tribe, gamedb=gamedb,
                              engine=engine)

        # TODO(brandon): return list of all players remaining
        return [Player()]

    def _get_voted_out_player(self, team: Team, gamedb: Database) -> [Player, None]:
        team_votes = gamedb.count_votes(from_team=team)
        _log_message("Computed team {} votes {}".format(
            team, pprint.pformat(team_votes)))
        most_voted_player_id = None
        most_votes = 0

        for id, votes in team_votes.items():
            _log_message("Counted {} votes for player {}".format(votes, id))

            # we add the randomization logic here in case there is a tie.
            # if two people have the same highest number of votes, then we
            # leave it to chance.
            if votes > most_votes or (votes == most_votes and random.uniform(0, 1) > 0.5):
                most_voted_player_id = id
                most_votes = votes

        if most_voted_player_id:
            return gamedb.player_from_id(most_voted_player_id)
        else:
            return None

    # fraction of teams in losing tribe must vote
    def _run_multi_tribe_council(self, winning_tribe: Tribe, losing_tribe: Tribe, gamedb: Database, engine: Engine):
        teams = gamedb.stream_teams(from_tribe=losing_tribe)
        non_immune_teams = list()

        for team in teams:
            immunity_granted = random.random() < self._options.multi_tribe_team_immunity_likelihood
            if not immunity_granted:
                non_immune_teams.append(team)
            else:
                engine.add_event(events.NotifyImmunityAwardedEvent(team=team))

        # announce winner and tribal council for losing tribe
        engine.add_event(events.NotifyMultiTribeCouncilEvent(
            winning_tribe=winning_tribe, losing_tribe=losing_tribe))

        tribal_council_start_timestamp = _unixtime()
        gamedb.clear_votes()

        # wait for votes
        while (((_unixtime() - tribal_council_start_timestamp)
                < self._options.multi_tribe_council_time_sec) and not self._stop.is_set()):
            _log_message("Waiting for tribal council to end.")
            time.sleep(self._options.game_wait_sleep_interval_sec)

        # count votes
        for team in non_immune_teams:
            voted_out_player = self._get_voted_out_player(
                team=team, gamedb=gamedb)
            if voted_out_player:
                gamedb.deactivate_player(player=voted_out_player)
                engine.add_event(events.NotifyPlayerVotedOutEvent(
                    player=voted_out_player))

        # notify all players of what happened at tribal council
        engine.add_event(events.NotifyTribalCouncilCompletionEvent())

    # keep top K teams
    def _run_single_tribe_council(self, winning_teams: List[Team], losing_teams: List[Team],
                                  gamedb: Database, engine: Engine):

        # announce winner and tribal council for losing teams
        engine.add_event(events.NotifySingleTribeCouncilEvent(
            winning_teams=winning_teams, losing_teams=losing_teams))
        tribal_council_start_timestamp = _unixtime()
        gamedb.clear_votes()

        # wait for votes
        while (((_unixtime() - tribal_council_start_timestamp)
                < self._options.single_tribe_council_time_sec) and not self._stop.is_set()):
            _log_message("Waiting for tribal council to end.")
            time.sleep(self._options.game_wait_sleep_interval_sec)

        # count votes
        for team in losing_teams:
            voted_out_player = self._get_voted_out_player(
                team=team, gamedb=gamedb)
            if voted_out_player:
                gamedb.deactivate_player(player=voted_out_player)
                _log_message("Deactivated player {}.".format(voted_out_player))
                engine.add_event(events.NotifyPlayerVotedOutEvent(
                    player=voted_out_player))

        # notify all players of what happened at tribal council
        engine.add_event(events.NotifyTribalCouncilCompletionEvent())

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

    def _score_entries_tribe_aggregate(self, tribe: Tribe, challenge: Challenge, gamedb: Database, engine: Engine):
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

    def _score_entries_top_k_teams(self, k: float, tribe: Tribe, challenge: Challenge, gamedb: Database,
        engine: Engine) -> Tuple[List[Team], List[Team]]:
        team_scores = {}
        top_scores = list()
        winning_teams = list()
        losing_teams = list()

        entries = gamedb.stream_entries(
            from_tribe=tribe, from_challenge=challenge)

        # TODO(someone): parallelize w/ async multiprocess pool
        for entry in entries:
            points = entry.likes / entry.views
            player = gamedb.player_from_id(entry.player_id)
            engine.add_event(events.NotifyPlayerScoreEvent(
                player=player, challenge=challenge,
                entry=entry, points=points))

            if player.team_id not in team_scores:
                team_scores[player.team_id] = points
            else:
                team_scores[player.team_id] = team_scores[player.team_id] + points

        for x, v in team_scores.items():
            heapq.heappush(top_scores, (v, x))

        rank_threshold = float(k * len(top_scores))
        for rank, (_, team_id) in enumerate(top_scores):
            if rank <= rank_threshold:
                winning_teams.append(gamedb.team_from_id(team_id))
            else:
                losing_teams.append(gamedb.team_from_id(team_id))

        return (winning_teams, losing_teams)

    def _merge_tribes(self, tribe1: Tribe, tribe2: Tribe, new_tribe_name: Text, gamedb: Database) -> Tribe:
        new_tribe = gamedb.tribe(name=new_tribe_name)
        gamedb.batch_update_tribe(from_tribe=tribe1, to_tribe=new_tribe)
        gamedb.batch_update_tribe(from_tribe=tribe2, to_tribe=new_tribe)
        return new_tribe
