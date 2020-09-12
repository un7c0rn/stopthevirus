import unittest
import mock
from game_engine import events
import uuid
import game
from contextlib import contextmanager
from game_engine.firestore import FirestoreDB
from game_engine.matchmaker import GameSimulator
from game_engine import database
import pprint
from game_engine.common import GameOptions, GameSchedule, STV_I18N_TABLE
from game_engine.twilio import TwilioSMSNotifier
import json

_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
_TEST_TWILIO_SMS_CONFIG_PATH = '../twilio/stv-twilio-service-test.json'
_TEST_GAME_ID = "f49f0cfd-c93b-4132-8c5b-ebea4bf81eae"
_TEST_GAME_ENVIRONMENT = """
{
   "games":{
      "7rPwCJaiSkxYgDocGDw1":{
         "id":"7rPwCJaiSkxYgDocGDw1",
         "count_teams":6,
         "count_players":2,
         "name":"test_game1"
      },
      "7rPwCJaiSkxYgDocGDw4":{
         "id":"7rPwCJaiSkxYgDocGDw4",
         "count_teams":6,
         "count_players":2,
         "name":"test_game1"
      },
      "f49f0cfd-c93b-4132-8c5b-ebea4bf81eae":{
         "count_players":20,
         "name":"game/f49f0cfd-c93b-4132-8c5b-ebea4bf81eae",
         "id":"f49f0cfd-c93b-4132-8c5b-ebea4bf81eae",
         "count_teams":4,
         "count_tribes":20,
         "hashtag":"#VIRUSALPHA"
      },
      "i5dlP94NP6vvB2xEyT36":{
         "name":"test_game2",
         "hashtag":"#TestGame1"
      }
   },
   "games/f49f0cfd-c93b-4132-8c5b-ebea4bf81eae/players":{
      "062496c3-b106-48ce-a498-dba2ec271a1c":{
         "team_id":"bbea5ef1-8688-4831-9929-07e3cd7a3f1b",
         "active":true,
         "email":"gary@hostname.com",
         "id":"062496c3-b106-48ce-a498-dba2ec271a1c",
         "tiktok":"gary",
         "class":"Player",
         "phone_number":"751-005-3935",
         "tribe_id":"c4630003-d361-4ff7-a03f-ab6f92afbb81"
      },
      "1a037b16-191c-4890-8c31-9122fe5d6dc1":{
         "tiktok":"sarah",
         "class":"Player",
         "phone_number":"962-582-3407",
         "tribe_id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "team_id":"9da6673f-c687-4c87-9b84-3c1f208bfd39",
         "active":true,
         "email":"sarah@hostname.com",
         "id":"1a037b16-191c-4890-8c31-9122fe5d6dc1"
      },
      "1a450d69-514f-492e-969a-03b9b5389a33":{
         "email":"elizabeth@hostname.com",
         "active":true,
         "id":"1a450d69-514f-492e-969a-03b9b5389a33",
         "tiktok":"elizabeth",
         "class":"Player",
         "phone_number":"388-685-3212",
         "tribe_id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "team_id":"bab66d57-74ad-4c08-b823-65946b160435"
      },
      "21d41310-0d7b-4452-8b6c-e37c76818996":{
         "phone_number":"331-046-5651",
         "class":"Player",
         "tribe_id":"c4630003-d361-4ff7-a03f-ab6f92afbb81",
         "team_id":"42a73a78-170e-45ed-a3eb-402fa844afa1",
         "active":true,
         "email":"charles@hostname.com",
         "id":"21d41310-0d7b-4452-8b6c-e37c76818996",
         "tiktok":"charles"
      },
      "23bead68-79b4-4e58-ae4e-2a7b89ddb347":{
         "tribe_id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "team_id":"bab66d57-74ad-4c08-b823-65946b160435",
         "active":true,
         "email":"donald@hostname.com",
         "id":"23bead68-79b4-4e58-ae4e-2a7b89ddb347",
         "tiktok":"donald",
         "class":"Player",
         "phone_number":"802-722-8425"
      },
      "4d87309f-e1d7-406c-b1ab-799fc35bdc2a":{
         "phone_number":"704-425-0095",
         "class":"Player",
         "tribe_id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "team_id":"bab66d57-74ad-4c08-b823-65946b160435",
         "active":true,
         "email":"denise@hostname.com",
         "id":"4d87309f-e1d7-406c-b1ab-799fc35bdc2a",
         "tiktok":"denise"
      },
      "4f521033-c793-4c95-a055-0ed1db4ca095":{
         "phone_number":"555-259-3255",
         "class":"Player",
         "tribe_id":"c4630003-d361-4ff7-a03f-ab6f92afbb81",
         "team_id":"bbea5ef1-8688-4831-9929-07e3cd7a3f1b",
         "active":true,
         "email":"donna@hostname.com",
         "id":"4f521033-c793-4c95-a055-0ed1db4ca095",
         "tiktok":"donna"
      },
      "5311ce5d-7bbc-4386-8059-83e715f58ce0":{
         "tiktok":"kirk",
         "class":"Player",
         "phone_number":"877-102-2965",
         "tribe_id":"c4630003-d361-4ff7-a03f-ab6f92afbb81",
         "team_id":"bbea5ef1-8688-4831-9929-07e3cd7a3f1b",
         "email":"kirk@hostname.com",
         "active":true,
         "id":"5311ce5d-7bbc-4386-8059-83e715f58ce0"
      },
      "5700835a-9e93-467d-b4c6-8d4d2f4e5158":{
         "tiktok":"juanita",
         "class":"Player",
         "phone_number":"835-161-1468",
         "tribe_id":"c4630003-d361-4ff7-a03f-ab6f92afbb81",
         "team_id":"42a73a78-170e-45ed-a3eb-402fa844afa1",
         "email":"juanita@hostname.com",
         "active":true,
         "id":"5700835a-9e93-467d-b4c6-8d4d2f4e5158"
      },
      "5d3deb3a-eced-4cfb-b1b4-cb3aeb718119":{
         "tribe_id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "team_id":"bab66d57-74ad-4c08-b823-65946b160435",
         "active":true,
         "email":"bruce@hostname.com",
         "id":"5d3deb3a-eced-4cfb-b1b4-cb3aeb718119",
         "tiktok":"bruce",
         "class":"Player",
         "phone_number":"436-038-5365"
      },
      "855d6617-132b-49b0-b4b0-7ab32c092f8f":{
         "tribe_id":"c4630003-d361-4ff7-a03f-ab6f92afbb81",
         "team_id":"bbea5ef1-8688-4831-9929-07e3cd7a3f1b",
         "active":true,
         "email":"neil@hostname.com",
         "id":"855d6617-132b-49b0-b4b0-7ab32c092f8f",
         "tiktok":"neil",
         "phone_number":"994-138-5472",
         "class":"Player"
      },
      "92103da2-45a6-483d-93d5-abe958e086e9":{
         "tribe_id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "team_id":"bab66d57-74ad-4c08-b823-65946b160435",
         "email":"stacy@hostname.com",
         "active":true,
         "id":"92103da2-45a6-483d-93d5-abe958e086e9",
         "tiktok":"stacy",
         "class":"Player",
         "phone_number":"514-721-1531"
      },
      "9d9bae3b-9b01-4a82-9f50-6641f70149fc":{
         "phone_number":"191-221-0517",
         "class":"Player",
         "tribe_id":"c4630003-d361-4ff7-a03f-ab6f92afbb81",
         "team_id":"42a73a78-170e-45ed-a3eb-402fa844afa1",
         "active":true,
         "email":"donna@hostname.com",
         "id":"9d9bae3b-9b01-4a82-9f50-6641f70149fc",
         "tiktok":"donna"
      },
      "aff6a786-e9a0-49b7-bbdf-60c9d628350a":{
         "tiktok":"william",
         "phone_number":"142-175-7280",
         "class":"Player",
         "tribe_id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "team_id":"9da6673f-c687-4c87-9b84-3c1f208bfd39",
         "active":true,
         "email":"william@hostname.com",
         "id":"aff6a786-e9a0-49b7-bbdf-60c9d628350a"
      },
      "d03e3c49-00d6-4a73-a0ac-0396c5f3151b":{
         "tribe_id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "team_id":"9da6673f-c687-4c87-9b84-3c1f208bfd39",
         "email":"karen@hostname.com",
         "active":true,
         "id":"d03e3c49-00d6-4a73-a0ac-0396c5f3151b",
         "tiktok":"karen",
         "class":"Player",
         "phone_number":"312-441-3246"
      },
      "d1d2b75c-2253-412e-b2a1-f1200c51f4f3":{
         "tribe_id":"c4630003-d361-4ff7-a03f-ab6f92afbb81",
         "team_id":"42a73a78-170e-45ed-a3eb-402fa844afa1",
         "active":true,
         "email":"henry@hostname.com",
         "id":"d1d2b75c-2253-412e-b2a1-f1200c51f4f3",
         "tiktok":"henry",
         "class":"Player",
         "phone_number":"114-458-3014"
      },
      "d5394423-a8b1-4ef5-b9e8-c69f1a15c5e7":{
         "id":"d5394423-a8b1-4ef5-b9e8-c69f1a15c5e7",
         "tiktok":"corina",
         "class":"Player",
         "phone_number":"245-228-6657",
         "tribe_id":"c4630003-d361-4ff7-a03f-ab6f92afbb81",
         "team_id":"42a73a78-170e-45ed-a3eb-402fa844afa1",
         "active":true,
         "email":"corina@hostname.com"
      },
      "fbe94385-2818-4a6f-960e-71c21bba5f8b":{
         "tribe_id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "team_id":"9da6673f-c687-4c87-9b84-3c1f208bfd39",
         "active":true,
         "email":"christopher@hostname.com",
         "id":"fbe94385-2818-4a6f-960e-71c21bba5f8b",
         "tiktok":"christopher",
         "class":"Player",
         "phone_number":"917-511-9963"
      },
      "fcc75c03-ec05-4579-a032-683005b3434a":{
         "tiktok":"frank",
         "phone_number":"461-328-0686",
         "class":"Player",
         "tribe_id":"c4630003-d361-4ff7-a03f-ab6f92afbb81",
         "team_id":"bbea5ef1-8688-4831-9929-07e3cd7a3f1b",
         "active":true,
         "email":"frank@hostname.com",
         "id":"fcc75c03-ec05-4579-a032-683005b3434a"
      },
      "ff99a8d9-9a4a-48f2-a9af-96e7f8bd7942":{
         "email":"sonia@hostname.com",
         "active":true,
         "id":"ff99a8d9-9a4a-48f2-a9af-96e7f8bd7942",
         "tiktok":"sonia",
         "class":"Player",
         "phone_number":"381-505-3014",
         "tribe_id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "team_id":"9da6673f-c687-4c87-9b84-3c1f208bfd39"
      }
   },
   "games/f49f0cfd-c93b-4132-8c5b-ebea4bf81eae/teams":{
      "42a73a78-170e-45ed-a3eb-402fa844afa1":{
         "class":"Team",
         "tribe_id":"c4630003-d361-4ff7-a03f-ab6f92afbb81",
         "count_players":5,
         "active":true,
         "id":"42a73a78-170e-45ed-a3eb-402fa844afa1",
         "name":"team/2"
      },
      "9da6673f-c687-4c87-9b84-3c1f208bfd39":{
         "id":"9da6673f-c687-4c87-9b84-3c1f208bfd39",
         "name":"team/3",
         "class":"Team",
         "tribe_id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "count_players":5,
         "active":true
      },
      "bab66d57-74ad-4c08-b823-65946b160435":{
         "tribe_id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "count_players":5,
         "active":true,
         "id":"bab66d57-74ad-4c08-b823-65946b160435",
         "name":"team/1",
         "class":"Team"
      },
      "bbea5ef1-8688-4831-9929-07e3cd7a3f1b":{
         "id":"bbea5ef1-8688-4831-9929-07e3cd7a3f1b",
         "name":"team/0",
         "class":"Team",
         "tribe_id":"c4630003-d361-4ff7-a03f-ab6f92afbb81",
         "count_players":5,
         "active":true
      }
   },
   "games/f49f0cfd-c93b-4132-8c5b-ebea4bf81eae/tribes":{
      "59939070-34e1-4bfd-9a92-5415e2fb4277":{
         "count_players":10,
         "active":true,
         "id":"59939070-34e1-4bfd-9a92-5415e2fb4277",
         "class":"Tribe",
         "name":"tribe/MANESSEH"
      },
      "c4630003-d361-4ff7-a03f-ab6f92afbb81":{
         "id":"c4630003-d361-4ff7-a03f-ab6f92afbb81",
         "class":"Tribe",
         "name":"tribe/ASHER",
         "count_players":10,
         "active":true
      }
   }
}
"""

