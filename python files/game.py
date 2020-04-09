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
from game_engine.firestore import FirestoreDB
from concurrent.futures import ThreadPoolExecutor


def _unixtime():
    return time.time()


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def _log_message(message):
    logging.info(message)


class GameError(Exception):
    pass


# TODO(brandon): update these values for production
_TRIBE_1_ID = ''
_TRIBE_2_ID = ''
_FIRESTORE_PROD_CONF_JSON_PATH = ''


@attr.s
class GameOptions(object):
    engine_worker_thread_count: int = attr.ib(default=5)
    engine_worker_sleep_interval_sec: int = attr.ib(default=1)
    game_wait_sleep_interval_sec: int = attr.ib(default=30)
    target_team_size: int = attr.ib(default=5)
    target_finalist_count: int = attr.ib(default=2)
    single_tribe_council_time_sec: int = attr.ib(300)
    single_team_council_time_sec: int = attr.ib(300)
    final_tribal_council_time_sec: int = attr.ib(300)
    multi_tribe_min_tribe_size: int = attr.ib(default=10)
    multi_tribe_target_team_size: int = attr.ib(default=5)
    multi_tribe_council_time_sec: int = attr.ib(300)
    multi_tribe_team_immunity_likelihood: float = attr.ib(0.0)
    merge_tribe_name: Text = attr.ib(default='a$apmob')
    single_tribe_top_k_threshold: float = attr.ib(default=0.5)


