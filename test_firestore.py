import unittest
import mock
from game_engine.firestore import FirestoreDB
import pprint

_TEST_FIRESTORE_INSTANCE_JSON_PATH = './stv-game-db-test-4c0ec2310b2e.json'
# _TEST_FIRESTORE_INSTANCE_JSON_PATH = '/Users/brandontory/Downloads/stv-game-db-test-firebase-adminsdk-h046q-0b2e3c61ca.json'
_TEST_TRIBE_TIGRAWAY_ID = '77TMV9omdLeW7ORvuheX'
_TEST_TRIBE_SIDAMA_ID = 'cbTgYdPh97K6rRTDdEPL'
_TEST_GAME_ID = '7rPwCJaiSkxYgDocGDw1'
_TEST_TEAM_BLUE_ID = 'GQnxhYXnV86oJXLklbGB'
_TEST_TEAM_YELLOW_ID = 'Q09FeEtoIgjNI57Bnl1E'
_TEST_CHALLENGE_KARAOKE_ID = '2JQ5ZvttkFafjxvrN07Q'
_TEST_CHALLENGE_KARAOKE_URL = 'https://www.youtube.com/watch?v=irVIUvDTTB0'
_TEST_YELLOW_TEAM_ACTIVE_PLAYER_ID = '2ZPmDfX9q82KY5PVf1LH'
_TEST_BOSTON_ROB_PLAYER_ID = '2ZPmDfX9q82KY5PVf1LH'

_gamedb = FirestoreDB(
    json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=_TEST_GAME_ID)


class FirestoreDBTest(unittest.TestCase):

    # TODO(brandon): after all the reads are done and the test db is setup, export
    # the whole thing and set it up at the beginning of the unit tests. that way doing
    # things like deactivating players won't matter as much during testing.
    # https://firebase.google.com/docs/firestore/manage-data/export-import

    def test_stream_teams(self):
        teams = _gamedb.stream_teams(
            from_tribe=_gamedb.tribe_from_id(_TEST_TRIBE_TIGRAWAY_ID))
        self.assertListEqual([team.name for team in teams], [
                             'BLUE', 'GREEN', 'RED'])

    def test_stream_entries(self):
        entries = _gamedb.stream_entries(from_tribe=_gamedb.tribe_from_id(_TEST_TRIBE_TIGRAWAY_ID),
                                         from_team=_gamedb.team_from_id(
            _TEST_TEAM_BLUE_ID),
            from_challenge=_gamedb.challenge_from_id(_TEST_CHALLENGE_KARAOKE_ID))
        self.assertListEqual([entry.url for entry in entries], [
                             _TEST_CHALLENGE_KARAOKE_URL])

    def test_count_players(self):
        self.assertEqual(_gamedb.count_players(from_tribe=_gamedb.tribe_from_id(
            _TEST_TRIBE_SIDAMA_ID)), 2)

        self.assertEqual(_gamedb.count_players(
            from_team=_gamedb.team_from_id(_TEST_TEAM_YELLOW_ID)), 2)

    def test_count_teams(self):
        self.assertEqual(_gamedb.count_teams(from_tribe=_gamedb.tribe_from_id(
            _TEST_TRIBE_TIGRAWAY_ID)), 4)

        self.assertEqual(_gamedb.count_teams(), 6)

    def test_count_votes(self):
        votes = _gamedb.count_votes(from_team=_gamedb.team_from_id(
            _TEST_TEAM_YELLOW_ID), is_for_win=False)
        self.assertDictEqual(votes, {
            _TEST_YELLOW_TEAM_ACTIVE_PLAYER_ID: 5
        })

        votes = _gamedb.count_votes(is_for_win=True)
        self.assertDictEqual(votes, {})

    def test_list_challenges(self):
        challenges = _gamedb.list_challenges(
            challenge_completed_predicate_value=False)
        self.assertListEqual([challenge.name for challenge in challenges], [
            'KARAOKE',
            'MOST CREATIVE HOME CLEAN'
        ])

        challenges = _gamedb.list_challenges(
            challenge_completed_predicate_value=True)
        self.assertListEqual([challenge.name for challenge in challenges], [])

    def test_list_players(self):
        players = _gamedb.list_players(
            from_team=_gamedb.team_from_id(_TEST_TEAM_YELLOW_ID))
        self.assertListEqual([player.name for player in players], [
            'Boston Rob',
            'Amber Brkich'
        ])

        players = _gamedb.list_players(from_team=_gamedb.team_from_id(_TEST_TEAM_YELLOW_ID),
                                       active_player_predicate_value=False)
        self.assertListEqual([player.name for player in players], [])

    def test_list_teams(self):
        teams = _gamedb.list_teams()
        self.assertListEqual([team.name for team in teams], [
            'BLUE', 'YELLOW', 'GREEN', 'RED'
        ])

        players = _gamedb.list_players(from_team=_gamedb.team_from_id(_TEST_TEAM_YELLOW_ID),
                                       active_player_predicate_value=False)
        self.assertListEqual([player.name for player in players], [])

    def test_player_from_id(self):
        self.assertEqual(_gamedb.player_from_id(
            _TEST_BOSTON_ROB_PLAYER_ID).name, 'Boston Rob')

    def test_team_from_id(self):
        self.assertEqual(_gamedb.team_from_id(_TEST_TEAM_BLUE_ID).name, 'BLUE')

    def test_tribe_from_id(self):
        self.assertEqual(_gamedb.tribe_from_id(
            _TEST_TRIBE_TIGRAWAY_ID).name, 'TIGRAWAY')

    def test_challenge_from_id(self):
        self.assertEqual(_gamedb.tribe_from_id(
            _TEST_CHALLENGE_KARAOKE_ID).name, 'KARAOKE')


if __name__ == '__main__':
    unittest.main()
