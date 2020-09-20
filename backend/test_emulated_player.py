import mock
from game_engine.emulated_player import EmulatedPlayer
from game_engine import emulated_player
from game_engine.common import GameIntegrationTestLogStream
import uuid
from parameterized import parameterized
from game_engine import messages
from game_engine.database import Entry, Player
from functions.sms import main as sms_endpoint
from game_engine.firestore import FirestoreDB
import unittest
from game_engine import database

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
_PLAYERS = [
    Player(id='test/id0', tiktok='test/tiktok0'),
    Player(id='test/id1', tiktok='test/tiktok1'),
    Player(id='test/id2', tiktok='test/tiktok2'),
]

_gamedb = FirestoreDB(
    json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH)


class EmulatedPlayerTest(unittest.TestCase):

    def setUp(self):
        self._game_id = str(uuid.uuid4())
        self.test_stream = GameIntegrationTestLogStream(
            game_id=self._game_id,
            test_id=self._game_id
        )
        self._emulated_player = EmulatedPlayer(
            id=str(uuid.uuid4()),
            name='name/foo',
            tiktok='tiktok/bar',
            phone_number='+10000000000',
            test_stream=self.test_stream,
            gamedb=_gamedb)

    @parameterized.expand([
        ('NOTIFY_PLAYER_SCORE_EVENT',
         messages.NOTIFY_PLAYER_SCORE_EVENT_MSG_FMT, False),
        ('NOTIFY_TEAM_REASSIGNMENT_EVENT',
         messages.NOTIFY_TEAM_REASSIGNMENT_EVENT_MSG_FMT, False),
        ('NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_LOSING',
         messages.NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_LOSING_MSG_FMT, True),
        ('NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_WINNING',
         messages.NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_WINNING_MSG_FMT, True),
        ('NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_LOSING',
         messages.NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_LOSING_MSG_FMT, True),
        ('NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_WINNING',
         messages.NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_WINNING_MSG_FMT, False),
        ('NOTIFY_TRIBAL_CHALLENGE_EVENT',
         messages.NOTIFY_TRIBAL_CHALLENGE_EVENT_MSG_FMT, False),
        ('NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_LOSING',
         messages.NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_LOSING_MSG_FMT, True),
        ('NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_WINNING',
         messages.NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_WINNING_MSG_FMT, False),
        ('NOTIFY_FINAL_TRIBAL_COUNCIL_EVENT',
         messages.NOTIFY_FINAL_TRIBAL_COUNCIL_EVENT_MSG_FMT, True),
        ('NOTIFY_PLAYER_VOTED_OUT',
         messages.NOTIFY_PLAYER_VOTED_OUT_MSG_FMT, False),
        ('NOTIFY_PLAYER_VOTED_OUT_TEAM',
         messages.NOTIFY_PLAYER_VOTED_OUT_TEAM_MSG_FMT, False),
        ('NOTIFY_TRIBAL_COUNCIL_COMPLETION_EVENT',
         messages.NOTIFY_TRIBAL_COUNCIL_COMPLETION_EVENT_MSG_FMT, False),
        ('NOTIFY_TEAM_REASSIGNMENT_EVENT',
         messages.NOTIFY_TEAM_REASSIGNMENT_EVENT_MSG_FMT, False),
        ('NOTIFY_TEAM_REASSIGNMENT_EVENT',
         messages.NOTIFY_TEAM_REASSIGNMENT_EVENT_MSG_FMT, False),
        ('NOTIFY_TEAM_REASSIGNMENT_EVENT',
         messages.NOTIFY_TEAM_REASSIGNMENT_EVENT_MSG_FMT, False),
        ('NOTIFY_TEAM_REASSIGNMENT_EVENT',
         messages.NOTIFY_TEAM_REASSIGNMENT_EVENT_MSG_FMT, False),
        ('NOTIFY_GAME_CANCELLED_EVENT',
         messages.NOTIFY_GAME_CANCELLED_EVENT_MSG_FMT, False),
        ('NOTIFY_GAME_RESCHEDULED_EVENT',
         messages.NOTIFY_GAME_RESCHEDULED_EVENT_MSG_FMT, False),
        ('GAME_START',
         messages.GAME_START_MSG_FMT, False),
        ('GAME_WILL_MERGE',
         messages.GAME_WILL_MERGE_MSG_FMT, False),
        ('PLAYER_LEFT_GAME',
         messages.PLAYER_LEFT_GAME_MSG_FMT, False),
        ('VERIFY_START_GAME',
         messages.VERIFY_START_GAME_MSG_FMT, False),
        ('VERIFY_JOIN_GAME',
         messages.VERIFY_JOIN_GAME_MSG_FMT, False)
    ])
    def test_is_voting_option(self, _, message, is_voting_option):
        self.assertEqual(
            emulated_player._is_voting_option(message=message),
            is_voting_option
        )

    @parameterized.expand([
        ('NOTIFY_PLAYER_SCORE_EVENT_MSG',
         messages.NOTIFY_PLAYER_SCORE_EVENT_MSG_FMT, False),
        ('NOTIFY_TEAM_REASSIGNMENT_EVENT_MSG',
         messages.NOTIFY_TEAM_REASSIGNMENT_EVENT_MSG_FMT, False),
        ('NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_LOSING_MSG',
         messages.NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_LOSING_MSG_FMT, False),
        ('NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_WINNING_MSG',
         messages.NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_WINNING_MSG_FMT, False),
        ('NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_LOSING_MSG',
         messages.NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_LOSING_MSG_FMT, False),
        ('NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_WINNING_MSG',
         messages.NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_WINNING_MSG_FMT, False),
        ('NOTIFY_TRIBAL_CHALLENGE_EVENT_MSG',
         messages.NOTIFY_TRIBAL_CHALLENGE_EVENT_MSG_FMT, True),
        ('NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_LOSING_MSG',
         messages.NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_LOSING_MSG_FMT, False),
        ('NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_WINNING_MSG',
         messages.NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_WINNING_MSG_FMT, False),
        ('NOTIFY_FINAL_TRIBAL_COUNCIL_EVENT_MSG',
         messages.NOTIFY_FINAL_TRIBAL_COUNCIL_EVENT_MSG_FMT, False),
        ('NOTIFY_PLAYER_VOTED_OUT_MSG',
         messages.NOTIFY_PLAYER_VOTED_OUT_MSG_FMT, False),
        ('NOTIFY_PLAYER_VOTED_OUT_TEAM_MSG',
         messages.NOTIFY_PLAYER_VOTED_OUT_TEAM_MSG_FMT, False),
        ('NOTIFY_TRIBAL_COUNCIL_COMPLETION_EVENT_MSG',
         messages.NOTIFY_TRIBAL_COUNCIL_COMPLETION_EVENT_MSG_FMT, False),
        ('NOTIFY_WINNER_ANNOUNCEMENT_EVENT_WINNER_MSG',
         messages.NOTIFY_WINNER_ANNOUNCEMENT_EVENT_WINNER_MSG_FMT, False),
        ('NOTIFY_WINNER_ANNOUNCEMENT_EVENT_GENERAL_MSG',
         messages.NOTIFY_WINNER_ANNOUNCEMENT_EVENT_GENERAL_MSG_FMT, False),
        ('NOTIFY_IMMUNITY_AWARDED_EVENT_MSG',
         messages.NOTIFY_IMMUNITY_AWARDED_EVENT_MSG_FMT, False),
        ('NOTIFY_GAME_STARTED_EVENT_MSG',
         messages.NOTIFY_GAME_STARTED_EVENT_MSG_FMT, False),
        ('NOTIFY_GAME_CANCELLED_EVENT_MSG',
         messages.NOTIFY_GAME_CANCELLED_EVENT_MSG_FMT, False),
        ('NOTIFY_GAME_RESCHEDULED_EVENT_MSG',
         messages.NOTIFY_GAME_RESCHEDULED_EVENT_MSG_FMT, False),
        ('GAME_START_MSG', messages.GAME_START_MSG_FMT, False),
        ('GAME_WILL_MERGE_MSG', messages.GAME_WILL_MERGE_MSG_FMT, False),
        ('PLAYER_LEFT_GAME_MSG', messages.PLAYER_LEFT_GAME_MSG_FMT, False),
        ('VERIFY_START_GAME_MSG', messages.VERIFY_START_GAME_MSG_FMT, False),
        ('VERIFY_JOIN_GAME_MSG', messages.VERIFY_JOIN_GAME_MSG_FMT, False)
    ])
    def test_is_challenge(self, _, message, is_challenge):
        self.assertEqual(
            emulated_player._is_challenge(message=message),
            is_challenge
        )

    @parameterized.expand([
        ('NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_LOSING', messages.NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_LOSING_MSG_FMT.format(
            header=messages.VIR_US_SMS_HEADER,
            time='foo',
            options=messages.players_as_formatted_options_map(players=_PLAYERS).formatted_string),
            ['A', 'B', 'C']),
        ('NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_LOSING', messages.NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_LOSING_MSG_FMT.format(
            header=messages.VIR_US_SMS_HEADER,
            time='foo',
            tribe='bar',
            options=messages.players_as_formatted_options_map(players=_PLAYERS).formatted_string),
            ['A', 'B', 'C']),
        ('NOTIFY_FINAL_TRIBAL_COUNCIL_EVENT', messages.NOTIFY_FINAL_TRIBAL_COUNCIL_EVENT_MSG_FMT.format(
            header=messages.VIR_US_SMS_HEADER,
            time='foo',
            players='bar',
            game=str(uuid.uuid4()),
            options=messages.players_as_formatted_options_map(players=_PLAYERS).formatted_string),
            ['A', 'B', 'C']),
    ])
    def test_parse_voting_options(self, _, formatted_message, options):
        self.assertListEqual(
            emulated_player._parse_voting_options(message=formatted_message),
            options
        )

    @parameterized.expand([
        ('NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_LOSING', messages.NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_LOSING_MSG_FMT.format(
            header=messages.VIR_US_SMS_HEADER,
            time='foo',
            options=messages.players_as_formatted_options_map(players=_PLAYERS).formatted_string)),
        ('NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_LOSING', messages.NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_LOSING_MSG_FMT.format(
            header=messages.VIR_US_SMS_HEADER,
            time='foo',
            tribe='bar',
            options=messages.players_as_formatted_options_map(players=_PLAYERS).formatted_string)),
        ('NOTIFY_FINAL_TRIBAL_COUNCIL_EVENT', messages.NOTIFY_FINAL_TRIBAL_COUNCIL_EVENT_MSG_FMT.format(
            header=messages.VIR_US_SMS_HEADER,
            time='foo',
            players='bar',
            game=str(uuid.uuid4()),
            options=messages.players_as_formatted_options_map(players=_PLAYERS).formatted_string)),
    ])
    def test_select_vote_option(self, _, formatted_message):
        self.assertIn(
            self._emulated_player._select_vote_option(formatted_message),
            ['A', 'B', 'C']
        )

    @mock.patch.object(emulated_player, '_challenge_id_from_message', return_value='NOP')
    @mock.patch.object(FirestoreDB, 'player_from_id', return_value=Player(
        id='id/foo',
        tribe_id='tribe/bar',
        team_id='team/ban'
    ))
    def test_entry_for_message(self, *_):
        self.assertTrue(isinstance(
            self._emulated_player._entry_for_message('foo'), Entry))

    @mock.patch.object(emulated_player, '_challenge_id_from_message', return_value='NOP')
    @mock.patch.object(EmulatedPlayer, '_select_vote_option', return_value='NOP')
    @mock.patch.object(FirestoreDB, 'player_from_id', return_value=Player(
        id='id/foo',
        tribe_id='tribe/bar',
        team_id='team/ban'
    ))
    @mock.patch.object(FirestoreDB, 'add_challenge_entry', return_value=None)
    @mock.patch.object(sms_endpoint, 'sms_http', return_value=None)
    def test_message_handler(self, sms_http_fn, add_challenge_entry_fn, player_from_id_fn, *_):
        self._emulated_player.message_handler(
            message=messages.NOTIFY_TRIBAL_CHALLENGE_EVENT_MSG_FMT
        )
        self._emulated_player.message_handler(
            message=messages.NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_LOSING_MSG_FMT
        )
        sms_http_fn.assert_called()
        add_challenge_entry_fn.assert_called()
        player_from_id_fn.assert_called()

    @parameterized.expand([
        ('tksubmit.page.link/AAAAAAB', 'LLLLLLL'),
        ('tksubmit.page.link/AAAAAAA', 'NNNNNNN'),
        ('tksubmit.page.link/ZZZZZZZ', 'YYYYYYY')
    ])
    def test_challenge_id_from_message(self, key, challenge_id):
        database.local_set(key=f'https://{key}', value=challenge_id)
        self.assertEqual(
            emulated_player._challenge_id_from_message(message=key),
            challenge_id
        )


if __name__ == '__main__':
    unittest.main()
