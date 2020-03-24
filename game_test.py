import unittest
import mock
from game import Game
from game import GameOptions
from game_engine.engine import Engine
from game_engine.database import Database, Data
from game_engine.database import Player, Team, Tribe
from game_engine.database import Challenge, Entry
import attr
from typing import Any, Iterable, Dict, Text, Tuple, List
import uuid
from mock import Mock
import time
import pprint

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
            'team/1': Team(id='team/1', name='name/team1', size=4),
            'team/2': Team(id='team/2', name='name/team2', size=4),
            'team/3': Team(id='team/3', name='name/team3', size=4),
            'team/4': Team(id='team/4', name='name/team4', size=4),
            'team/5': Team(id='team/5', name='name/team5', size=2),
            'team/6': Team(id='team/6', name='name/team6', size=2),
            'team/7': Team(id='team/7', name='name/team7', size=3)
        }

        self._tribes = {
            'tribe/1': Tribe(id='tribe/1', name='name/tribe1'),
            'tribe/2': Tribe(id='tribe/2', name='name/tribe2')
        }

        self._challenges = {
            'challenge/1': Challenge(id='challenge/1', name='name/challenge1'),
            'challenge/2': Challenge(id='challenge/2', name='name/challenge2'),
            'challenge/3': Challenge(id='challenge/3', name='name/challenge3'),
            'challenge/4': Challenge(id='challenge/4', name='name/challenge4'),
            'challenge/5': Challenge(id='challenge/5', name='name/challenge5'),
        }

        self._entries = {
            'entry/1': Entry(id='entry1', likes=1, views=1, player_id='player/01', tribe_id='tribe/1', challenge_id='challenge/1'),
            'entry/2': Entry(id='entry2', likes=1, views=1, player_id='player/02', tribe_id='tribe/1', challenge_id='challenge/1'),
            'entry/3': Entry(id='entry3', likes=1, views=1, player_id='player/03', tribe_id='tribe/1', challenge_id='challenge/1'),
            'entry/4': Entry(id='entry4', likes=1, views=1, player_id='player/04', tribe_id='tribe/1', challenge_id='challenge/1'),
            'entry/5': Entry(id='entry5', likes=1, views=1, player_id='player/12', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/6': Entry(id='entry6', likes=1, views=1, player_id='player/13', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/7': Entry(id='entry7', likes=1, views=1, player_id='player/14', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/8': Entry(id='entry8', likes=1, views=1, player_id='player/15', tribe_id='tribe/2', challenge_id='challenge/1'),
            'entry/9': Entry(id='entry9', likes=1, views=1, player_id='player/16', tribe_id='tribe/2', challenge_id='challenge/1'),
        }

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
                                                                     and team.active)],
                          key=lambda team: team.size, reverse=True)
        else:
            return sorted([team for team in self._teams.values() if team.active],
                          key=lambda team: team.size, reverse=True)

    def count_players(self, from_tribe: Tribe) -> int:
        count = 0
        for key in self._players:
            if self._players[key].tribe_id == from_tribe.id:
                count = count + 1
        return count

    def deactivate_player(self, player: Player) -> None:
        player.active = False
        self._players[player.id].active = False

    def deactivate_team(self, team: Team) -> None:
        team.active = False
        self._teams[team.id].active = False
        pprint.pprint(self._teams)

    def count_votes(self, from_team: Team) -> Tuple[Player, int]:
        pass

    def clear_votes(self) -> None:
        pass

    def list_challenges(self, challenge_completed_predicate_value=False) -> Iterable[Challenge]:
        return [challenge for challenge in self._challenges.values() if not challenge.complete]

    def list_players(self, from_team: Team) -> Iterable[Player]:
        return [player for player in self._players.values() if player.team_id == from_team.id]

    def player(self, name: Text) -> Player:
        pass

    def player_from_id(self, id: Text) -> Player:
        return self._players[id]

    def tribe(self, name: Text) -> Tribe:
        tribe_id = uuid.uuid1()
        tribe = Tribe(id=tribe_id, name=name)
        self._tribes[tribe_id] = tribe
        return tribe

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
            game_wait_sleep_interval_sec=0.5))
    # def test_play(self):
    # def test_play_multi_tribe(self):
    # def test_play_single_tribe(self):
    # def test_get_voted_out_player(self):
    # def test_run_multi_tribe_council(self):
    # def test_run_single_tribe_council(self):

    def test_merge_teams_2player(self):
        gamedb = MockDatabase()
        engine = Mock()

        gamedb._players = {
            'player/01': Player(id='player/01', tribe_id='tribe/1', team_id='team/1'),
            'player/02': Player(id='player/02', tribe_id='tribe/1', team_id='team/1'),
        }

        gamedb._teams = {
            'team/1': Team(id='team/1', name='name/team1', size=1),
            'team/2': Team(id='team/2', name='name/team2', size=1),
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
            'team/1': Team(id='team/1', name='name/team1', size=2),
            'team/2': Team(id='team/2', name='name/team2', size=1),
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
            'team/1': Team(id='team/1', name='name/team1', size=2),
            'team/2': Team(id='team/2', name='name/team2', size=3),
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
            'player/05': Player(id='player/05', tribe_id='tribe/1', team_id='team/2'),
        }

        gamedb._teams = {
            'team/1': Team(id='team/1', name='name/team1', size=3),
            'team/2': Team(id='team/2', name='name/team2', size=3),
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
            'team/1': Team(id='team/1', name='name/team1', size=2),
            'team/2': Team(id='team/2', name='name/team2', size=2),
            'team/3': Team(id='team/3', name='name/team3', size=2),
            'team/4': Team(id='team/4', name='name/team4', size=3),
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
            'team/1': Team(id='team/1', name='name/team1', size=2),
            'team/2': Team(id='team/2', name='name/team2', size=4),
            'team/3': Team(id='team/3', name='name/team3', size=4),
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
        self._game._run_challenge(challenge=challenge, engine=engine)
        engine.add_event.assert_called_once()

    def test_score_entries(self):
        engine = Mock()
        gamedb = MockDatabase()
        tribe = gamedb.tribe_from_id('tribe/1')
        challenge = gamedb.challenge_from_id('challenge/1')
        self.assertEqual(self._game._score_entries(
            tribe=tribe, challenge=challenge, gamedb=gamedb, engine=engine), 0.5)
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
