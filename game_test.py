import unittest
import mock
from game import Game
from game import GameOptions
from game_engine.engine import Engine
from game_engine.database import Database, Data
from game_engine.database import Player, Team, Tribe
from game_engine.database import Challenge, Entry, Vote
import attr
from typing import Any, Iterable, Dict, Text, Tuple, List
import uuid
from mock import Mock
import time
import pprint
from multiprocessing import Process
from game_engine import events
from queue import Queue

TEST_CHALLENGE_START_OFFSET_SEC = 1
TEST_CHALLENGE_END_OFFSET_SEC = 1


class MockDatabase(Database):
    def __init__(self):
        self._players = {
            'player/01': Player(id='player/01', tribe_id='tribe/1', team_id='team/1'),
            'player/02': Player(id='player/02', tribe_id='tribe/1', team_id='team/1'),
            'player/03': Player(id='player/03', tribe_id='tribe/1', team_id='team/1'),
            'player/04': Player(id='player/04', tribe_id='tribe/1', team_id='team/1'),
            'player/05': Player(id='player/05', tribe_id='tribe/1', team_id='team/2'),
            'player/06': Player(id='player/06', tribe_id='tribe/1', team_id='team/2'),
            'player/07': Player(id='player/07', tribe_id='tribe/1', team_id='team/2'),
            'player/08': Player(id='player/08', tribe_id='tribe/1', team_id='team/2'),
            'player/09': Player(id='player/09', tribe_id='tribe/2', team_id='team/3'),
            'player/10': Player(id='player/10', tribe_id='tribe/2', team_id='team/3'),
            'player/11': Player(id='player/11', tribe_id='tribe/2', team_id='team/3'),
            'player/12': Player(id='player/12', tribe_id='tribe/2', team_id='team/3'),
            'player/13': Player(id='player/13', tribe_id='tribe/2', team_id='team/4'),
            'player/14': Player(id='player/14', tribe_id='tribe/2', team_id='team/4'),
            'player/15': Player(id='player/15', tribe_id='tribe/2', team_id='team/4'),
            'player/16': Player(id='player/16', tribe_id='tribe/2', team_id='team/4'),
            'player/17': Player(id='player/17', tribe_id='tribe/2', team_id='team/5'),
            'player/18': Player(id='player/18', tribe_id='tribe/2', team_id='team/5'),
            'player/19': Player(id='player/19', tribe_id='tribe/2', team_id='team/6'),
            'player/20': Player(id='player/20', tribe_id='tribe/2', team_id='team/6'),
            'player/21': Player(id='player/21', tribe_id='tribe/2', team_id='team/7'),
            'player/22': Player(id='player/22', tribe_id='tribe/2', team_id='team/7'),
            'player/23': Player(id='player/23', tribe_id='tribe/2', team_id='team/7')
        }

        self._teams = {
            'team/1': Team(id='team/1', name='name/team1', size=4, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', size=4, tribe_id='tribe/1'),
            'team/3': Team(id='team/3', name='name/team3', size=4, tribe_id='tribe/2'),
            'team/4': Team(id='team/4', name='name/team4', size=4, tribe_id='tribe/2'),
            'team/5': Team(id='team/5', name='name/team5', size=2, tribe_id='tribe/2'),
            'team/6': Team(id='team/6', name='name/team6', size=2, tribe_id='tribe/2'),
            'team/7': Team(id='team/7', name='name/team7', size=3, tribe_id='tribe/2')
        }

        self._tribes = {
            'tribe/1': Tribe(id='tribe/1', name='name/tribe1', size=8),
            'tribe/2': Tribe(id='tribe/2', name='name/tribe2', size=15)
        }

        self._challenges = {
            'challenge/1': Challenge(id='challenge/1', name='name/challenge1'),
            'challenge/2': Challenge(id='challenge/2', name='name/challenge2'),
            'challenge/3': Challenge(id='challenge/3', name='name/challenge3'),
            'challenge/4': Challenge(id='challenge/4', name='name/challenge4'),
            'challenge/5': Challenge(id='challenge/5', name='name/challenge5'),
        }

        self._entries = {
            'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='player/01', tribe_id='tribe/1', challenge_id='challenge/1'),
            'entry/2': Entry(id='entry/2', likes=1, views=1, player_id='player/02', tribe_id='tribe/1', challenge_id='challenge/1'),
            'entry/3': Entry(id='entry/3', likes=1, views=1, player_id='player/03', tribe_id='tribe/1', challenge_id='challenge/1'),
            'entry/4': Entry(id='entry/4', likes=1, views=1, player_id='player/04', tribe_id='tribe/1', challenge_id='challenge/1'),
            'entry/5': Entry(id='entry/5', likes=1, views=1, player_id='player/12', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/6': Entry(id='entry/6', likes=1, views=1, player_id='player/13', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/7': Entry(id='entry/7', likes=1, views=1, player_id='player/14', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/8': Entry(id='entry/8', likes=1, views=1, player_id='player/15', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/9': Entry(id='entry/9', likes=1, views=1, player_id='player/16', tribe_id='tribe/2', challenge_id='challenge/1'),
        }

        self._votes = {}

    def batch_update_tribe(self, from_tribe: Tribe, to_tribe: Tribe) -> None:
        for key in self._players:
            if self._players[key].tribe_id == from_tribe.id:
                self._players[key].tribe_id = to_tribe.id

    def stream_entries(self, from_tribe: Tribe, from_challenge: Challenge) -> Iterable[Entry]:
        return [entry for entry in self._entries.values() if
                (entry.challenge_id == from_challenge.id and entry.tribe_id == from_tribe.id)]

    def stream_teams(self, from_tribe: Tribe,
                     team_size_predicate_value: [int, None] = None,
                     order_by_size=True,
                     descending=False
                     ) -> Iterable[Team]:
        if team_size_predicate_value:
            return sorted([team for team in self._teams.values() if (team.size == team_size_predicate_value
                                                                     and team.active
                                                                     and team.tribe_id == from_tribe.id)],
                          key=lambda team: team.size, reverse=True)
        else:
            return sorted([team for team in self._teams.values() if (team.active and team.tribe_id == from_tribe.id)],
                          key=lambda team: team.size, reverse=True)

    def count_players(self, from_tribe: Tribe = None, from_team: Team = None) -> int:
        count = 0
        for key in self._players:
            if from_tribe:
                if self._players[key].tribe_id == from_tribe.id:
                    count = count + 1
            elif from_team:
                if self._players[key].team_id == from_team.id:
                    count = count + 1
        return count

    def count_teams(self, active_team_predicate_value=True) -> int:
        return len([team for team in self._teams.values() if team.active == active_team_predicate_value])

    def deactivate_player(self, player: Player) -> None:
        player.active = False
        self._players[player.id].active = False
        self._teams[player.team_id].size = self._teams[player.team_id].size - 1

    def deactivate_team(self, team: Team) -> None:
        team.active = False
        self._teams[team.id].active = False
        pprint.pprint(self._teams)

    def count_votes(self, from_team: Team) -> Dict[Text, int]:
        player_counts = {}

        for vote in self._votes.values():
            voter = self.player_from_id(vote.from_id)
            team = self._teams[voter.team_id]
            if team.id != from_team.id or not voter.active:
                continue

            if vote.to_id not in player_counts:
                player_counts[vote.to_id] = 1
            else:
                player_counts[vote.to_id] = player_counts[vote.to_id] + 1

        return player_counts

    def clear_votes(self) -> None:
        self._votes = {}

    def list_challenges(self, challenge_completed_predicate_value=False) -> Iterable[Challenge]:
        return [challenge for challenge in self._challenges.values() if not challenge.complete]

    def list_players(self, from_team: Team, active_player_predicate_value=True) -> Iterable[Player]:
        return [player for player in self._players.values() if player.team_id == from_team.id and player.active == active_player_predicate_value]

    def list_teams(self, active_team_predicate_value=True) -> Iterable[Team]:
        return [team for team in self._teams.values() if team.active == active_team_predicate_value]

    def player(self, name: Text) -> Player:
        pass

    def player_from_id(self, id: Text) -> Player:
        return self._players[id]

    def tribe(self, name: Text) -> Tribe:
        tribe_id = uuid.uuid1()
        tribe = Tribe(id=tribe_id, name=name)
        self._tribes[tribe_id] = tribe
        return tribe

    def team_from_id(self, id: Text) -> Team:
        return self._teams[id]

    def tribe_from_id(self, id: Text) -> Tribe:
        return self._tribes[id]

    def challenge_from_id(self, id: Text) -> Challenge:
        return self._challenges[id]

    def save(self, data: Data) -> None:
        if isinstance(data, Player):
            prev_team_id = self._players[data.id].team_id
            next_team_id = data.team_id
            self._players[data.id] = data
            if prev_team_id != next_team_id:
                self._teams[prev_team_id].size -= 1
                self._teams[next_team_id].size += 1


class GameTest(unittest.TestCase):
    def setUp(self):
        self._game = Game(options=GameOptions(
            game_wait_sleep_interval_sec=0.5,
            single_tribe_council_time_sec=2,
            single_tribe_top_k_threshold=0.5,
            multi_tribe_team_immunity_likelihood=0.0,
            multi_tribe_council_time_sec=2))

    # def test_play(self):
    # def test_play_multi_tribe(self):

    def test_play_single_tribe(self):
        gamedb = MockDatabase()
        engine = Mock()

        # start with 8 players in tribe
        gamedb._players = {
            'r1': Player(id='r1', tribe_id='tribe/1', team_id='red'),
            'r2': Player(id='r2', tribe_id='tribe/1', team_id='red'),
            'r3': Player(id='r3', tribe_id='tribe/1', team_id='red'),
            'r4': Player(id='r4', tribe_id='tribe/1', team_id='red'),
            'b1': Player(id='b1', tribe_id='tribe/1', team_id='blue'),
            'b2': Player(id='b2', tribe_id='tribe/1', team_id='blue'),
            'b3': Player(id='b3', tribe_id='tribe/1', team_id='blue'),
            'b4': Player(id='b4', tribe_id='tribe/1', team_id='blue'),
        }

        gamedb._teams = {
            'red': Team(id='red', name='name/red', size=4, tribe_id='tribe/1'),
            'blue': Team(id='blue', name='name/blue', size=4, tribe_id='tribe/1'),
        }

        gamedb._tribes = {
            'tribe/1': Tribe(id='tribe/1', name='name/tribe1', size=8),
        }

        gamedb._challenges = {
            'challenge/1': Challenge(id='challenge/1', name='name/challenge1'),
            'challenge/2': Challenge(id='challenge/2', name='name/challenge2'),
            'challenge/3': Challenge(id='challenge/3', name='name/challenge3'),
            'challenge/4': Challenge(id='challenge/4', name='name/challenge4'),
        }

        gamedb._entries = {}

        def challenge1_worker(gamedb):
            # round1: red1, red2, red3, red4 vs blue1, blue2, blue3, blue4
            # blue wins challenge
            # red4 is voted out
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id='tribe/1', challenge_id='challenge/1'),
                'entry/2': Entry(id='entry/2', likes=1, views=1, player_id='r2', tribe_id='tribe/1', challenge_id='challenge/1'),
                'entry/3': Entry(id='entry/3', likes=1, views=1, player_id='r3', tribe_id='tribe/1', challenge_id='challenge/1'),
                'entry/4': Entry(id='entry/4', likes=1, views=1, player_id='r4', tribe_id='tribe/1', challenge_id='challenge/1'),
                'entry/5': Entry(id='entry/5', likes=2, views=1, player_id='b1', tribe_id='tribe/1', challenge_id='challenge/1'),
                'entry/6': Entry(id='entry/6', likes=2, views=1, player_id='b2', tribe_id='tribe/1', challenge_id='challenge/1'),
                'entry/7': Entry(id='entry/7', likes=2, views=1, player_id='b3', tribe_id='tribe/1', challenge_id='challenge/1'),
                'entry/8': Entry(id='entry/8', likes=2, views=1, player_id='b4', tribe_id='tribe/1', challenge_id='challenge/1'),
            }

        def council1_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='r4'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='r4'),
                'vote/3': Vote(id='vote/3', from_id='r3', to_id='r4'),
                'vote/4': Vote(id='vote/4', from_id='r4', to_id='r1'),
            }

        def challenge2_worker(gamedb):
            # round2: red1, red2, red3 vs blue1, blue2, blue3, blue4
            # red wins challenge
            # blue4 is voted out
            # TODO(brandon): only count votes from active players
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=2, views=1, player_id='r1', tribe_id='tribe/1', challenge_id='challenge/2'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='r2', tribe_id='tribe/1', challenge_id='challenge/2'),
                'entry/3': Entry(id='entry/3', likes=2, views=1, player_id='r3', tribe_id='tribe/1', challenge_id='challenge/2'),
                'entry/5': Entry(id='entry/5', likes=1, views=1, player_id='b1', tribe_id='tribe/1', challenge_id='challenge/2'),
                'entry/6': Entry(id='entry/6', likes=1, views=1, player_id='b2', tribe_id='tribe/1', challenge_id='challenge/2'),
                'entry/7': Entry(id='entry/7', likes=1, views=1, player_id='b3', tribe_id='tribe/1', challenge_id='challenge/2'),
                'entry/8': Entry(id='entry/8', likes=1, views=1, player_id='b4', tribe_id='tribe/1', challenge_id='challenge/2'),
            }

        def council2_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='b1', to_id='b4'),
                'vote/2': Vote(id='vote/2', from_id='b2', to_id='b4'),
                'vote/3': Vote(id='vote/3', from_id='b3', to_id='b4'),
                'vote/4': Vote(id='vote/4', from_id='b4', to_id='b1'),
            }

        def challenge3_worker(gamedb):
            # round3: red1, red2, red3 vs blue1, blue2, blue3
            # red wins challenge
            # blue3 is voted out
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=2, views=1, player_id='r1', tribe_id='tribe/1', challenge_id='challenge/3'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='r2', tribe_id='tribe/1', challenge_id='challenge/3'),
                'entry/3': Entry(id='entry/3', likes=2, views=1, player_id='r3', tribe_id='tribe/1', challenge_id='challenge/3'),
                'entry/5': Entry(id='entry/5', likes=1, views=1, player_id='b1', tribe_id='tribe/1', challenge_id='challenge/3'),
                'entry/6': Entry(id='entry/6', likes=1, views=1, player_id='b2', tribe_id='tribe/1', challenge_id='challenge/3'),
                'entry/7': Entry(id='entry/7', likes=1, views=1, player_id='b3', tribe_id='tribe/1', challenge_id='challenge/3'),
            }

        def council3_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='b1', to_id='b3'),
                'vote/2': Vote(id='vote/2', from_id='b2', to_id='b3'),
                'vote/3': Vote(id='vote/3', from_id='b3', to_id='b1'),
            }

        challenge_worker_queue = Queue()
        for worker in [challenge1_worker, challenge2_worker, challenge3_worker]:
            challenge_worker_queue.put(worker)

        council_worker_queue = Queue()
        for worker in [council1_worker, council2_worker, council3_worker]:
            council_worker_queue.put(worker)

        def event_fn(event):
            if isinstance(event, events.NotifyTribalChallengeEvent) and not challenge_worker_queue.empty():
                challenge_worker = challenge_worker_queue.get_nowait()
                challenge_worker(gamedb)
            elif isinstance(event, events.NotifySingleTribeCouncilEvent) and not council_worker_queue.empty():
                council_worker = council_worker_queue.get_nowait()
                council_worker(gamedb)

        engine.add_event = event_fn
        team = self._game._play_single_tribe(gamedb.tribe_from_id('tribe/1'), gamedb=gamedb,
                                             engine=engine)

        # round4: red1, red2, red3 vs blue1, blue2
        # blue has two players and would deadlock
        # blue merges into red
        # single team with 5 members should be returned
        self.assertEqual(team.id, 'red')
        self.assertListEqual([player.id for player in gamedb.list_players(from_team=team) if player.active], [
            'r1', 'r2', 'r3', 'b1', 'b2'
        ])

    def test_get_voted_out_player(self):
        gamedb = MockDatabase()

        gamedb._votes = {
            'vote/1': Vote(id='vote/1', from_id='player/20', to_id='player/22'),
            'vote/2': Vote(id='vote/2', from_id='player/21', to_id='player/22'),
            'vote/3': Vote(id='vote/3', from_id='player/22', to_id='player/21'),
            'vote/4': Vote(id='vote/4', from_id='player/23', to_id='player/22'),
        }

        player = self._game._get_voted_out_player(gamedb.team_from_id('team/7'),
                                                  gamedb=gamedb)
        self.assertEqual(player.id, 'player/22')

        gamedb._votes = {
            'vote/1': Vote(id='vote/1', from_id='player/20', to_id='player/23'),
            'vote/2': Vote(id='vote/2', from_id='player/21', to_id='player/23'),
            'vote/3': Vote(id='vote/3', from_id='player/22', to_id='player/23'),
            'vote/4': Vote(id='vote/4', from_id='player/23', to_id='player/20'),
        }

        player = self._game._get_voted_out_player(gamedb.team_from_id('team/7'),
                                                  gamedb=gamedb)
        self.assertEqual(player.id, 'player/23')

    def test_get_voted_out_player_with_tie(self):
        gamedb = MockDatabase()

        gamedb._players = {
            'player/20': Player(id='player/20', tribe_id='tribe/2', team_id='team/7'),
            'player/21': Player(id='player/21', tribe_id='tribe/2', team_id='team/7'),
            'player/22': Player(id='player/22', tribe_id='tribe/2', team_id='team/7'),
            'player/23': Player(id='player/23', tribe_id='tribe/2', team_id='team/7')
        }

        gamedb._teams = {
            'team/7': Team(id='team/7', name='name/team7', size=4, tribe_id='tribe/2')
        }

        # in a tie situation, the algorithm leaves it to chance to
        # decide the winner.
        gamedb._votes = {
            'vote/1': Vote(id='vote/1', from_id='player/20', to_id='player/21'),
            'vote/2': Vote(id='vote/2', from_id='player/21', to_id='player/20'),
            'vote/3': Vote(id='vote/3', from_id='player/22', to_id='player/21'),
            'vote/4': Vote(id='vote/4', from_id='player/23', to_id='player/20'),
        }

        player = self._game._get_voted_out_player(gamedb.team_from_id('team/7'),
                                                  gamedb=gamedb)
        self.assertIn(player.id, ['player/20', 'player/21'])

    def test_run_multi_tribe_council(self):
        gamedb = MockDatabase()
        gamedb.clear_votes = Mock()
        engine = Mock()

        # inject votes
        gamedb._votes = {
            'vote/1': Vote(id='vote/1', from_id='player/09', to_id='player/12'),
            'vote/2': Vote(id='vote/2', from_id='player/10', to_id='player/12'),
            'vote/3': Vote(id='vote/3', from_id='player/11', to_id='player/12'),
            'vote/4': Vote(id='vote/4', from_id='player/12', to_id='player/09'),
        }

        self._game._run_multi_tribe_council(winning_tribe=gamedb.tribe_from_id('tribe/1'),
                                            losing_tribe=gamedb.tribe_from_id('tribe/2'), gamedb=gamedb, engine=engine)

        engine.add_event.assert_called()
        gamedb.clear_votes.assert_called_once()
        self.assertFalse(gamedb.player_from_id('player/12').active)

    def test_run_single_tribe_council(self):
        gamedb = MockDatabase()
        gamedb.clear_votes = Mock()
        engine = Mock()

        # inject votes
        gamedb._votes = {
            'vote/1': Vote(id='vote/1', from_id='player/01', to_id='player/04'),
            'vote/2': Vote(id='vote/2', from_id='player/02', to_id='player/04'),
            'vote/3': Vote(id='vote/3', from_id='player/03', to_id='player/04'),
            'vote/4': Vote(id='vote/4', from_id='player/04', to_id='player/01'),
        }

        self._game._run_single_tribe_council(winning_teams=[gamedb._teams['team/2']],
                                             losing_teams=[
                                                 gamedb._teams['team/1']],
                                             gamedb=gamedb, engine=engine)
        engine.add_event.assert_called()
        gamedb.clear_votes.assert_called_once()
        self.assertFalse(gamedb.player_from_id('player/04').active)

    def test_merge_teams_2player(self):
        gamedb = MockDatabase()
        engine = Mock()

        gamedb._players = {
            'player/01': Player(id='player/01', tribe_id='tribe/1', team_id='team/1'),
            'player/02': Player(id='player/02', tribe_id='tribe/1', team_id='team/1'),
        }

        gamedb._teams = {
            'team/1': Team(id='team/1', name='name/team1', size=1, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', size=1, tribe_id='tribe/1'),
        }

        tribe = gamedb.tribe_from_id('tribe/1')
        self._game._merge_teams(
            target_team_size=5, tribe=tribe, gamedb=gamedb, engine=engine)
        engine.add_event.assert_not_called()

        expected_player_to_team_dict = {
            'player/01': 'team/1',
            'player/02': 'team/1',
        }

        for k, v in gamedb._players.items():
            self.assertEqual(v.team_id, expected_player_to_team_dict[k])

    def test_merge_teams_3player(self):
        gamedb = MockDatabase()
        engine = Mock()

        gamedb._players = {
            'player/01': Player(id='player/01', tribe_id='tribe/1', team_id='team/1'),
            'player/02': Player(id='player/02', tribe_id='tribe/1', team_id='team/1'),
            'player/03': Player(id='player/03', tribe_id='tribe/1', team_id='team/2'),
        }

        gamedb._teams = {
            'team/1': Team(id='team/1', name='name/team1', size=2, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', size=1, tribe_id='tribe/1'),
        }

        tribe = gamedb.tribe_from_id('tribe/1')
        self._game._merge_teams(
            target_team_size=5, tribe=tribe, gamedb=gamedb, engine=engine)
        engine.add_event.assert_called()

        expected_player_to_team_dict = {
            'player/01': 'team/2',
            'player/02': 'team/2',
            'player/03': 'team/2',
        }

        for k, v in gamedb._players.items():
            self.assertEqual(v.team_id, expected_player_to_team_dict[k])

    def test_merge_teams_5player(self):
        gamedb = MockDatabase()
        engine = Mock()

        gamedb._players = {
            'player/01': Player(id='player/01', tribe_id='tribe/1', team_id='team/1'),
            'player/02': Player(id='player/02', tribe_id='tribe/1', team_id='team/1'),
            'player/03': Player(id='player/03', tribe_id='tribe/1', team_id='team/2'),
            'player/04': Player(id='player/04', tribe_id='tribe/1', team_id='team/2'),
            'player/05': Player(id='player/05', tribe_id='tribe/1', team_id='team/2'),
        }

        gamedb._teams = {
            'team/1': Team(id='team/1', name='name/team1', size=2, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', size=3, tribe_id='tribe/1'),
        }

        tribe = gamedb.tribe_from_id('tribe/1')
        self._game._merge_teams(
            target_team_size=5, tribe=tribe, gamedb=gamedb, engine=engine)
        engine.add_event.assert_called()

        expected_player_to_team_dict = {
            'player/01': 'team/2',
            'player/02': 'team/2',
            'player/03': 'team/2',
            'player/04': 'team/2',
            'player/05': 'team/2',
        }

        for k, v in gamedb._players.items():
            self.assertEqual(v.team_id, expected_player_to_team_dict[k])

    def test_merge_teams_6player(self):
        gamedb = MockDatabase()
        engine = Mock()

        gamedb._players = {
            'player/01': Player(id='player/01', tribe_id='tribe/1', team_id='team/1'),
            'player/02': Player(id='player/02', tribe_id='tribe/1', team_id='team/1'),
            'player/03': Player(id='player/03', tribe_id='tribe/1', team_id='team/1'),
            'player/04': Player(id='player/04', tribe_id='tribe/1', team_id='team/2'),
            'player/05': Player(id='player/05', tribe_id='tribe/1', team_id='team/2'),
            'player/06': Player(id='player/06', tribe_id='tribe/1', team_id='team/2'),
        }

        gamedb._teams = {
            'team/1': Team(id='team/1', name='name/team1', size=3, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', size=3, tribe_id='tribe/1'),
        }

        tribe = gamedb.tribe_from_id('tribe/1')
        self._game._merge_teams(
            target_team_size=5, tribe=tribe, gamedb=gamedb, engine=engine)
        engine.add_event.assert_not_called()

        expected_player_to_team_dict = {
            'player/01': 'team/1',
            'player/02': 'team/1',
            'player/03': 'team/1',
            'player/04': 'team/2',
            'player/05': 'team/2',
            'player/06': 'team/2',
        }

        for k, v in gamedb._players.items():
            self.assertEqual(v.team_id, expected_player_to_team_dict[k])

    def test_merge_teams_9player(self):
        gamedb = MockDatabase()
        engine = Mock()

        gamedb._players = {
            'player/01': Player(id='player/01', tribe_id='tribe/1', team_id='team/1'),
            'player/02': Player(id='player/02', tribe_id='tribe/1', team_id='team/1'),
            'player/03': Player(id='player/03', tribe_id='tribe/1', team_id='team/2'),
            'player/04': Player(id='player/04', tribe_id='tribe/1', team_id='team/2'),
            'player/05': Player(id='player/05', tribe_id='tribe/1', team_id='team/3'),
            'player/06': Player(id='player/06', tribe_id='tribe/1', team_id='team/3'),
            'player/07': Player(id='player/07', tribe_id='tribe/1', team_id='team/4'),
            'player/08': Player(id='player/08', tribe_id='tribe/1', team_id='team/4'),
            'player/09': Player(id='player/09', tribe_id='tribe/1', team_id='team/4'),
        }

        gamedb._teams = {
            'team/1': Team(id='team/1', name='name/team1', size=2, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', size=2, tribe_id='tribe/1'),
            'team/3': Team(id='team/3', name='name/team3', size=2, tribe_id='tribe/1'),
            'team/4': Team(id='team/4', name='name/team4', size=3, tribe_id='tribe/1'),
        }

        tribe = gamedb.tribe_from_id('tribe/1')
        self._game._merge_teams(
            target_team_size=5, tribe=tribe, gamedb=gamedb, engine=engine)
        engine.add_event.assert_called()

        expected_player_to_team_dict = {
            'player/01': 'team/4',
            'player/02': 'team/4',
            'player/03': 'team/4',
            'player/04': 'team/4',
            'player/05': 'team/4',
            'player/06': 'team/4',
            'player/07': 'team/4',
            'player/08': 'team/4',
            'player/09': 'team/4',
        }

        for k, v in gamedb._players.items():
            self.assertEqual(v.team_id, expected_player_to_team_dict[k])

    def test_merge_teams_10player(self):
        gamedb = MockDatabase()
        engine = Mock()

        gamedb._players = {
            'player/01': Player(id='player/01', tribe_id='tribe/1', team_id='team/1'),
            'player/02': Player(id='player/02', tribe_id='tribe/1', team_id='team/1'),
            'player/03': Player(id='player/03', tribe_id='tribe/1', team_id='team/2'),
            'player/04': Player(id='player/04', tribe_id='tribe/1', team_id='team/2'),
            'player/05': Player(id='player/05', tribe_id='tribe/1', team_id='team/2'),
            'player/06': Player(id='player/06', tribe_id='tribe/1', team_id='team/2'),
            'player/07': Player(id='player/07', tribe_id='tribe/1', team_id='team/3'),
            'player/08': Player(id='player/08', tribe_id='tribe/1', team_id='team/3'),
            'player/09': Player(id='player/09', tribe_id='tribe/1', team_id='team/3'),
            'player/10': Player(id='player/10', tribe_id='tribe/1', team_id='team/3'),
        }

        gamedb._teams = {
            'team/1': Team(id='team/1', name='name/team1', size=2, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', size=4, tribe_id='tribe/1'),
            'team/3': Team(id='team/3', name='name/team3', size=4, tribe_id='tribe/1'),
        }

        tribe = gamedb.tribe_from_id('tribe/1')
        self._game._merge_teams(
            target_team_size=5, tribe=tribe, gamedb=gamedb, engine=engine)
        engine.add_event.assert_called()

        expected_player_to_team_dict = {
            'player/01': 'team/2',
            'player/02': 'team/3',
            'player/03': 'team/2',
            'player/04': 'team/2',
            'player/05': 'team/2',
            'player/06': 'team/2',
            'player/07': 'team/3',
            'player/08': 'team/3',
            'player/09': 'team/3',
            'player/10': 'team/3',
        }

        for k, v in gamedb._players.items():
            self.assertEqual(v.team_id, expected_player_to_team_dict[k])

    def test_get_challenge(self):
        gamedb = MockDatabase()
        challenges = set()
        for _ in range(5):
            challenge = self._game._get_challenge(gamedb=gamedb)
            challenges.add(challenge.name)
        self.assertSetEqual(challenges, set(
            ['name/challenge1']))

        for _ in range(5):
            challenge = self._game._get_challenge(gamedb=gamedb)
            challenges.add(challenge.name)
            gamedb._challenges[challenge.id].complete = True
        self.assertSetEqual(challenges, set(
            ['name/challenge1', 'name/challenge2', 'name/challenge3', 'name/challenge4', 'name/challenge5']))

    def test_run_challenge(self):
        engine = Mock()
        gamedb = MockDatabase()
        challenge = gamedb.challenge_from_id('challenge/1')
        challenge.start_timestamp = time.time() + TEST_CHALLENGE_START_OFFSET_SEC
        challenge.end_timestamp = challenge.start_timestamp + TEST_CHALLENGE_END_OFFSET_SEC
        self._game._run_challenge(
            challenge=challenge, gamedb=gamedb, engine=engine)
        engine.add_event.assert_called_once()

    def test_score_entries_tribe_aggregate(self):
        engine = Mock()
        gamedb = MockDatabase()
        tribe = gamedb.tribe_from_id('tribe/1')
        challenge = gamedb.challenge_from_id('challenge/1')
        self.assertEqual(self._game._score_entries_tribe_aggregate(
            tribe=tribe, challenge=challenge, gamedb=gamedb, engine=engine), 0.5)
        engine.add_event.assert_called()

    def test_score_entries_top_k_teams(self):
        engine = Mock()
        gamedb = MockDatabase()
        tribe = gamedb.tribe_from_id('tribe/2')
        challenge = gamedb.challenge_from_id('challenge/1')

        gamedb._players = {
            'player/09': Player(id='player/09', tribe_id='tribe/2', team_id='team/3'),
            'player/10': Player(id='player/10', tribe_id='tribe/2', team_id='team/3'),
            'player/11': Player(id='player/11', tribe_id='tribe/2', team_id='team/3'),
            'player/12': Player(id='player/12', tribe_id='tribe/2', team_id='team/3'),
            'player/13': Player(id='player/13', tribe_id='tribe/2', team_id='team/4'),
            'player/14': Player(id='player/14', tribe_id='tribe/2', team_id='team/4'),
            'player/15': Player(id='player/15', tribe_id='tribe/2', team_id='team/4'),
            'player/16': Player(id='player/16', tribe_id='tribe/2', team_id='team/4'),
            'player/17': Player(id='player/17', tribe_id='tribe/2', team_id='team/5'),
            'player/18': Player(id='player/18', tribe_id='tribe/2', team_id='team/5'),
        }

        gamedb._entries = {
            'entry/01': Entry(id='entry/01', likes=5, views=1, player_id='player/09', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/02': Entry(id='entry/02', likes=5, views=1, player_id='player/10', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/03': Entry(id='entry/03', likes=5, views=1, player_id='player/11', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/04': Entry(id='entry/04', likes=5, views=1, player_id='player/12', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/05': Entry(id='entry/05', likes=2, views=1, player_id='player/13', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/06': Entry(id='entry/06', likes=2, views=1, player_id='player/14', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/07': Entry(id='entry/07', likes=2, views=1, player_id='player/15', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/08': Entry(id='entry/08', likes=2, views=1, player_id='player/16', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/09': Entry(id='entry/09', likes=1, views=1, player_id='player/17', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/10': Entry(id='entry/10', likes=1, views=1, player_id='player/18', tribe_id='tribe/2', challenge_id='challenge/1'),
        }

        winning_teams, losing_teams = self._game._score_entries_top_k_teams(k=self._game._options.single_tribe_top_k_threshold,
                                                                            tribe=tribe, challenge=challenge, gamedb=gamedb, engine=engine)
        self.assertListEqual(winning_teams, [
            gamedb.team_from_id('team/3'),
        ])
        self.assertListEqual(losing_teams, [
            gamedb.team_from_id('team/5'),
            gamedb.team_from_id('team/4'),
        ])
        engine.add_event.assert_called()

    def test_merge_tribes(self):
        gamedb = MockDatabase()
        tribe1 = gamedb.tribe_from_id(id='tribe/1')
        tribe2 = gamedb.tribe_from_id(id='tribe/2')
        tribe1_count = gamedb.count_players(from_tribe=tribe1)
        tribe2_count = gamedb.count_players(from_tribe=tribe2)
        tribe3 = self._game._merge_tribes(tribe1=tribe1, tribe2=tribe2,
                                          new_tribe_name='test/tribe3', gamedb=gamedb)
        self.assertEqual(gamedb.count_players(
            from_tribe=tribe3), tribe1_count + tribe2_count)


if __name__ == '__main__':
    unittest.main()