class Game(object):

    def __init__(self, options: GameOptions):
        self._options = options
        self._stop = threading.Event()

    def play(self, tribe1: Tribe, tribe2: Tribe, gamedb: Database, engine: Engine) -> Player:
        last_tribe_standing = self._play_multi_tribe(tribe1=tribe1, tribe2=tribe2,
                                                     gamedb=gamedb, engine=engine)
        _log_message("Last tribe standing is {}.".format(last_tribe_standing))
        last_team_standing = self._play_single_tribe(
            tribe=last_tribe_standing, gamedb=gamedb, engine=engine)

        _log_message("Last team standing is {}.".format(last_team_standing))
        finalists = self._play_single_team(
            team=last_team_standing, gamedb=gamedb, engine=engine)

        _log_message("Finalists are {}.".format(pprint.pformat(finalists)))
        winner = self._run_finalist_tribe_council(
            finalists=finalists, gamedb=gamedb, engine=engine)

        _log_message("Winner is {}.".format(winner))
        return winner

    def _play_multi_tribe(self, tribe1: Tribe, tribe2: Tribe, gamedb: Database, engine: Engine) -> Tribe:
        while (tribe1.size > self._options.multi_tribe_min_tribe_size and
               tribe2.size > self._options.multi_tribe_min_tribe_size):
            _log_message("Tribe {} size {} tribe {} size {}.".format(
                tribe1, tribe1.size, tribe2, tribe2.size))

            _log_message("Getting new challenge.")
            challenge = self._get_challenge(gamedb=gamedb)

            _log_message("Running challenge {}.".format(challenge))
            self._run_challenge(challenge=challenge,
                                gamedb=gamedb, engine=engine)

            _log_message("Scoring entries for {}.".format(tribe1))
            tribe1_score = self._score_entries_tribe_aggregate(tribe=tribe1, challenge=challenge,
                                                               gamedb=gamedb, engine=engine)

            _log_message("Scoring entries for {}.".format(tribe2))
            tribe2_score = self._score_entries_tribe_aggregate(tribe=tribe2, challenge=challenge,
                                                               gamedb=gamedb, engine=engine)

            winning_tribe = tribe1 if tribe1_score > tribe2_score else tribe2
            losing_tribe = tribe1 if winning_tribe == tribe2 else tribe2

            _log_message("Running multi-tribe council.")
            self._run_multi_tribe_council(winning_tribe=winning_tribe, losing_tribe=losing_tribe,
                                          gamedb=gamedb, engine=engine)

            _log_message("Merging teams.")
            self._merge_teams(target_team_size=self._options.target_team_size, tribe=losing_tribe,
                              gamedb=gamedb, engine=engine)

        return self._merge_tribes(tribe1=tribe1, tribe2=tribe2, new_tribe_name=self._options.merge_tribe_name,
                                  gamedb=gamedb)

    def _play_single_tribe(self, tribe: Tribe, gamedb: Database, engine: Engine) -> Team:
        while gamedb.count_teams(active_team_predicate_value=True) > 1:
            _log_message("Teams remaining = {}.".format(
                gamedb.count_teams(active_team_predicate_value=True)))

            _log_message("Getting new challenge.")
            challenge = self._get_challenge(gamedb=gamedb)

            _log_message("Running challenge {}.".format(challenge))
            self._run_challenge(challenge=challenge,
                                gamedb=gamedb, engine=engine)

            _log_message("Scoring entries.")
            winning_teams, losing_teams = self._score_entries_top_k_teams(k=self._options.single_tribe_top_k_threshold,
                                                                          tribe=tribe, challenge=challenge, gamedb=gamedb, engine=engine)

            _log_message("Running single tribe council.")
            self._run_single_tribe_council(winning_teams=winning_teams, losing_teams=losing_teams,
                                           gamedb=gamedb, engine=engine)

            _log_message("Merging teams.")
            self._merge_teams(target_team_size=self._options.target_team_size, tribe=tribe, gamedb=gamedb,
                              engine=engine)

        return gamedb.list_teams(active_team_predicate_value=True)[0]

    def _play_single_team(self, team: Team, gamedb: Database, engine: Engine) -> List[Player]:
        while team.size > self._options.target_finalist_count:
            challenge = self._get_challenge(gamedb=gamedb)
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
        _log_message("Counting votes from team {}.".format(team))
        team_votes = gamedb.count_votes(from_team=team)
        _log_message("Got votes {}.".format(pprint.pformat(team_votes)))

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

    # fraction of teams in losing tribe must vote
    def _run_multi_tribe_council(self, winning_tribe: Tribe, losing_tribe: Tribe, gamedb: Database, engine: Engine):
        non_immune_teams = list()

        for team in gamedb.stream_teams(from_tribe=losing_tribe):
            _log_message("Found losing team {}.".format(team))
            immunity_granted = random.random() < self._options.multi_tribe_team_immunity_likelihood
            if not immunity_granted:
                non_immune_teams.append(team)
            else:
                engine.add_event(events.NotifyImmunityAwardedEvent(team=team))

        # announce winner and tribal council for losing tribe
        tribal_council_start_timestamp = _unixtime()
        gamedb.clear_votes()
        engine.add_event(events.NotifyMultiTribeCouncilEvent(
            winning_tribe=winning_tribe, losing_tribe=losing_tribe))

        # wait for votes
        while (((_unixtime() - tribal_council_start_timestamp)
                < self._options.multi_tribe_council_time_sec) and not self._stop.is_set()):
            _log_message("Waiting for tribal council to end.")
            time.sleep(self._options.game_wait_sleep_interval_sec)

        # count votes
        for team in non_immune_teams:
            _log_message("Counting votes for non-immune team {}.".format(team))
            voted_out_player = self._get_voted_out_player(
                team=team, gamedb=gamedb)
            if voted_out_player:
                gamedb.deactivate_player(player=voted_out_player)
                _log_message("Deactivated player {}.".format(voted_out_player))
                engine.add_event(events.NotifyPlayerVotedOutEvent(
                    player=voted_out_player))

        # notify all players of what happened at tribal council
        engine.add_event(events.NotifyTribalCouncilCompletionEvent())

    # keep top K teams
    def _run_single_tribe_council(self, winning_teams: List[Team], losing_teams: List[Team],
                                  gamedb: Database, engine: Engine):

        # announce winner and tribal council for losing teams
        gamedb.clear_votes()
        engine.add_event(events.NotifySingleTribeCouncilEvent(
            winning_teams=winning_teams, losing_teams=losing_teams))
        tribal_council_start_timestamp = _unixtime()

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
            else:
                _log_message("For some reason no one got voted out...")
                _log_message("Players = {}.".format(
                    pprint.pformat(gamedb.list_players(from_team=team))))

        # notify all players of what happened at tribal council
        engine.add_event(events.NotifyTribalCouncilCompletionEvent())

    def _run_single_team_council(self, team: Team, losing_players: List[Player], gamedb: Database, engine: Engine):
        # announce winner and tribal council for losing teams
        gamedb.clear_votes()

        winning_player = [player for player in gamedb.list_players(
            from_team=team) if player not in losing_players][0]
        engine.add_event(events.NotifySingleTeamCouncilEvent(
            winning_player=winning_player, losing_players=losing_players))
        tribal_council_start_timestamp = _unixtime()

        # wait for votes
        while (((_unixtime() - tribal_council_start_timestamp)
                < self._options.single_team_council_time_sec) and not self._stop.is_set()):
            _log_message("Waiting for tribal council to end.")
            time.sleep(self._options.game_wait_sleep_interval_sec)

        # count votes
        voted_out_player = self._get_voted_out_player(team=team, gamedb=gamedb)
        if voted_out_player:
            gamedb.deactivate_player(player=voted_out_player)
            _log_message("Deactivated player {}.".format(voted_out_player))
            engine.add_event(events.NotifyPlayerVotedOutEvent(
                player=voted_out_player))

        # notify all players of what happened at tribal council
        engine.add_event(events.NotifyTribalCouncilCompletionEvent())

    def _run_finalist_tribe_council(self, finalists: List[Player], gamedb: Database, engine: Engine) -> Player:
        gamedb.clear_votes()

        engine.add_event(
            events.NotifyFinalTribalCouncilEvent(finalists=finalists))
        tribal_council_start_timestamp = _unixtime()

        # wait for votes
        while (((_unixtime() - tribal_council_start_timestamp)
                < self._options.final_tribal_council_time_sec) and not self._stop.is_set()):
            _log_message("Waiting for tribal council to end.")
            time.sleep(self._options.game_wait_sleep_interval_sec)

        # count votes
        player_votes = gamedb.count_votes(is_for_win=True)
        max_votes = 0
        winner = None

        for player_id, votes in player_votes.items():
            if votes > max_votes:
                max_votes = votes
                winner = gamedb.player_from_id(id=player_id)

        # announce winner
        engine.add_event(events.NotifyWinnerAnnouncementEvent(winner=winner))
        return winner

    def _merge_teams(self, target_team_size: int, tribe: Tribe, gamedb: Database, engine: Engine):
        # team merging is only necessary when the size of the team == 2
        # once a team size == 2, it should be merged with another team. the optimal
        # choice is to keep team sizes as close to the intended size as possible

        # find all teams with size = 2, these players need to be merged
        small_teams = gamedb.stream_teams(
            from_tribe=tribe, team_size_predicate_value=2)
        merge_candidates = Queue()

        for team in small_teams:
            _log_message("Found team of 2. Deacticating team {}.".format(team))

            # do not deactivate the last active team in the tribe
            if gamedb.count_teams(from_tribe=tribe, active_team_predicate_value=True) > 1:
                gamedb.deactivate_team(team)

            for player in gamedb.list_players(from_team=team):
                _log_message("Adding merge candidate {}.".format(player))
                merge_candidates.put(player)

        sorted_teams = gamedb.stream_teams(
            from_tribe=tribe, order_by_size=True, descending=False)

        _log_message("Redistributing merge candidates...")
        # round robin redistribution strategy
        # simplest case, could use more thought.
        visited = {}
        while not merge_candidates.empty() and sorted_teams:
            for team in sorted_teams:
                other_options_available = team.id not in visited
                visited[team.id] = True

                if (team.size >= target_team_size and other_options_available):
                    _log_message("Team {} has size >= target {} and other options are available. "
                                 "Continuing search...".format(team, target_team_size))
                    continue

                player = merge_candidates.get()
                if player.team_id == team.id:
                    continue

                _log_message("Merging player {} from team {} into team {}.".format(
                    player, player.team_id, team.id))
                player.team_id = team.id
                team.size = team.size + 1
                gamedb.save(team)
                gamedb.save(player)

                # notify player of new team assignment
                engine.add_event(events.NotifyTeamReassignmentEvent(player=player,
                                                                    team=team))

    def _get_challenge(self, gamedb: Database) -> Challenge:
        available_challenge_count = 0
        while available_challenge_count == 0 and not self._stop.is_set():
            _log_message("Waiting for next challenge to become available.")
            time.sleep(self._options.game_wait_sleep_interval_sec)
            available_challenges = gamedb.list_challenges(
                challenge_completed_predicate_value=False)
            available_challenge_count = len(available_challenges)
        return available_challenges[0]

    def _run_challenge(self, challenge: Challenge, gamedb: Database, engine: Engine):
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

        challenge.complete = True
        gamedb.save(challenge)

    def _score_entries_tribe_aggregate_fn(self, entries: Iterable, challenge: Challenge, score_dict: Dict, gamedb: Database, engine: Engine):
        """Note that all built-ins are thread safe in python, meaning we can
        atomically increment the score int held in score_dict."""

        entries_iter = iter(entries)
        while not self._stop.is_set():
            try:
                entry = next(entries_iter)
                pprint.pprint(entry)
                points = entry.likes / entry.views
                player = gamedb.player_from_id(entry.player_id)
                engine.add_event(events.NotifyPlayerScoreEvent(
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
        _log_message("_score_entries_tribe_agg = {}.".format(
            score_dict['score']))
        return score_dict['score'] / players

    def _score_entries_top_k_teams_fn(self, entries: Iterable, challenge: Challenge, score_dict: Dict, gamedb: Database, engine: Engine):
        entries_iter = iter(entries)
        while not self._stop.is_set():
            try:
                entry = next(entries_iter)
                _log_message("Entry {}.".format(entry))
                points = entry.likes / entry.views
                player = gamedb.player_from_id(entry.player_id)
                engine.add_event(events.NotifyPlayerScoreEvent(
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
        _log_message("Rank threshold = {}".format(rank_threshold))

        # note that the default python heap pops in ascending order,
        # so the rank here is actually worst to best.
        num_scores = len(top_scores)
        if num_scores == 1:
            score, team_id = heapq.heappop(top_scores)
            _log_message("Winner {}.".format(team_id))
            winning_teams = [gamedb.team_from_id(team_id)]
        else:
            for rank in range(num_scores):
                score, team_id = heapq.heappop(top_scores)
                _log_message("Team {} rank {} with score {}.".format(
                    team_id, rank, score))
                if rank >= rank_threshold:
                    _log_message("Winner {}.".format(team_id))
                    winning_teams.append(gamedb.team_from_id(team_id))
                else:
                    _log_message("Loser {}.".format(team_id))
                    losing_teams.append(gamedb.team_from_id(team_id))

        return (winning_teams, losing_teams)

    def _score_entries_top_k_players_fn(self, entries: Iterable, challenge: Challenge, score_dict: Dict, gamedb: Database, engine: Engine):
        entries_iter = iter(entries)
        while not self._stop.is_set():
            try:
                entry = next(entries_iter)
                _log_message("Entry {}.".format(entry))
                points = entry.likes / entry.views
                player = gamedb.player_from_id(entry.player_id)
                engine.add_event(events.NotifyPlayerScoreEvent(
                    player=player, challenge=challenge,
                    entry=entry, points=points))
                score_dict[player.id] = points
            except StopIteration:
                break

    def _score_entries_top_k_players(self, team: Team, challenge: Challenge, gamedb: Database, engine: Engine) -> List[Player]:
        player_scores = {}
        top_scores = list()
        losing_players = list()
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
                _log_message("Player {} rank {} with score {}.".format(
                    player_id, rank, score))

                # all but the highest scorer lose
                if rank < (num_scores - 1):
                    losing_players.append(gamedb.player_from_id(player_id))

        return losing_players

    def _merge_tribes(self, tribe1: Tribe, tribe2: Tribe, new_tribe_name: Text, gamedb: Database) -> Tribe:
        new_tribe = gamedb.tribe(name=new_tribe_name)
        gamedb.batch_update_tribe(from_tribe=tribe1, to_tribe=new_tribe)
        gamedb.batch_update_tribe(from_tribe=tribe2, to_tribe=new_tribe)
        return new_tribe


if __name__ == '__main__':
    options = GameOptions()
    game = Game(options=options)
    engine = Engine(options=options)
    database = FirestoreDB(json_config_path=_FIRESTORE_PROD_CONF_JSON_PATH)
    game.play(tribe1=database.tribe_from_id(_TRIBE_1_ID),
              tribe2=database.tribe_from_id(_TRIBE_2_ID),
              gamedb=database,
              engine=engine)
