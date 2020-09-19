from game_engine.database import Database
from multiprocessing import Process
import attr
import threading
from typing import Any, Iterable, Dict, Text, Tuple, List
import game_engine
from game_engine.events import SMSEvent
from game_engine.engine import Engine
from game_engine.database import *
from game_engine import events
import time
import logging
import sys
from queue import Queue, Empty
import random
import pprint
import heapq
from game_engine.firestore import FirestoreDB
from concurrent.futures import ThreadPoolExecutor
from game_engine.common import GameError
from game_engine.common import GameClockMode
from game_engine.common import GameOptions
from game_engine.common import log_message
import uuid
import itertools


def _unixtime():
    return time.time()


def _tribe_count_players(tribe: Tribe, gamedb: Database) -> int:
    tribe = gamedb.tribe_from_id(tribe.id)
    return tribe.count_players


def _team_count_players(team: Team, gamedb: Database) -> int:
    team = gamedb.team_from_id(team.id)
    return team.count_players


class Game:
    def __init__(self, game_id: Text, options: GameOptions):
        self._options = options
        self._game_id = game_id
        self._stop_event = threading.Event()
        self._wait_for_game_start_event = threading.Event()
        self._wait_for_tribal_council_start_event = threading.Event()
        self._wait_for_tribal_council_end_event = threading.Event()
        self._wait_for_challenge_start_event = threading.Event()
        self._wait_for_challenge_end_event = threading.Event()

    def play(self, tribe1: Tribe, tribe2: Tribe, gamedb: Database, engine: Engine) -> Player:
        self._wait_for_game_start_time()

        last_tribe_standing = self._play_multi_tribe(tribe1=tribe1, tribe2=tribe2,
                                                     gamedb=gamedb, engine=engine)
        log_message(message="Last tribe standing is {}.".format(
            last_tribe_standing), game_id=self._game_id)
        last_team_standing = self._play_single_tribe(
            tribe=last_tribe_standing, gamedb=gamedb, engine=engine)

        log_message(message="Last team standing is {}.".format(
            last_team_standing), game_id=self._game_id)
        finalists = self._play_single_team(
            team=last_team_standing, gamedb=gamedb, engine=engine)

        log_message(message="Finalists are {}.".format(
            pprint.pformat(finalists)), game_id=self._game_id)
        winner = self._run_finalist_tribe_council(
            finalists=finalists, gamedb=gamedb, engine=engine)

        log_message(message="Winner is {}.".format(
            winner), game_id=self._game_id)
        return winner

    def _play_multi_tribe(self, tribe1: Tribe, tribe2: Tribe, gamedb: Database, engine: Engine) -> Tribe:
        merged_tribe = None
        while (_tribe_count_players(tribe1, gamedb) > self._options.multi_tribe_min_tribe_size and
               _tribe_count_players(tribe2, gamedb) > self._options.multi_tribe_min_tribe_size):
            log_message("Getting new challenge.")
            challenge = self._get_next_challenge(gamedb=gamedb)

            log_message(message="Running challenge {}.".format(
                challenge), game_id=self._game_id)
            self._run_challenge(challenge=challenge,
                                gamedb=gamedb, engine=engine)

            log_message(message="Scoring entries for {}.".format(
                tribe1), game_id=self._game_id)
            tribe1_score = self._score_entries_tribe_aggregate(tribe=tribe1, challenge=challenge,
                                                               gamedb=gamedb, engine=engine)

            log_message(message="Scoring entries for {}.".format(
                tribe2), game_id=self._game_id)
            tribe2_score = self._score_entries_tribe_aggregate(tribe=tribe2, challenge=challenge,
                                                               gamedb=gamedb, engine=engine)

            winning_tribe = tribe1 if tribe1_score > tribe2_score else tribe2
            losing_tribe = tribe1 if winning_tribe == tribe2 else tribe2

            log_message(message="Running multi-tribe council.",
                        game_id=self._game_id)
            self._run_multi_tribe_council(winning_tribe=winning_tribe, losing_tribe=losing_tribe,
                                          gamedb=gamedb, engine=engine)

            log_message(message="Merging teams.", game_id=self._game_id)
            self._merge_teams(target_team_size=self._options.target_team_size, tribe=losing_tribe,
                              gamedb=gamedb, engine=engine)

        return self._merge_tribes(tribe1=tribe1, tribe2=tribe2, new_tribe_name=self._options.merge_tribe_name,
                                  gamedb=gamedb, engine=engine)

    def _play_single_tribe(self, tribe: Tribe, gamedb: Database, engine: Engine) -> Team:
        while gamedb.count_teams(active_team_predicate_value=True) > 1:
            log_message(message="Teams remaining = {}.".format(
                gamedb.count_teams(active_team_predicate_value=True)), game_id=self._game_id)

            log_message("Getting new challenge.")
            challenge = self._get_next_challenge(gamedb=gamedb)

            log_message(message="Running challenge {}.".format(
                challenge), game_id=self._game_id)
            self._run_challenge(challenge=challenge,
                                gamedb=gamedb, engine=engine)

            log_message(message="Scoring entries.", game_id=self._game_id)
            winning_teams, losing_teams = self._score_entries_top_k_teams(k=self._options.single_tribe_top_k_threshold,
                                                                          tribe=tribe, challenge=challenge, gamedb=gamedb, engine=engine)

            log_message(message="Running single tribe council.",
                        game_id=self._game_id)
            self._run_single_tribe_council(winning_teams=winning_teams, losing_teams=losing_teams,
                                           gamedb=gamedb, engine=engine)

            log_message(message="Merging teams.", game_id=self._game_id)
            self._merge_teams(target_team_size=self._options.target_team_size, tribe=tribe, gamedb=gamedb,
                              engine=engine)

        return [team for team in gamedb.list_teams(active_team_predicate_value=True)][0]

    def _play_single_team(self, team: Team, gamedb: Database, engine: Engine) -> List[Player]:
        while _team_count_players(team, gamedb) > self._options.target_finalist_count:
            challenge = self._get_next_challenge(gamedb=gamedb)
            self._run_challenge(challenge=challenge,
                                gamedb=gamedb, engine=engine)
            losing_players = self._score_entries_top_k_players(
                team=team, challenge=challenge, gamedb=gamedb, engine=engine)
            self._run_single_team_council(
                team=team, losing_players=losing_players, gamedb=gamedb, engine=engine)

        return gamedb.list_players(from_team=team)

    def _get_voted_out_player(self, team: Team, gamedb: Database) -> [Player, None]:
        high = 0
        candidates = []
        log_message(message="Counting votes from team {}.".format(
            team), game_id=self._game_id)
        team_votes = gamedb.count_votes(from_team=team)
        log_message(message="Got votes {}.".format(
            pprint.pformat(team_votes)), game_id=self._game_id)

        for _, votes in team_votes.items():
            if votes > high:
                high = votes

        for id, votes in team_votes.items():
            if votes == high:
                candidates.append(id)

        num_candidates = len(candidates)
        if num_candidates == 1:
            return gamedb.player_from_id(candidates[0])
        elif num_candidates > 1:
            return gamedb.player_from_id(candidates[random.randint(0, num_candidates - 1)])
        else:
            raise GameError("Unable to determine voted out player.")

    def set_game_start_event(self) -> None:
        self._wait_for_game_start_event.set()
        self._wait_for_game_start_event.clear()

    def set_tribal_council_start_event(self) -> None:
        self._wait_for_tribal_council_start_event.set()
        self._wait_for_tribal_council_start_event.clear()

    def set_tribal_council_end_event(self) -> None:
        self._wait_for_tribal_council_end_event.set()
        self._wait_for_tribal_council_end_event.clear()

    def set_challenge_start_event(self) -> None:
        self._wait_for_challenge_start_event.set()
        self._wait_for_challenge_start_event.clear()

    def set_challenge_end_event(self) -> None:
        self._wait_for_challenge_end_event.set()
        self._wait_for_challenge_end_event.clear()

    def set_stop_event(self) -> None:
        self._stop_event.set()
        self._stop_event.clear()

    def _wait_for_game_start_time(self) -> None:
        if self._options.game_clock_mode == GameClockMode.SYNC:
            game_start_time_sec = _unixtime() + self._options.game_schedule.localized_time_delta_sec(
                end_time=self._options.game_schedule.game_start_time)
            while((_unixtime() < game_start_time_sec) and not self._stop_event.is_set() and not self._wait_for_game_start_event.is_set()):
                log_message("Waiting until {} for game start.".format(
                    game_start_time_sec))
                time.sleep(self._options.game_wait_sleep_interval_sec)
        elif self._options.game_clock_mode == GameClockMode.ASYNC:
            # start immediately.
            log_message("Initiating game {} with timing mode.".format(
                self._options.game_clock_mode))

    def _wait_for_tribal_council_start_time(self) -> None:
        if self._options.game_clock_mode == GameClockMode.SYNC:
            tribal_council_start_time_sec = _unixtime() + self._options.game_schedule.localized_time_delta_sec(
                end_time=self._options.game_schedule.daily_tribal_council_start_time)
            while((_unixtime() < tribal_council_start_time_sec) and not self._stop_event.is_set() and not self._wait_for_tribal_council_start_event.is_set()):
                log_message("Waiting until {} for tribal council.".format(
                    tribal_council_start_time_sec))
                time.sleep(self._options.game_wait_sleep_interval_sec)
        elif self._options.game_clock_mode == GameClockMode.ASYNC:
            # start immediately.
            log_message("Initiating tribal council in {} game timing mode.".format(
                self._options.game_clock_mode))
            return

    def _wait_for_tribal_council_end_time(self) -> None:
        if self._options.game_clock_mode == GameClockMode.SYNC:
            tribal_council_end_time_sec = _unixtime() + self._options.game_schedule.localized_time_delta_sec(
                end_time=self._options.game_schedule.daily_tribal_council_end_time)
            while((_unixtime() < tribal_council_end_time_sec) and not self._stop_event.is_set() and not self._wait_for_tribal_council_start_event.is_set()):
                log_message("Waiting until {} for tribal council.".format(
                    tribal_council_end_time_sec))
                time.sleep(self._options.game_wait_sleep_interval_sec)
        elif self._options.game_clock_mode == GameClockMode.ASYNC:
            tribal_council_start_timestamp = _unixtime()
            while (((_unixtime() - tribal_council_start_timestamp)
                    < self._options.tribe_council_time_sec) and not self._stop_event.is_set() and not self._wait_for_tribal_council_end_event.is_set()):
                log_message("Waiting for tribal council to end.")
                time.sleep(self._options.game_wait_sleep_interval_sec)

    def _wait_for_challenge_start_time(self, challenge: Challenge) -> None:
        if self._options.game_clock_mode == GameClockMode.SYNC:
            challenge_start_time_sec = _unixtime() + self._options.game_schedule.localized_time_delta_sec(
                end_time=self._options.game_schedule.daily_challenge_start_time)
            while((_unixtime() < challenge_start_time_sec) and not self._stop_event.is_set() and not self._wait_for_challenge_start_event.is_set()):
                log_message("Waiting until {} for daily challenge start.".format(
                    challenge_start_time_sec))
                time.sleep(self._options.game_wait_sleep_interval_sec)
        elif self._options.game_clock_mode == GameClockMode.ASYNC:
            log_message(
                f"Waiting {self._options.game_wait_sleep_interval_sec}s for challenge to {str(challenge)} to begin...")
            time.sleep(self._options.game_wait_sleep_interval_sec)

    def _wait_for_challenge_end_time(self, challenge: Challenge) -> None:
        if self._options.game_clock_mode == GameClockMode.SYNC:
            challenge_end_time_sec = _unixtime() + self._options.game_schedule.localized_time_delta_sec(
                end_time=self._options.game_schedule.daily_challenge_end_time)
            while not self._stop_event.is_set() and not self._wait_for_challenge_end_event.is_set():
                log_message("Waiting until {} for daily challenge start.".format(
                    challenge_end_time_sec))
                time.sleep(self._options.game_wait_sleep_interval_sec)
        elif self._options.game_clock_mode == GameClockMode.ASYNC:
            log_message(
                f"Waiting {self._options.game_wait_sleep_interval_sec}s for challenge to {str(challenge)} to end...")
            time.sleep(self._options.game_wait_sleep_interval_sec)

    def _run_multi_tribe_council(self, winning_tribe: Tribe, losing_tribe: Tribe, gamedb: Database, engine: Engine):
        self._wait_for_tribal_council_start_time()

        # fraction of teams in losing tribe must vote
        non_immune_teams = list()
        for team in gamedb.stream_teams(from_tribe=losing_tribe):
            log_message(message="Found losing team {}.".format(
                team), game_id=self._game_id)
            immunity_granted = random.random() < self._options.multi_tribe_team_immunity_likelihood
            if not immunity_granted:
                non_immune_teams.append(team)
            else:
                engine.add_event(events.NotifyImmunityAwardedEvent(
                    game_id=self._game_id, game_options=self._options, team=team))

        # announce winner and tribal council for losing tribe
        gamedb.clear_votes()
        engine.add_event(events.NotifyMultiTribeCouncilEvent(game_id=self._game_id, game_options=self._options,
                                                             winning_tribe=winning_tribe, losing_tribe=losing_tribe))
        self._wait_for_tribal_council_end_time()

        # count votes
        for team in non_immune_teams:
            log_message(
                message="Counting votes for non-immune team {}.".format(team), game_id=self._game_id)
            voted_out_player = self._get_voted_out_player(
                team=team, gamedb=gamedb)
            if voted_out_player:
                gamedb.deactivate_player(player=voted_out_player)
                log_message(message="Deactivated player {}.".format(
                    voted_out_player), game_id=self._game_id)
                engine.add_event(events.NotifyPlayerVotedOutEvent(game_id=self._game_id, game_options=self._options,
                                                                  player=voted_out_player))

        # notify all players of what happened at tribal council
        engine.add_event(events.NotifyTribalCouncilCompletionEvent(
            game_id=self._game_id, game_options=self._options))

    def _run_single_tribe_council(self, winning_teams: List[Team], losing_teams: List[Team],
                                  gamedb: Database, engine: Engine):
        self._wait_for_tribal_council_start_time()
        # keep top K teams

        # announce winner and tribal council for losing teams
        gamedb.clear_votes()
        engine.add_event(events.NotifySingleTribeCouncilEvent(
            game_id=self._game_id, game_options=self._options,
            winning_teams=winning_teams, losing_teams=losing_teams))
        self._wait_for_tribal_council_end_time()

        # count votes
        for team in losing_teams:
            voted_out_player = self._get_voted_out_player(
                team=team, gamedb=gamedb)
            if voted_out_player:
                gamedb.deactivate_player(player=voted_out_player)
                log_message(message="Deactivated player {}.".format(
                    voted_out_player), game_id=self._game_id)
                engine.add_event(events.NotifyPlayerVotedOutEvent(game_id=self._game_id, game_options=self._options,
                                                                  player=voted_out_player))
            else:
                log_message(
                    message="For some reason no one got voted out...", game_id=self._game_id)
                log_message(message="Players = {}.".format(
                    pprint.pformat(gamedb.list_players(from_team=team))), game_id=self._game_id)

        # notify all players of what happened at tribal council
        engine.add_event(
            events.NotifyTribalCouncilCompletionEvent(game_id=self._game_id, game_options=self._options))

    def _run_single_team_council(self, team: Team, losing_players: List[Player], gamedb: Database, engine: Engine):
        self._wait_for_tribal_council_start_time()

        # announce winner and tribal council for losing teams
        gamedb.clear_votes()

        winning_players = [player for player in gamedb.list_players(
            from_team=team) if player not in losing_players]
        if len(winning_players) > 0:
            winning_player = winning_players[0]
        else:
            engine.stop()
            raise GameError(
                "Unable to determine a winning player for the challenge. Have any entries been submitted?")

        engine.add_event(events.NotifySingleTeamCouncilEvent(game_id=self._game_id, game_options=self._options,
                                                             winning_player=winning_player, losing_players=losing_players))
        self._wait_for_tribal_council_end_time()

        # count votes
        voted_out_player = self._get_voted_out_player(
            team=team, gamedb=gamedb)
        if voted_out_player:
            gamedb.deactivate_player(player=voted_out_player)
            log_message(message="Deactivated player {}.".format(
                voted_out_player), game_id=self._game_id)
            engine.add_event(events.NotifyPlayerVotedOutEvent(game_id=self._game_id, game_options=self._options,
                                                              player=voted_out_player))

        # notify all players of what happened at tribal council
        engine.add_event(
            events.NotifyTribalCouncilCompletionEvent(game_id=self._game_id, game_options=self._options))

    def _run_finalist_tribe_council(self, finalists: List[Player], gamedb: Database, engine: Engine) -> Player:
        gamedb.clear_votes()
        self._wait_for_tribal_council_start_time()

        engine.add_event(
            events.NotifyFinalTribalCouncilEvent(
                game_id=self._game_id, game_options=self._options, finalists=finalists))
        self._wait_for_tribal_council_end_time()

        # count votes
        player_votes = gamedb.count_votes(is_for_win=True)
        max_votes = 0
        winner = None

        for player_id, votes in player_votes.items():
            if votes > max_votes:
                max_votes = votes
                winner = gamedb.player_from_id(id=player_id)

        # announce winner
        engine.add_event(events.NotifyWinnerAnnouncementEvent(
            game_id=self._game_id, game_options=self._options, winner=winner))
        return winner

    def _merge_teams(self, target_team_size: int, tribe: Tribe, gamedb: Database, engine: Engine):
        with engine:
            # team merging is only necessary when the size of the team == 2
            # once a team size == 2, it should be merged with another team, because
            # a self preservation vote lands in a deadlock. in general, the optimal
            # choice is to keep team sizes as close to the intended size as possible
            # up until a merge becomes necessary.

            # find all teams with size == 2, these players need to be merged
            small_teams = gamedb.stream_teams(
                from_tribe=tribe, team_size_predicate_value=2)
            merge_candidates = Queue()

            for team in small_teams:
                # do not deactivate the last active team in the tribe
                count_teams = gamedb.count_teams(
                    from_tribe=tribe, active_team_predicate_value=True)
                if count_teams > 1:
                    log_message(message="Found team of 2. Deactivating team {}.".format(
                        team), game_id=self._game_id)
                    gamedb.deactivate_team(team)
                for player in gamedb.list_players(from_team=team):
                    log_message(message="Adding merge candidate {}.".format(
                        player), game_id=self._game_id)
                    merge_candidates.put(player)

            sorted_teams = gamedb.stream_teams(
                from_tribe=tribe, order_by_size=True, descending=False)

            log_message(message="Redistributing merge candidates...",
                        game_id=self._game_id)
            # round robin redistribution strategy
            # simplest case, could use more thought.
            visited = {}
            while not merge_candidates.empty() and sorted_teams:
                for team in itertools.cycle(sorted_teams):
                    team.count_players = _team_count_players(team, gamedb)
                    other_options_available = team.id not in visited
                    visited[team.id] = True

                    if (team.count_players >= target_team_size and other_options_available):
                        log_message(message="Team {} has size >= target {} and other options are available. "
                                    "Continuing search...".format(team, target_team_size), game_id=self._game_id)
                        continue

                    player = None
                    try:
                        player = merge_candidates.get_nowait()
                    except Empty:
                        log_message(message="Merge candidates empty.")
                        return

                    if player.team_id == team.id:
                        log_message(
                            message=f"Player {str(player)} already on team {str(team)}. Continuing.")
                        continue

                    log_message(message="Merging player {} from team {} into team {}.".format(
                        player, player.team_id, team.id), game_id=self._game_id)
                    player.team_id = team.id
                    team.count_players += 1
                    gamedb.save(team)
                    gamedb.save(player)

                    # notify player of new team assignment
                    engine.add_event(events.NotifyTeamReassignmentEvent(game_id=self._game_id, game_options=self._options, player=player,
                                                                        team=team))

    def _get_next_challenge(self, gamedb: Database) -> Challenge:
        available_challenge_count = 0
        while available_challenge_count == 0 and not self._stop_event.is_set():
            log_message("Waiting for next challenge to become available.")
            time.sleep(self._options.game_wait_sleep_interval_sec)
            available_challenges = gamedb.list_challenges(
                challenge_completed_predicate_value=False)
            available_challenge_count = len(available_challenges)
        challenge = available_challenges[0]
        # return serializable challenge since this gets placed on the event queue.
        return Challenge(
            id=challenge.id,
            name=challenge.name,
            message=challenge.message,
            complete=challenge.complete
        )

    def _run_challenge(self, challenge: Challenge, gamedb: Database, engine: Engine):
        # wait for challenge to begin
        self._wait_for_challenge_start_time(challenge=challenge)

        # notify players
        engine.add_event(
            events.NotifyTribalChallengeEvent(game_id=self._game_id, game_options=self._options, challenge=challenge))

        # wait for challenge to end
        self._wait_for_challenge_end_time(challenge=challenge)

        challenge.complete = True
        gamedb.save(challenge)

    def _score_entries_tribe_aggregate_fn(self, entries: Iterable, challenge: Challenge, score_dict: Dict, gamedb: Database, engine: Engine):
        """Note that all built-ins are thread safe in python, meaning we can
        atomically increment the score int held in score_dict."""

        entries_iter = iter(entries)
        while not self._stop_event.is_set():
            try:
                entry = next(entries_iter)
                pprint.pprint(entry)
                points = entry.likes / entry.views
                player = gamedb.player_from_id(entry.player_id)
                engine.add_event(events.NotifyPlayerScoreEvent(
                    game_id=self._game_id, game_options=self._options,
                    player=player, challenge=challenge,
                    entry=entry, points=points))
                score_dict['score'] += points
            except StopIteration:
                break

    def _score_entries_tribe_aggregate(self, tribe: Tribe, challenge: Challenge, gamedb: Database, engine: Engine):
        score_dict = {'score': 0}
        players = gamedb.count_players(from_tribe=tribe)
        entries = gamedb.stream_entries(
            from_tribe=tribe, from_challenge=challenge)

        with ThreadPoolExecutor(max_workers=self._options.engine_worker_thread_count) as executor:
            executor.submit(self._score_entries_tribe_aggregate_fn,
                            entries=entries, challenge=challenge, score_dict=score_dict, gamedb=gamedb, engine=engine)

        # tribe score = avg score of all tribe members
        log_message(message="_score_entries_tribe_agg = {}.".format(
            score_dict['score']), game_id=self._game_id)

        if players > 0:
            return score_dict['score'] / players
        return 0

    def _score_entries_top_k_teams_fn(self, entries: Iterable, challenge: Challenge, score_dict: Dict, gamedb: Database, engine: Engine):
        entries_iter = iter(entries)
        while not self._stop_event.is_set():
            try:
                entry = next(entries_iter)
                log_message(message="Entry {}.".format(
                    entry), game_id=self._game_id)
                points = entry.likes / entry.views
                player = gamedb.player_from_id(entry.player_id)
                engine.add_event(events.NotifyPlayerScoreEvent(game_id=self._game_id, game_options=self._options,
                                                               player=player, challenge=challenge,
                                                               entry=entry, points=points))

                if player.team_id not in score_dict:
                    score_dict[player.team_id] = points
                else:
                    score_dict[player.team_id] += points
            except StopIteration:
                break

    def _score_entries_top_k_teams(self, k: float, tribe: Tribe, challenge: Challenge, gamedb: Database,
                                   engine: Engine) -> Tuple[List[Team], List[Team]]:
        team_scores = {}
        top_scores = list()
        winning_teams = list()
        losing_teams = list()

        entries = gamedb.stream_entries(
            from_tribe=tribe, from_challenge=challenge)

        with ThreadPoolExecutor(max_workers=self._options.engine_worker_thread_count) as executor:
            executor.submit(self._score_entries_top_k_teams_fn,
                            entries=entries, challenge=challenge, score_dict=team_scores, gamedb=gamedb, engine=engine)

        for team_id, score in team_scores.items():
            heapq.heappush(top_scores, (score / gamedb.count_players(from_team=gamedb.team_from_id(team_id)),
                                        team_id))

        rank_threshold = float(k * len(top_scores))
        log_message(message="Rank threshold = {}".format(
            rank_threshold), game_id=self._game_id)

        # note that the default python heap pops in ascending order,
        # so the rank here is actually worst to best.
        num_scores = len(top_scores)
        if num_scores == 1:
            score, team_id = heapq.heappop(top_scores)
            log_message(message="Winner {}.".format(
                team_id), game_id=self._game_id)
            winning_teams = [gamedb.team_from_id(team_id)]
        else:
            for rank in range(num_scores):
                score, team_id = heapq.heappop(top_scores)
                log_message(message="Team {} rank {} with score {}.".format(
                    team_id, rank, score), game_id=self._game_id)
                if rank >= rank_threshold:
                    log_message(message="Winner {}.".format(
                        team_id), game_id=self._game_id)
                    winning_teams.append(gamedb.team_from_id(team_id))
                else:
                    log_message(message="Loser {}.".format(
                        team_id), game_id=self._game_id)
                    losing_teams.append(gamedb.team_from_id(team_id))

        return (winning_teams, losing_teams)

    def _score_entries_top_k_players_fn(self, entries: Iterable, challenge: Challenge, score_dict: Dict, gamedb: Database, engine: Engine):
        entries_iter = iter(entries)
        while not self._stop_event.is_set():
            try:
                entry = next(entries_iter)
                log_message(message="Entry {}.".format(
                    entry), game_id=self._game_id)
                points = entry.likes / entry.views
                player = gamedb.player_from_id(entry.player_id)
                engine.add_event(events.NotifyPlayerScoreEvent(game_id=self._game_id, game_options=self._options,
                                                               player=player, challenge=challenge,
                                                               entry=entry, points=points))
                score_dict[player.id] = points
            except StopIteration:
                break

    def _score_entries_top_k_players(self, team: Team, challenge: Challenge, gamedb: Database, engine: Engine) -> List[Player]:
        player_scores = {}
        top_scores = list()
        losing_players = list()
        winning_player_ids = set()
        entries = gamedb.stream_entries(
            from_team=team, from_challenge=challenge)

        with ThreadPoolExecutor(max_workers=self._options.engine_worker_thread_count) as executor:
            executor.submit(self._score_entries_top_k_players_fn,
                            entries=entries, challenge=challenge, score_dict=player_scores, gamedb=gamedb, engine=engine)

        for player_id, score in player_scores.items():
            heapq.heappush(top_scores, (score, player_id))

        # note that the default python heap pops in ascending order,
        # so the rank here is actually worst to best.
        num_scores = len(top_scores)
        if num_scores == 1:
            raise GameError(
                "Unable to rank losing players with team size = 1.")
        else:
            for rank in range(num_scores):
                score, player_id = heapq.heappop(top_scores)
                log_message(message="Player {} rank {} with score {}.".format(
                    player_id, rank, score), game_id=self._game_id)

                # all but the highest scorer lose
                if rank < (num_scores - 1):
                    losing_players.append(gamedb.player_from_id(player_id))
                else:
                    winning_player_ids.add(player_id)

        # players that did not score also lose.
        losing_player_ids = set([p.id for p in losing_players])
        for player in gamedb.list_players(from_team=team):
            if (player.id not in losing_player_ids) and (player.id not in winning_player_ids):
                losing_players.append(player)
        return losing_players

    def _merge_tribes(self, tribe1: Tribe, tribe2: Tribe, new_tribe_name: Text, gamedb: Database, engine: Engine) -> Tribe:
        log_message(message=f"Merging tribes into {new_tribe_name}.")
        with engine:
            new_tribe = gamedb.tribe(name=new_tribe_name)
            gamedb.batch_update_tribe(from_tribe=tribe1, to_tribe=new_tribe)
            gamedb.batch_update_tribe(from_tribe=tribe2, to_tribe=new_tribe)
            # after tribes merge, sweep the teams to ensure no size of 2
            self._merge_teams(target_team_size=self._options.target_team_size, tribe=new_tribe,
                              gamedb=gamedb, engine=engine)
            game = gamedb.game_from_id(gamedb.get_game_id())
            game.count_tribes = 1
            gamedb.save(game)
            return new_tribe