_gamedb = FirestoreDB(
    json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=_TEST_GAME_ID)
_gamedb.import_collections(collections_json=_TEST_GAME_ENVIRONMENT)


def _event_messages_as_json(messages):
    return json.dumps([m.to_dict() for m in messages])


class SMSMessageUXTest(unittest.TestCase):

    def setUp(self):
        self.game_options = GameOptions()
        self.game_options.game_schedule = STV_I18N_TABLE['US']
        self.twilio = TwilioSMSNotifier(
            json_config_path=_TEST_TWILIO_SMS_CONFIG_PATH,
            game_id=_TEST_GAME_ID)

    def test_notify_player_score_event_msg(self):
        event = events.NotifyPlayerScoreEvent(
            game_id=_TEST_GAME_ID,
            game_options=self.game_options,
            player=_gamedb.player_from_id(
                id="062496c3-b106-48ce-a498-dba2ec271a1c"),
            challenge=database.Challenge(
                name="Most creative way to make a mask.",
                message="Use your imagination to make a mask from items in your home.",
            ),
            entry=database.Entry(),
            points=100
        )

        self.assertEqual(
            _event_messages_as_json(event.messages(gamedb=_gamedb)),
            json.dumps(
                [
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: You scored 100 points with your video! "
                                    "Winning teams for the day will be announced by 6PM EDT.\n"),
                        "recipient_phone_numbers": [
                            "751-005-3935"
                        ]
                    }
                ]
            )
        )

    def test_notify_team_reassignment_event_msg(self):
        event = events.NotifyTeamReassignmentEvent(
            game_id=_TEST_GAME_ID,
            game_options=self.game_options,
            player=_gamedb.player_from_id(
                id="aff6a786-e9a0-49b7-bbdf-60c9d628350a"),
            team=_gamedb.team_from_id(
                id="42a73a78-170e-45ed-a3eb-402fa844afa1")
        )

        self.assertEqual(
            _event_messages_as_json(event.messages(gamedb=_gamedb)),
            json.dumps(
                [
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: You've surved elimination, but your team did not. "
                                    "Here's your new team:\n\nwww.tiktok.com/@charles\n\nwww.tiktok.com/@juanita\n\n"
                                    "www.tiktok.com/@donna\n\nwww.tiktok.com/@henry\n\nwww.tiktok.com/@corina\n\n\n\n\n"
                                    "Next challenge begins tomorrow {tomorrow} at 12PM EDT!\n").format(
                                        tomorrow=self.game_options.game_schedule.tomorrow_localized_string),
                        "recipient_phone_numbers": [
                            "142-175-7280"
                        ]
                    }
                ]
            )
        )

    def test_notify_single_team_council_event_msg(self):
        losing_players = [p for p in _gamedb.list_players(
            from_team=_gamedb.team_from_id(id="bab66d57-74ad-4c08-b823-65946b160435")) if
            p.id != "5d3deb3a-eced-4cfb-b1b4-cb3aeb718119"]
        event = events.NotifySingleTeamCouncilEvent(
            game_id=_TEST_GAME_ID,
            game_options=self.game_options,
            winning_player=_gamedb.player_from_id(
                id="5d3deb3a-eced-4cfb-b1b4-cb3aeb718119"),
            losing_players=losing_players
        )

        self.assertEqual(
            _event_messages_as_json(event.messages(gamedb=_gamedb)),
            json.dumps(
                [
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: bruce (www.tiktok.com/@bruce) has won today's challenge"
                                    " and cannot be voted out! There are now 10 players remaining and you must vote"
                                    " a player out of the game!\nReply by 6PM EDT with the letter of the player you're"
                                    " voting OUT. If you do not reply, your vote will count against you.\n\nA: "
                                    "www.tiktok.com/@donald\n\nB: www.tiktok.com/@denise\n\nC: www.tiktok.com/@stacy\n\n\n\n"),
                        "recipient_phone_numbers": "388-685-3212"
                    },
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: bruce (www.tiktok.com/@bruce) has won today's challenge "
                                    "and cannot be voted out! There are now 10 players remaining and you must vote "
                                    "a player out of the game!\nReply by 6PM EDT with the letter of the player you're "
                                    "voting OUT. If you do not reply, your vote will count against you.\n\nA: "
                                    "www.tiktok.com/@elizabeth\n\nB: www.tiktok.com/@denise\n\nC: www.tiktok.com/@stacy\n\n\n\n"),
                        "recipient_phone_numbers": "802-722-8425"
                    },
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: bruce (www.tiktok.com/@bruce) has won today's challenge"
                                    " and cannot be voted out! There are now 10 players remaining and you must vote "
                                    "a player out of the game!\nReply by 6PM EDT with the letter of the player you're "
                                    "voting OUT. If you do not reply, your vote will count against you.\n\nA: "
                                    "www.tiktok.com/@elizabeth\n\nB: www.tiktok.com/@donald\n\nC: www.tiktok.com/@stacy\n\n\n\n"),
                        "recipient_phone_numbers": "704-425-0095"
                    },
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: bruce (www.tiktok.com/@bruce) has won today's challenge "
                                    "and cannot be voted out! There are now 10 players remaining and you must vote a "
                                    "player out of the game!\nReply by 6PM EDT with the letter of the player you're voting "
                                    "OUT. If you do not reply, your vote will count against you.\n\nA: "
                                    "www.tiktok.com/@elizabeth\n\nB: www.tiktok.com/@donald\n\nC: www.tiktok.com/@denise\n\n\n\n"),
                        "recipient_phone_numbers": "514-721-1531"
                    },
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: Congratulations you have won today's challenge and can not be voted "
                                    "out!\nThere are now 10 players remaining and you must vote a player out of the game.\n"
                                    "Reply by 6PM EDT with the letter of the player you're voting OUT.\n\nA: "
                                    "www.tiktok.com/@elizabeth\n\nB: www.tiktok.com/@donald\n\nC: "
                                    "www.tiktok.com/@denise\n\nD: www.tiktok.com/@stacy\n\n\n\n"),
                        "recipient_phone_numbers": "436-038-5365"
                    }
                ]
            )
        )

    def test_notify_single_tribe_council_event_msg(self):
        event = events.NotifySingleTribeCouncilEvent(
            game_id=_TEST_GAME_ID,
            game_options=self.game_options,
            winning_teams=[
                _gamedb.team_from_id(
                    id="42a73a78-170e-45ed-a3eb-402fa844afa1")
            ],
            losing_teams=[
                _gamedb.team_from_id(
                    id="bbea5ef1-8688-4831-9929-07e3cd7a3f1b")
            ]
        )

        self.assertEqual(
            _event_messages_as_json(event.messages(gamedb=_gamedb)),
            json.dumps(
                [
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: Your team has lost today's challenge and you must vote "
                                    "a player off of your team!\nReply by 9PM EDT with the letter of the player you're "
                                    "voting OUT. If you do not reply, your vote will count against you. \n\nA: "
                                    "www.tiktok.com/@gary\n\nB: www.tiktok.com/@donna\n\nC: "
                                    "www.tiktok.com/@kirk\n\nD: www.tiktok.com/@neil\n\nE: www.tiktok.com/@frank\n\n\n\n"),
                        "recipient_phone_numbers": [
                            "751-005-3935",
                            "555-259-3255",
                            "877-102-2965",
                            "994-138-5472",
                            "461-328-0686"
                        ]
                    },
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: Congratulations! Your team is a winner of today's "
                                    "challenge and none of your team members will be eliminated. Other teams "
                                    "will be voting players out of the game tonight at 9PM EDT.\n\nNext challenge "
                                    "begins tomorrow at 12PM EDT!\"\n"),
                        "recipient_phone_numbers": [
                            "331-046-5651",
                            "835-161-1468",
                            "191-221-0517",
                            "114-458-3014",
                            "245-228-6657"
                        ]
                    }
                ]
            )
        )

    def test_notify_tribal_challenge_event_msg(self):
        event = events.NotifyTribalChallengeEvent(
            game_id=_TEST_GAME_ID,
            game_options=self.game_options,
            challenge=database.Challenge(
                name="Most creative way to make a mask.",
                message="Use your imagination to make a mask from items in your home.",
            )
        )

        self.assertEqual(
            _event_messages_as_json(
                [m for m in event.messages(gamedb=_gamedb)][:2]),
            json.dumps(
                [
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: Your challenge today is \"Most creative way to make a "
                                    "mask.\"! Post a video to your TikTok feed, and use this link to submit it to "
                                    "the game https://https://vir_us.io/challenge-submission/062496c3-b106-48ce-a498-dba2ec271a1c/f49f0cfd-c93b-4132-8c5b-ebea4bf81eae/\n\nAll "
                                    "entries must be submitted by 6PM EDT. Winning teams stay, losing teams must vote someone out. Good luck!\"\n"),
                        "recipient_phone_numbers": [
                            "751-005-3935"
                        ]
                    },
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: Your challenge today is \"Most creative way to make a "
                                    "mask.\"! Post a video to your TikTok feed, and use this link to submit it to "
                                    "the game https://https://vir_us.io/challenge-submission/1a037b16-191c-4890-8c31-9122fe5d6dc1/f49f0cfd-c93b-4132-8c5b-ebea4bf81eae/\n\n"
                                    "All entries must be submitted by 6PM EDT. Winning teams stay, losing teams must vote someone out. Good luck!\"\n"),
                        "recipient_phone_numbers": [
                            "962-582-3407"
                        ]
                    }
                ]
            ))

    def test_notify_multi_tribe_council_event_msg(self):
        event = events.NotifyMultiTribeCouncilEvent(
            game_id=_TEST_GAME_ID,
            game_options=self.game_options,
            winning_tribe=_gamedb.tribe_from_id(
                id="59939070-34e1-4bfd-9a92-5415e2fb4277"),
            losing_tribe=_gamedb.tribe_from_id(
                id="c4630003-d361-4ff7-a03f-ab6f92afbb81")
        )

        self.assertEqual(
            _event_messages_as_json(event.messages(gamedb=_gamedb)),
            json.dumps(
                [
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: Your team's tribe tribe/ASHER has lost today's challenge "
                                    "and you must vote a player off of your team!\nReply by 9PM EDT with the letter "
                                    "of the player you're voting OUT. If you do not reply, your vote will count against "
                                    "you.\n\nA: www.tiktok.com/@charles\n\nB: www.tiktok.com/@juanita\n\nC: "
                                    "www.tiktok.com/@donna\n\nD: www.tiktok.com/@henry\n\nE: www.tiktok.com/@corina\n\n\n\n"),
                        "recipient_phone_numbers": [
                            "331-046-5651",
                            "835-161-1468",
                            "191-221-0517",
                            "114-458-3014",
                            "245-228-6657"
                        ]
                    },
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: Your team's tribe tribe/ASHER has lost today's challenge "
                                    "and you must vote a player off of your team!\nReply by 9PM EDT with the letter of "
                                    "the player you're voting OUT. If you do not reply, your vote will count against you."
                                    "\n\nA: www.tiktok.com/@gary\n\nB: www.tiktok.com/@donna\n\nC: www.tiktok.com/@kirk\n\nD: "
                                    "www.tiktok.com/@neil\n\nE: www.tiktok.com/@frank\n\n\n\n"),
                        "recipient_phone_numbers": [
                            "751-005-3935",
                            "555-259-3255",
                            "877-102-2965",
                            "994-138-5472",
                            "461-328-0686"
                        ]
                    },
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: Congratulations! Your tribe tribe/MANESSEH has won today's "
                                    "challenge and everyone is safe. tribe/ASHER will be voting players out of the "
                                    "game TONIGHT at 9PM EDT.\n\nNext challenge begins tomorrow at 12PM EDT!\"\n"),
                        "recipient_phone_numbers": [
                            "962-582-3407",
                            "142-175-7280",
                            "312-441-3246",
                            "917-511-9963",
                            "381-505-3014",
                            "388-685-3212",
                            "802-722-8425",
                            "704-425-0095",
                            "436-038-5365",
                            "514-721-1531"
                        ]
                    }
                ]
            )
        )

    def test_notify_final_tribal_council_event_msg(self):
        event = events.NotifyFinalTribalCouncilEvent(
            game_id=_TEST_GAME_ID,
            game_options=self.game_options,
            finalists=[
                _gamedb.player_from_id(
                    id="5700835a-9e93-467d-b4c6-8d4d2f4e5158"),
                _gamedb.player_from_id(
                    id="5d3deb3a-eced-4cfb-b1b4-cb3aeb718119"),
            ]
        )

        self.assertEqual(
            _event_messages_as_json(event.messages(gamedb=_gamedb)),
            json.dumps(
                [
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nhttps://vir_us.io Only 2 players remain and it's your chance to vote for "
                                    "a WINNER of #VIRUSALPHA!\nReply by 9PM EDT with the letter of the player you vote to WIN!"
                                    "\n\nA: www.tiktok.com/@juanita\n\nB: www.tiktok.com/@bruce\n\n\n\n"),
                        "recipient_phone_numbers": [
                            "751-005-3935",
                            "962-582-3407",
                            "388-685-3212",
                            "331-046-5651",
                            "802-722-8425",
                            "704-425-0095",
                            "555-259-3255",
                            "877-102-2965",
                            "835-161-1468",
                            "436-038-5365",
                            "994-138-5472",
                            "514-721-1531",
                            "191-221-0517",
                            "142-175-7280",
                            "312-441-3246",
                            "114-458-3014",
                            "245-228-6657",
                            "917-511-9963",
                            "461-328-0686",
                            "381-505-3014"
                        ]
                    }
                ]
            )
        )

    def test_notify_player_voted_out_msg(self):
        event = events.NotifyPlayerVotedOutEvent(
            game_id=_TEST_GAME_ID,
            game_options=self.game_options,
            player=_gamedb.player_from_id(
                id="4f521033-c793-4c95-a055-0ed1db4ca095")
        )

        self.assertEqual(
            _event_messages_as_json(event.messages(gamedb=_gamedb)),
            json.dumps(
                [
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: The tribe has spoken and donna (www.tiktok.com/@donna) "
                                    "has been voted out of the game. Next challenge begins tomorrow at 12PM EDT!\n"),
                        "recipient_phone_numbers": [
                            "751-005-3935",
                            "877-102-2965",
                            "994-138-5472",
                            "461-328-0686"
                        ]
                    },
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: The tribe has spoken. You have been voted out of "
                                    "the game but will still have a chance to help decide the winner!\n"),
                        "recipient_phone_numbers": [
                            "555-259-3255"
                        ]
                    }
                ]
            )
        )

    def test_notify_tribal_council_completion_event_msg(self):
        event = events.NotifyTribalCouncilCompletionEvent(
            game_id=_TEST_GAME_ID,
            game_options=self.game_options
        )
        self.assertEqual(
            _event_messages_as_json(event.messages(gamedb=_gamedb)),
            json.dumps(
                [
                    {
                        "class": "SMSEventMessage",
                        "content": ("\nVIR-US: You have survived elimination!\nNext "
                                    "challenge starts tomorrow {tomorrow} at 12PM EDT.\n").format(
                                        tomorrow=self.game_options.game_schedule.tomorrow_localized_string),
                        "recipient_phone_numbers": [
                            "751-005-3935",
                            "962-582-3407",
                            "388-685-3212",
                            "331-046-5651",
                            "802-722-8425",
                            "704-425-0095",
                            "555-259-3255",
                            "877-102-2965",
                            "835-161-1468",
                            "436-038-5365",
                            "994-138-5472",
                            "514-721-1531",
                            "191-221-0517",
                            "142-175-7280",
                            "312-441-3246",
                            "114-458-3014",
                            "245-228-6657",
                            "917-511-9963",
                            "461-328-0686",
                            "381-505-3014"
                        ]
                    }
                ]
            )
        )

    def test_notify_winner_announcement_event_winner_msg(self):
        event = events.NotifyWinnerAnnouncementEvent(
            game_id=_TEST_GAME_ID,
            game_options=self.game_options,
            winner=_gamedb.player_from_id(
                id="1a037b16-191c-4890-8c31-9122fe5d6dc1")
        )

        self.assertEqual(
            _event_messages_as_json(event.messages(gamedb=_gamedb)),
            json.dumps([
                {
                    "class": "SMSEventMessage",
                    "content": "\nVIR-US: You are the last survivor and WINNER of #VIRUSALPHA!\n",
                    "recipient_phone_numbers": [
                        "962-582-3407"
                    ]
                },
                {
                    "class": "SMSEventMessage",
                    "content": "\nVIR-US: sarah (www.tiktok.com/@sarah) is the last survivor and WINNER of #VIRUSALPHA!\n",
                    "recipient_phone_numbers": [

                    ]
                }
            ])
        )

    def test_notify_immunity_awarded_event_msg(self):
        event = events.NotifyImmunityAwardedEvent(
            game_id=_TEST_GAME_ID,
            game_options=self.game_options,
            team=_gamedb.team_from_id(
                id="42a73a78-170e-45ed-a3eb-402fa844afa1")
        )

        self.assertEqual(
            _event_messages_as_json(event.messages(gamedb=_gamedb)),
            json.dumps([
                {
                    "class": "SMSEventMessage",
                    "content": ("\nVIR-US: You have received immunity and cannot be voted out "
                                "tonight!\nNext challenge starts tomorrow {tomorrow} at 12PM EDT.\n").format(
                                    tomorrow=self.game_options.game_schedule.tomorrow_localized_string
                    ),
                    "recipient_phone_numbers": [
                        "331-046-5651",
                        "835-161-1468",
                        "191-221-0517",
                        "114-458-3014",
                        "245-228-6657"
                    ]
                }
            ])
        )


if __name__ == '__main__':
    unittest.main()
