import unittest
import mock
import types
from game import Game
from game import GameOptions
from game_engine.engine import Engine
from game_engine.database import Database, Data
from game_engine.database import Player, Team, Tribe
from game_engine.database import Challenge, Entry, Vote, Ballot
import attr
from typing import Any, Iterable, Dict, Text, Tuple, List, Optional
import uuid
from mock import Mock
import time
import pprint
from multiprocessing import Process
from game_engine import events
from queue import Queue


class MockPlayEngine(Mock):
    def CreateEngine(self, mygamedb):
        def challenge1_worker(gamedb):
            # round 1: [Africa r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [Asia y1 y2 y3 k1 k2 k3 x1 x2 x3]
            # africa wins
            # asia teams vote
            # y votes out y3
            # k votes out k3
            # x votes out x3
            # [Africa r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [Asia y1 y2 k1 k2 x1 x2]
            # asia teams of 2 would deadlock and must merge
            # [Africa r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [Asia y1 y2 k1 k2 x1 x2 (all on k team)]
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=2, views=1, player_id='r1', tribe_id='AFRICA', challenge_id='challenge/1'),
                'entry/2': Entry(id='entry/2', likes=1, views=1, player_id='y1', tribe_id='ASIA', challenge_id='challenge/1'),
            }

        def council1_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='y1', to_id='y3'),
                'vote/2': Vote(id='vote/2', from_id='y2', to_id='y3'),
                'vote/3': Vote(id='vote/3', from_id='y3', to_id='y1'),
                'vote/4': Vote(id='vote/4', from_id='k1', to_id='k3'),
                'vote/5': Vote(id='vote/5', from_id='k2', to_id='k3'),
                'vote/6': Vote(id='vote/6', from_id='k3', to_id='k1'),
                'vote/7': Vote(id='vote/7', from_id='x1', to_id='x3'),
                'vote/8': Vote(id='vote/8', from_id='x2', to_id='x3'),
                'vote/9': Vote(id='vote/9', from_id='x3', to_id='x1'),
            }

        def challenge2_worker(gamedb):
            # round 2: [Africa r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [Asia y1 y2 k1 k2 x1 x2 (all on k team)]
            # asia wins
            # africa teams vote
            # r votes out r3
            # g votes out g3
            # b votes out b3
            # [Africa r1 r2 g1 g2 b1 b2] vs [Asia y1 y2 k1 k2 x1 x2 (all on k team)]
            # africa teams of 2 would deadlock and must merge
            # [Africa r1 r2 g1 g2 b1 b2 (all on team r)] vs [Asia y1 y2 k1 k2 x1 x2 (all on k team)]
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id='AFRICA', challenge_id='challenge/2'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='y1', tribe_id='ASIA', challenge_id='challenge/2'),
            }

        def council2_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='r3'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='r3'),
                'vote/3': Vote(id='vote/3', from_id='r3', to_id='r1'),
                'vote/4': Vote(id='vote/4', from_id='g1', to_id='g3'),
                'vote/5': Vote(id='vote/5', from_id='g2', to_id='g3'),
                'vote/6': Vote(id='vote/6', from_id='g3', to_id='g1'),
                'vote/7': Vote(id='vote/7', from_id='b1', to_id='b3'),
                'vote/8': Vote(id='vote/8', from_id='b2', to_id='b3'),
                'vote/9': Vote(id='vote/9', from_id='b3', to_id='b1'),
            }

        def challenge3_worker(gamedb):
            # round 3: [Africa r1 r2 g1 g2 b1 b2 (all on team r)] vs [Asia y1 y2 k1 k2 x1 x2 (all on k team)]
            # asia wins
            # africa single team votes
            # b2 is voted out
            # [Africa r1 r2 g1 g2 b1 (all on team r)] vs [Asia y1 y2 k1 k2 x1 x2 (all on k team)]
            # africa tribe size has reached minimum, tribes merge
            # [a$apmob (r1 r2 g1 g2 b1) (y1 y2 k1 k2 x1 x2)]
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id='AFRICA', challenge_id='challenge/3'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='y1', tribe_id='ASIA', challenge_id='challenge/3'),
            }

        def council3_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='b2'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='b2'),
                'vote/3': Vote(id='vote/3', from_id='g1', to_id='b2'),
                'vote/4': Vote(id='vote/4', from_id='g2', to_id='b2'),
                'vote/5': Vote(id='vote/5', from_id='b1', to_id='b2'),
                'vote/6': Vote(id='vote/6', from_id='b2', to_id='r1'),
            }

        def challenge4_worker(gamedb):
            # round 4: [a$apmob (team L: r1 r2 g1 g2 b1) (team R: y1 y2 k1 k2 x1 x2)]
            # team L wins
            # team R votes out x2
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=2, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/4'),
                'entry/2': Entry(id='entry/2', likes=1, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/4'),
            }

        def council4_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='y1', to_id='x2'),
                'vote/2': Vote(id='vote/2', from_id='y2', to_id='x2'),
                'vote/3': Vote(id='vote/3', from_id='k1', to_id='x2'),
                'vote/4': Vote(id='vote/4', from_id='k2', to_id='x2'),
                'vote/5': Vote(id='vote/5', from_id='x1', to_id='x2'),
                'vote/6': Vote(id='vote/6', from_id='x2', to_id='x1'),
            }

        def challenge5_worker(gamedb):
            # round 5: [a$apmob (team L: r1 r2 g1 g2 b1) (team R: y1 y2 k1 k2 x1)]
            # team L wins
            # team R votes out x1
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=2, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/5'),
                'entry/2': Entry(id='entry/2', likes=1, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/5'),
            }

        def council5_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='y1', to_id='x1'),
                'vote/2': Vote(id='vote/2', from_id='y2', to_id='x1'),
                'vote/3': Vote(id='vote/3', from_id='k1', to_id='x1'),
                'vote/4': Vote(id='vote/4', from_id='k2', to_id='x1'),
                'vote/5': Vote(id='vote/5', from_id='x1', to_id='y1'),
            }

        def challenge6_worker(gamedb):
            # round 6: [a$apmob (team L: r1 r2 g1 g2 b1) (team R: y1 y2 k1 k2)]
            # team R wins
            # team L votes out b1
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/6'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/6'),
            }

        def council6_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='b1'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='b1'),
                'vote/3': Vote(id='vote/3', from_id='g1', to_id='b1'),
                'vote/4': Vote(id='vote/4', from_id='g2', to_id='b1'),
                'vote/5': Vote(id='vote/5', from_id='b1', to_id='r1'),
            }

        def challenge7_worker(gamedb):
            # round 7: [a$apmob (team L: r1 r2 g1 g2) (team R: y1 y2 k1 k2)]
            # team R wins
            # team L votes out g2
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/7'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/7'),
            }

        def council7_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='g2'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='g2'),
                'vote/3': Vote(id='vote/3', from_id='g1', to_id='g2'),
                'vote/4': Vote(id='vote/4', from_id='g2', to_id='g1'),
            }

        def challenge8_worker(gamedb):
            # round 8: [a$apmob (team L: r1 r2 g1) (team R: y1 y2 k1 k2)]
            # team R wins
            # team L votes out g1
            # team L would deadlock and must merge
            # a$apmob: r1 r2 y1 y2 k1 k2
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/8'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/8'),
            }

        def council8_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='g1'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='g1'),
                'vote/3': Vote(id='vote/3', from_id='g1', to_id='r1'),
            }

        def challenge9_worker(gamedb):
            # round 9: a$apmob: r1 r2 y1 y2 k1 k2
            # r1 wins immunity
            # team votes out k2
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=6, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/2': Entry(id='entry/2', likes=5, views=1, player_id='r2', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/3': Entry(id='entry/3', likes=4, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/4': Entry(id='entry/4', likes=3, views=1, player_id='y2', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/5': Entry(id='entry/5', likes=2, views=1, player_id='k1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/6': Entry(id='entry/6', likes=1, views=1, player_id='k2', tribe_id=tribe_id, challenge_id='challenge/9'),
            }

        def council9_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='k2'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='k2'),
                'vote/3': Vote(id='vote/3', from_id='y1', to_id='k2'),
                'vote/4': Vote(id='vote/4', from_id='y2', to_id='k2'),
                'vote/5': Vote(id='vote/5', from_id='k1', to_id='k2'),
                'vote/6': Vote(id='vote/6', from_id='k2', to_id='k1'),
            }

        def challenge10_worker(gamedb):
            # round 10: a$apmob: r1 r2 y1 y2 k1
            # r1 wins immunity
            # team votes out k1
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=5, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/2': Entry(id='entry/2', likes=4, views=1, player_id='r2', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/3': Entry(id='entry/3', likes=3, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/4': Entry(id='entry/4', likes=2, views=1, player_id='y2', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/5': Entry(id='entry/5', likes=1, views=1, player_id='k1', tribe_id=tribe_id, challenge_id='challenge/9'),
            }

        def council10_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='k1'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='k1'),
                'vote/3': Vote(id='vote/3', from_id='y1', to_id='k1'),
                'vote/4': Vote(id='vote/4', from_id='y2', to_id='k1'),
                'vote/5': Vote(id='vote/5', from_id='k1', to_id='r1'),
            }

        def challenge11_worker(gamedb):
            # round 11: a$apmob: r1 r2 y1 y2
            # r1 wins immunity
            # team votes out y2
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=4, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/2': Entry(id='entry/2', likes=3, views=1, player_id='r2', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/3': Entry(id='entry/3', likes=2, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/4': Entry(id='entry/4', likes=1, views=1, player_id='y2', tribe_id=tribe_id, challenge_id='challenge/9'),
            }

        def council11_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='y2'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='y2'),
                'vote/3': Vote(id='vote/3', from_id='y1', to_id='y2'),
                'vote/4': Vote(id='vote/4', from_id='y2', to_id='r1'),
            }

        def challenge12_worker(gamedb):
            # round 12: a$apmob: r1 r2 y1
            # y1 wins immunity
            # team votes out r1
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='r2', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/3': Entry(id='entry/3', likes=3, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/9'),
            }

        def council12_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='y1'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='r1'),
                'vote/3': Vote(id='vote/3', from_id='y1', to_id='r1'),
            }

        def challenge13_worker(gamedb):
            # round 13: a$apmob: r2 y1
            # community votes y1 to win (no tribal challenge)
            # y1 wins
            pass

        def council13_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='y1', is_for_win=True),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='y1', is_for_win=True),
                'vote/3': Vote(id='vote/3', from_id='y2', to_id='y1', is_for_win=True),
                'vote/4': Vote(id='vote/4', from_id='k1', to_id='y1', is_for_win=True),
                'vote/5': Vote(id='vote/5', from_id='k2', to_id='y1', is_for_win=True),
            }
        challenge_worker_queue = Queue()
        for worker in [challenge1_worker, challenge2_worker, challenge3_worker, challenge4_worker, challenge5_worker,
                       challenge6_worker, challenge7_worker, challenge8_worker, challenge9_worker, challenge10_worker,
                       challenge11_worker, challenge12_worker, challenge13_worker]:
            challenge_worker_queue.put(worker)

        council_worker_queue = Queue()
        for worker in [council1_worker, council2_worker, council3_worker, council4_worker, council5_worker, council6_worker,
                       council7_worker, council8_worker, council9_worker, council10_worker, council11_worker, council12_worker,
                       council13_worker]:
            council_worker_queue.put(worker)

        def event_fn(event):
            if isinstance(event, events.NotifyTribalChallengeEvent) and not challenge_worker_queue.empty():
                challenge_worker = challenge_worker_queue.get_nowait()
                challenge_worker(mygamedb)
            elif isinstance(event, events.NotifyMultiTribeCouncilEvent) and not council_worker_queue.empty():
                council_worker = council_worker_queue.get_nowait()
                council_worker(mygamedb)
            elif isinstance(event, events.NotifySingleTribeCouncilEvent) and not council_worker_queue.empty():
                council_worker = council_worker_queue.get_nowait()
                council_worker(mygamedb)
            elif isinstance(event, events.NotifySingleTeamCouncilEvent) and not council_worker_queue.empty():
                council_worker = council_worker_queue.get_nowait()
                council_worker(mygamedb)
            elif isinstance(event, events.NotifyFinalTribalCouncilEvent) and not council_worker_queue.empty():
                council_worker = council_worker_queue.get_nowait()
                council_worker(mygamedb)
        eng = Mock()
        eng.add_event = event_fn
        return eng



class MockDatabase(Database):
    def __init__(self):
        self._games = dict()
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
            'team/1': Team(id='team/1', name='name/team1', count_players=4, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', count_players=4, tribe_id='tribe/1'),
            'team/3': Team(id='team/3', name='name/team3', count_players=4, tribe_id='tribe/2'),
            'team/4': Team(id='team/4', name='name/team4', count_players=4, tribe_id='tribe/2'),
            'team/5': Team(id='team/5', name='name/team5', count_players=2, tribe_id='tribe/2'),
            'team/6': Team(id='team/6', name='name/team6', count_players=2, tribe_id='tribe/2'),
            'team/7': Team(id='team/7', name='name/team7', count_players=3, tribe_id='tribe/2')
        }

        self._tribes = {
            'tribe/1': Tribe(id='tribe/1', name='name/tribe1', count_players=8),
            'tribe/2': Tribe(id='tribe/2', name='name/tribe2', count_players=15)
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

        self._games = {
            "7rPwCJaiSkxYgDocGDw1":{
                "count_teams":6,
                "count_players":8,
                "name":"test_game1",
                "country_code":"US",
                "game_has_started": False,
                "id": "7rPwCJaiSkxYgDocGDw1"
            },
            "FFFFFFFFFFFFFFFFFFFF":{
                "count_teams":6,
                "count_players":5,
                "name":"test_game2",
                "country_code":"EU",
                "game_has_started": True,
                "id": "FFFFFFFFFFFFFFFFFFFF"
            }
        }

        self._votes = {}

    def batch_update_tribe(self, from_tribe: Tribe, to_tribe: Tribe) -> None:
        new_active_players_count = 0

        for key in self._teams:
            if self._teams[key].tribe_id == from_tribe.id:
                self._teams[key].tribe_id = to_tribe.id

        for key in self._players:
            if self._players[key].tribe_id == from_tribe.id:
                self._players[key].tribe_id = to_tribe.id
                if self._players[key].active:
                    new_active_players_count = new_active_players_count + 1
        self._tribes[to_tribe.id].count_players = self._tribes[to_tribe.id].count_players + \
            new_active_players_count

    def stream_entries(self, from_tribe: Tribe = None, from_team: Team = None, from_challenge: Challenge = None) -> Iterable[Entry]:
        if from_tribe:
            return [entry for entry in self._entries.values() if
                    (entry.challenge_id == from_challenge.id and entry.tribe_id == from_tribe.id)]

        if from_team:
            players_ids = [player.id for player in self._players.values(
            ) if player.team_id == from_team.id]
            return [entry for entry in self._entries.values() if
                    (entry.challenge_id == from_challenge.id and entry.player_id in players_ids)]

    def stream_teams(self, from_tribe: Tribe,
                     team_size_predicate_value: [int, None] = None,
                     order_by_size=True,
                     descending=False
                     ) -> Iterable[Team]:
        if team_size_predicate_value:
            return sorted([team for team in self._teams.values() if (team.count_players == team_size_predicate_value
                                                                     and team.active
                                                                     and team.tribe_id == from_tribe.id)],
                          key=lambda team: team.count_players, reverse=True)
        else:
            return sorted([team for team in self._teams.values() if (team.active and team.tribe_id == from_tribe.id)],
                          key=lambda team: team.count_players, reverse=True)

    def stream_players(self, active_player_predicate_value: bool = True) -> Iterable[Player]:
        pass

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

    def count_teams(self, from_tribe: Tribe = None, active_team_predicate_value=True) -> int:
        if from_tribe:
            return len([team for team in self._teams.values() if team.tribe_id == from_tribe.id and team.active == active_team_predicate_value])
        else:
            return len([team for team in self._teams.values() if team.active == active_team_predicate_value])

    def deactivate_player(self, player: Player) -> None:
        player.active = False
        self._players[player.id].active = False
        self._teams[player.team_id].count_players = self._teams[player.team_id].count_players - 1
        self._tribes[player.tribe_id].count_players = self._tribes[player.tribe_id].count_players - 1

    def deactivate_team(self, team: Team) -> None:
        team.active = False
        self._teams[team.id].active = False
        pprint.pprint(self._teams)

    def count_votes(self, from_team: Team = None, is_for_win: bool = False) -> Dict[Text, int]:
        player_counts = {}

        if from_team:
            for vote in self._votes.values():
                print(vote)
                voter = self.player_from_id(vote.from_id)
                team = self._teams[voter.team_id]
                if team.id != from_team.id or not voter.active:
                    continue

                if vote.to_id not in player_counts:
                    player_counts[vote.to_id] = 1
                else:
                    player_counts[vote.to_id] = player_counts[vote.to_id] + 1
        else:
            for vote in self._votes.values():
                if not vote.is_for_win:
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

    def game_from_id(self, id: Text) -> Game:
        return self._games[id]

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
            self._players[data.id] = data

        if isinstance(data, Team):
            self._teams[data.id] = data

        if isinstance(data, Challenge):
            self._challenges[data.id] = data

    def find_matchmaker_games(self, region="US") -> list:
        class TestGame(dict):
            class Reference():
                class Stream(dict):
                    def stream(self3):
                        players_dict = self._players
                        players_list = []
                        for key, val in players_dict.items():
                            players_list.append(val)
                        return players_list
                def collection(self2, inp):
                    if inp =="players":
                        return self2.Stream()
            reference = Reference()
            def to_dict(self):
                return self
        filtered = filter(lambda elem: elem[1]['country_code'] == region and not elem[1]['game_has_started'], self._games.items())
        games = list(filtered)
        games_list = []
        for g_tuple in games:
            game = TestGame(g_tuple[1])
            games_list.append(game)
        return games_list

    def ballot(self, player_id: str, challenge_id: str, options: Dict[str, str]) -> None:
        pass

    def find_ballot(self, player: Player) -> Iterable[Ballot]:
        pass

    def find_player(self, phone_number: str) -> Optional[Player]:
        pass



class GameTest(unittest.TestCase):
    def setUp(self):
        self._game = Game(game_id=str(uuid.uuid4()), options=GameOptions(
            game_wait_sleep_interval_sec=0.1,
            tribe_council_time_sec=.2,
            single_tribe_top_k_threshold=0.5,
            multi_tribe_min_tribe_size=5,
            multi_tribe_team_immunity_likelihood=0.0))

    def test_play(self):
        gamedb = MockDatabase()
        engine = Mock()

        # [Africa r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [Asia y1 y2 y3 k1 k2 k3 x1 x2 x3]
        gamedb._players = {
            'r1': Player(id='r1', tribe_id='AFRICA', team_id='r'),
            'r2': Player(id='r2', tribe_id='AFRICA', team_id='r'),
            'r3': Player(id='r3', tribe_id='AFRICA', team_id='r'),
            'g1': Player(id='g1', tribe_id='AFRICA', team_id='g'),
            'g2': Player(id='g2', tribe_id='AFRICA', team_id='g'),
            'g3': Player(id='g3', tribe_id='AFRICA', team_id='g'),
            'b1': Player(id='b1', tribe_id='AFRICA', team_id='b'),
            'b2': Player(id='b2', tribe_id='AFRICA', team_id='b'),
            'b3': Player(id='b3', tribe_id='AFRICA', team_id='b'),
            'y1': Player(id='y1', tribe_id='ASIA', team_id='y'),
            'y2': Player(id='y2', tribe_id='ASIA', team_id='y'),
            'y3': Player(id='y3', tribe_id='ASIA', team_id='y'),
            'k1': Player(id='k1', tribe_id='ASIA', team_id='k'),
            'k2': Player(id='k2', tribe_id='ASIA', team_id='k'),
            'k3': Player(id='k3', tribe_id='ASIA', team_id='k'),
            'x1': Player(id='x1', tribe_id='ASIA', team_id='x'),
            'x2': Player(id='x2', tribe_id='ASIA', team_id='x'),
            'x3': Player(id='x3', tribe_id='ASIA', team_id='x'),
        }

        gamedb._teams = {
            'r': Team(id='r', name='name/r', count_players=3, tribe_id='AFRICA'),
            'g': Team(id='g', name='name/g', count_players=3, tribe_id='AFRICA'),
            'b': Team(id='b', name='name/b', count_players=3, tribe_id='AFRICA'),
            'y': Team(id='y', name='name/y', count_players=3, tribe_id='ASIA'),
            'k': Team(id='k', name='name/k', count_players=3, tribe_id='ASIA'),
            'x': Team(id='x', name='name/x', count_players=3, tribe_id='ASIA'),
        }

        gamedb._tribes = {
            'AFRICA': Tribe(id='AFRICA', name='name/AFRICA', count_players=9),
            'ASIA': Tribe(id='ASIA', name='name/ASIA', count_players=9),
        }

        gamedb._challenges = {
            'challenge/1': Challenge(id='challenge/1', name='name/challenge1'),
            'challenge/2': Challenge(id='challenge/2', name='name/challenge2'),
            'challenge/3': Challenge(id='challenge/3', name='name/challenge3'),
            'challenge/4': Challenge(id='challenge/4', name='name/challenge4'),
            'challenge/5': Challenge(id='challenge/5', name='name/challenge5'),
            'challenge/6': Challenge(id='challenge/6', name='name/challenge6'),
            'challenge/7': Challenge(id='challenge/7', name='name/challenge7'),
            'challenge/8': Challenge(id='challenge/8', name='name/challenge8'),
            'challenge/10': Challenge(id='challenge/9', name='name/challenge9'),
            'challenge/11': Challenge(id='challenge/10', name='name/challenge10'),
            'challenge/12': Challenge(id='challenge/11', name='name/challenge11'),
            'challenge/13': Challenge(id='challenge/12', name='name/challenge12'),
            'challenge/14': Challenge(id='challenge/13', name='name/challenge13'),
            'challenge/15': Challenge(id='challenge/14', name='name/challenge14'),
        }

        gamedb._entries = {}

        def challenge1_worker(gamedb):
            # round 1: [Africa r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [Asia y1 y2 y3 k1 k2 k3 x1 x2 x3]
            # africa wins
            # asia teams vote
            # y votes out y3
            # k votes out k3
            # x votes out x3
            # [Africa r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [Asia y1 y2 k1 k2 x1 x2]
            # asia teams of 2 would deadlock and must merge
            # [Africa r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [Asia y1 y2 k1 k2 x1 x2 (all on k team)]
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=2, views=1, player_id='r1', tribe_id='AFRICA', challenge_id='challenge/1'),
                'entry/2': Entry(id='entry/2', likes=1, views=1, player_id='y1', tribe_id='ASIA', challenge_id='challenge/1'),
            }

        def council1_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='y1', to_id='y3'),
                'vote/2': Vote(id='vote/2', from_id='y2', to_id='y3'),
                'vote/3': Vote(id='vote/3', from_id='y3', to_id='y1'),
                'vote/4': Vote(id='vote/4', from_id='k1', to_id='k3'),
                'vote/5': Vote(id='vote/5', from_id='k2', to_id='k3'),
                'vote/6': Vote(id='vote/6', from_id='k3', to_id='k1'),
                'vote/7': Vote(id='vote/7', from_id='x1', to_id='x3'),
                'vote/8': Vote(id='vote/8', from_id='x2', to_id='x3'),
                'vote/9': Vote(id='vote/9', from_id='x3', to_id='x1'),
            }

        def challenge2_worker(gamedb):
            # round 2: [Africa r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [Asia y1 y2 k1 k2 x1 x2 (all on k team)]
            # asia wins
            # africa teams vote
            # r votes out r3
            # g votes out g3
            # b votes out b3
            # [Africa r1 r2 g1 g2 b1 b2] vs [Asia y1 y2 k1 k2 x1 x2 (all on k team)]
            # africa teams of 2 would deadlock and must merge
            # [Africa r1 r2 g1 g2 b1 b2 (all on team r)] vs [Asia y1 y2 k1 k2 x1 x2 (all on k team)]
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id='AFRICA', challenge_id='challenge/2'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='y1', tribe_id='ASIA', challenge_id='challenge/2'),
            }

        def council2_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='r3'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='r3'),
                'vote/3': Vote(id='vote/3', from_id='r3', to_id='r1'),
                'vote/4': Vote(id='vote/4', from_id='g1', to_id='g3'),
                'vote/5': Vote(id='vote/5', from_id='g2', to_id='g3'),
                'vote/6': Vote(id='vote/6', from_id='g3', to_id='g1'),
                'vote/7': Vote(id='vote/7', from_id='b1', to_id='b3'),
                'vote/8': Vote(id='vote/8', from_id='b2', to_id='b3'),
                'vote/9': Vote(id='vote/9', from_id='b3', to_id='b1'),
            }

        def challenge3_worker(gamedb):
            # round 3: [Africa r1 r2 g1 g2 b1 b2 (all on team r)] vs [Asia y1 y2 k1 k2 x1 x2 (all on k team)]
            # asia wins
            # africa single team votes
            # b2 is voted out
            # [Africa r1 r2 g1 g2 b1 (all on team r)] vs [Asia y1 y2 k1 k2 x1 x2 (all on k team)]
            # africa tribe size has reached minimum, tribes merge
            # [a$apmob (r1 r2 g1 g2 b1) (y1 y2 k1 k2 x1 x2)]
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id='AFRICA', challenge_id='challenge/3'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='y1', tribe_id='ASIA', challenge_id='challenge/3'),
            }

        def council3_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='b2'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='b2'),
                'vote/3': Vote(id='vote/3', from_id='g1', to_id='b2'),
                'vote/4': Vote(id='vote/4', from_id='g2', to_id='b2'),
                'vote/5': Vote(id='vote/5', from_id='b1', to_id='b2'),
                'vote/6': Vote(id='vote/6', from_id='b2', to_id='r1'),
            }

        def challenge4_worker(gamedb):
            # round 4: [a$apmob (team L: r1 r2 g1 g2 b1) (team R: y1 y2 k1 k2 x1 x2)]
            # team L wins
            # team R votes out x2
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=2, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/4'),
                'entry/2': Entry(id='entry/2', likes=1, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/4'),
            }

        def council4_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='y1', to_id='x2'),
                'vote/2': Vote(id='vote/2', from_id='y2', to_id='x2'),
                'vote/3': Vote(id='vote/3', from_id='k1', to_id='x2'),
                'vote/4': Vote(id='vote/4', from_id='k2', to_id='x2'),
                'vote/5': Vote(id='vote/5', from_id='x1', to_id='x2'),
                'vote/6': Vote(id='vote/6', from_id='x2', to_id='x1'),
            }

        def challenge5_worker(gamedb):
            # round 5: [a$apmob (team L: r1 r2 g1 g2 b1) (team R: y1 y2 k1 k2 x1)]
            # team L wins
            # team R votes out x1
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=2, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/5'),
                'entry/2': Entry(id='entry/2', likes=1, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/5'),
            }

        def council5_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='y1', to_id='x1'),
                'vote/2': Vote(id='vote/2', from_id='y2', to_id='x1'),
                'vote/3': Vote(id='vote/3', from_id='k1', to_id='x1'),
                'vote/4': Vote(id='vote/4', from_id='k2', to_id='x1'),
                'vote/5': Vote(id='vote/5', from_id='x1', to_id='y1'),
            }

        def challenge6_worker(gamedb):
            # round 6: [a$apmob (team L: r1 r2 g1 g2 b1) (team R: y1 y2 k1 k2)]
            # team R wins
            # team L votes out b1
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/6'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/6'),
            }

        def council6_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='b1'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='b1'),
                'vote/3': Vote(id='vote/3', from_id='g1', to_id='b1'),
                'vote/4': Vote(id='vote/4', from_id='g2', to_id='b1'),
                'vote/5': Vote(id='vote/5', from_id='b1', to_id='r1'),
            }

        def challenge7_worker(gamedb):
            # round 7: [a$apmob (team L: r1 r2 g1 g2) (team R: y1 y2 k1 k2)]
            # team R wins
            # team L votes out g2
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/7'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/7'),
            }

        def council7_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='g2'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='g2'),
                'vote/3': Vote(id='vote/3', from_id='g1', to_id='g2'),
                'vote/4': Vote(id='vote/4', from_id='g2', to_id='g1'),
            }

        def challenge8_worker(gamedb):
            # round 8: [a$apmob (team L: r1 r2 g1) (team R: y1 y2 k1 k2)]
            # team R wins
            # team L votes out g1
            # team L would deadlock and must merge
            # a$apmob: r1 r2 y1 y2 k1 k2
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/8'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/8'),
            }

        def council8_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='g1'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='g1'),
                'vote/3': Vote(id='vote/3', from_id='g1', to_id='r1'),
            }

        def challenge9_worker(gamedb):
            # round 9: a$apmob: r1 r2 y1 y2 k1 k2
            # r1 wins immunity
            # team votes out k2
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=6, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/2': Entry(id='entry/2', likes=5, views=1, player_id='r2', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/3': Entry(id='entry/3', likes=4, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/4': Entry(id='entry/4', likes=3, views=1, player_id='y2', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/5': Entry(id='entry/5', likes=2, views=1, player_id='k1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/6': Entry(id='entry/6', likes=1, views=1, player_id='k2', tribe_id=tribe_id, challenge_id='challenge/9'),
            }

        def council9_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='k2'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='k2'),
                'vote/3': Vote(id='vote/3', from_id='y1', to_id='k2'),
                'vote/4': Vote(id='vote/4', from_id='y2', to_id='k2'),
                'vote/5': Vote(id='vote/5', from_id='k1', to_id='k2'),
                'vote/6': Vote(id='vote/6', from_id='k2', to_id='k1'),
            }

        def challenge10_worker(gamedb):
            # round 10: a$apmob: r1 r2 y1 y2 k1
            # r1 wins immunity
            # team votes out k1
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=5, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/2': Entry(id='entry/2', likes=4, views=1, player_id='r2', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/3': Entry(id='entry/3', likes=3, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/4': Entry(id='entry/4', likes=2, views=1, player_id='y2', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/5': Entry(id='entry/5', likes=1, views=1, player_id='k1', tribe_id=tribe_id, challenge_id='challenge/9'),
            }

        def council10_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='k1'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='k1'),
                'vote/3': Vote(id='vote/3', from_id='y1', to_id='k1'),
                'vote/4': Vote(id='vote/4', from_id='y2', to_id='k1'),
                'vote/5': Vote(id='vote/5', from_id='k1', to_id='r1'),
            }

        def challenge11_worker(gamedb):
            # round 11: a$apmob: r1 r2 y1 y2
            # r1 wins immunity
            # team votes out y2
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=4, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/2': Entry(id='entry/2', likes=3, views=1, player_id='r2', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/3': Entry(id='entry/3', likes=2, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/4': Entry(id='entry/4', likes=1, views=1, player_id='y2', tribe_id=tribe_id, challenge_id='challenge/9'),
            }

        def council11_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='y2'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='y2'),
                'vote/3': Vote(id='vote/3', from_id='y1', to_id='y2'),
                'vote/4': Vote(id='vote/4', from_id='y2', to_id='r1'),
            }

        def challenge12_worker(gamedb):
            # round 12: a$apmob: r1 r2 y1
            # y1 wins immunity
            # team votes out r1
            tribe_id = [tribe for tribe in gamedb._tribes.values()
                        if tribe.name == "a$apmob"][0].id
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='r2', tribe_id=tribe_id, challenge_id='challenge/9'),
                'entry/3': Entry(id='entry/3', likes=3, views=1, player_id='y1', tribe_id=tribe_id, challenge_id='challenge/9'),
            }

        def council12_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='y1'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='r1'),
                'vote/3': Vote(id='vote/3', from_id='y1', to_id='r1'),
            }

        def challenge13_worker(gamedb):
            # round 13: a$apmob: r2 y1
            # community votes y1 to win (no tribal challenge)
            # y1 wins
            pass

        def council13_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='y1', is_for_win=True),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='y1', is_for_win=True),
                'vote/3': Vote(id='vote/3', from_id='y2', to_id='y1', is_for_win=True),
                'vote/4': Vote(id='vote/4', from_id='k1', to_id='y1', is_for_win=True),
                'vote/5': Vote(id='vote/5', from_id='k2', to_id='y1', is_for_win=True),
            }

        challenge_worker_queue = Queue()
        for worker in [challenge1_worker, challenge2_worker, challenge3_worker, challenge4_worker, challenge5_worker,
                       challenge6_worker, challenge7_worker, challenge8_worker, challenge9_worker, challenge10_worker,
                       challenge11_worker, challenge12_worker, challenge13_worker]:
            challenge_worker_queue.put(worker)

        council_worker_queue = Queue()
        for worker in [council1_worker, council2_worker, council3_worker, council4_worker, council5_worker, council6_worker,
                       council7_worker, council8_worker, council9_worker, council10_worker, council11_worker, council12_worker,
                       council13_worker]:
            council_worker_queue.put(worker)

        def event_fn(event):
            if isinstance(event, events.NotifyTribalChallengeEvent) and not challenge_worker_queue.empty():
                challenge_worker = challenge_worker_queue.get_nowait()
                challenge_worker(gamedb)
            elif isinstance(event, events.NotifyMultiTribeCouncilEvent) and not council_worker_queue.empty():
                council_worker = council_worker_queue.get_nowait()
                council_worker(gamedb)
            elif isinstance(event, events.NotifySingleTribeCouncilEvent) and not council_worker_queue.empty():
                council_worker = council_worker_queue.get_nowait()
                council_worker(gamedb)
            elif isinstance(event, events.NotifySingleTeamCouncilEvent) and not council_worker_queue.empty():
                council_worker = council_worker_queue.get_nowait()
                council_worker(gamedb)
            elif isinstance(event, events.NotifyFinalTribalCouncilEvent) and not council_worker_queue.empty():
                council_worker = council_worker_queue.get_nowait()
                council_worker(gamedb)

        engine.add_event = event_fn
        eng = MockPlayEngine().CreateEngine(gamedb)
        winner = self._game.play(tribe1=gamedb.tribe_from_id('AFRICA'), tribe2=gamedb.tribe_from_id('ASIA'),
                                 gamedb=gamedb, engine=eng)

        self.assertEqual(winner, gamedb.player_from_id('y1'))

    def test_play_multi_tribe(self):
        gamedb = MockDatabase()
        engine = Mock()

        # [Tokyo r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [London y1 y2 y3 k1 k2 k3 x1 x2 x3]
        gamedb._players = {
            'r1': Player(id='r1', tribe_id='TOKYO', team_id='r'),
            'r2': Player(id='r2', tribe_id='TOKYO', team_id='r'),
            'r3': Player(id='r3', tribe_id='TOKYO', team_id='r'),
            'g1': Player(id='g1', tribe_id='TOKYO', team_id='g'),
            'g2': Player(id='g2', tribe_id='TOKYO', team_id='g'),
            'g3': Player(id='g3', tribe_id='TOKYO', team_id='g'),
            'b1': Player(id='b1', tribe_id='TOKYO', team_id='b'),
            'b2': Player(id='b2', tribe_id='TOKYO', team_id='b'),
            'b3': Player(id='b3', tribe_id='TOKYO', team_id='b'),
            'y1': Player(id='y1', tribe_id='LONDON', team_id='y'),
            'y2': Player(id='y2', tribe_id='LONDON', team_id='y'),
            'y3': Player(id='y3', tribe_id='LONDON', team_id='y'),
            'k1': Player(id='k1', tribe_id='LONDON', team_id='k'),
            'k2': Player(id='k2', tribe_id='LONDON', team_id='k'),
            'k3': Player(id='k3', tribe_id='LONDON', team_id='k'),
            'x1': Player(id='x1', tribe_id='LONDON', team_id='x'),
            'x2': Player(id='x2', tribe_id='LONDON', team_id='x'),
            'x3': Player(id='x3', tribe_id='LONDON', team_id='x'),
        }

        gamedb._teams = {
            'r': Team(id='r', name='name/r', count_players=3, tribe_id='TOKYO'),
            'g': Team(id='g', name='name/g', count_players=3, tribe_id='TOKYO'),
            'b': Team(id='b', name='name/b', count_players=3, tribe_id='TOKYO'),
            'y': Team(id='y', name='name/y', count_players=3, tribe_id='LONDON'),
            'k': Team(id='k', name='name/k', count_players=3, tribe_id='LONDON'),
            'x': Team(id='x', name='name/x', count_players=3, tribe_id='LONDON'),
        }

        gamedb._tribes = {
            'TOKYO': Tribe(id='TOKYO', name='name/TOKYO', count_players=9),
            'LONDON': Tribe(id='LONDON', name='name/LONDON', count_players=9),
        }

        gamedb._challenges = {
            'challenge/1': Challenge(id='challenge/1', name='name/challenge1'),
            'challenge/2': Challenge(id='challenge/2', name='name/challenge2'),
            'challenge/3': Challenge(id='challenge/3', name='name/challenge3'),
            'challenge/4': Challenge(id='challenge/4', name='name/challenge4'),
        }

        gamedb._entries = {}

        def challenge1_worker(gamedb):
            # round 1: [Tokyo r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [London y1 y2 y3 k1 k2 k3 x1 x2 x3]
            # tokyo wins
            # asia teams vote
            # y votes out y3
            # k votes out k3
            # x votes out x3
            # [Tokyo r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [London y1 y2 k1 k2 x1 x2]
            # asia teams of 2 would deadlock and must merge
            # [Tokyo r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [London y1 y2 k1 k2 x1 x2 (all on k team)]
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=2, views=1, player_id='r1', tribe_id='TOKYO', challenge_id='challenge/1'),
                'entry/2': Entry(id='entry/2', likes=1, views=1, player_id='y1', tribe_id='LONDON', challenge_id='challenge/1'),
            }

        def council1_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='y1', to_id='y3'),
                'vote/2': Vote(id='vote/2', from_id='y2', to_id='y3'),
                'vote/3': Vote(id='vote/3', from_id='y3', to_id='y1'),
                'vote/4': Vote(id='vote/4', from_id='k1', to_id='k3'),
                'vote/5': Vote(id='vote/5', from_id='k2', to_id='k3'),
                'vote/6': Vote(id='vote/6', from_id='k3', to_id='k1'),
                'vote/7': Vote(id='vote/7', from_id='x1', to_id='x3'),
                'vote/8': Vote(id='vote/8', from_id='x2', to_id='x3'),
                'vote/9': Vote(id='vote/9', from_id='x3', to_id='x1'),
            }

        def challenge2_worker(gamedb):
            # round 2: [Tokyo r1 r2 r3 g1 g2 g3 b1 b2 b3] vs [London y1 y2 k1 k2 x1 x2 (all on k team)]
            # london wins
            # tokyo teams vote
            # r votes out r3
            # g votes out g3
            # b votes out b3
            # [Tokyo r1 r2 g1 g2 b1 b2] vs [London y1 y2 k1 k2 x1 x2 (all on k team)]
            # tokyo teams of 2 would deadlock and must merge
            # [Tokyo r1 r2 g1 g2 b1 b2 (all on team r)] vs [London y1 y2 k1 k2 x1 x2 (all on k team)]
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id='TOKYO', challenge_id='challenge/1'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='y1', tribe_id='LONDON', challenge_id='challenge/1'),
            }

        def council2_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='r3'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='r3'),
                'vote/3': Vote(id='vote/3', from_id='r3', to_id='r1'),
                'vote/4': Vote(id='vote/4', from_id='g1', to_id='g3'),
                'vote/5': Vote(id='vote/5', from_id='g2', to_id='g3'),
                'vote/6': Vote(id='vote/6', from_id='g3', to_id='g1'),
                'vote/7': Vote(id='vote/7', from_id='b1', to_id='b3'),
                'vote/8': Vote(id='vote/8', from_id='b2', to_id='b3'),
                'vote/9': Vote(id='vote/9', from_id='b3', to_id='b1'),
            }

        def challenge3_worker(gamedb):
            # round 3: [Tokyo r1 r2 g1 g2 b1 b2 (all on team r)] vs [London y1 y2 k1 k2 x1 x2 (all on k team)]
            # london wins
            # tokyo single team votes
            # b2 is voted out
            # [Tokyo r1 r2 g1 g2 b1 (all on team r)] vs [London y1 y2 k1 k2 x1 x2 (all on k team)]
            # tokyo tribe size has reached minimum, tribes merge
            # [a$apmob (r1 r2 g1 g2 b1) (y1 y2 k1 k2 x1 x2)]
            gamedb._entries = {
                'entry/1': Entry(id='entry/1', likes=1, views=1, player_id='r1', tribe_id='TOKYO', challenge_id='challenge/1'),
                'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='y1', tribe_id='LONDON', challenge_id='challenge/1'),
            }

        def council3_worker(gamedb):
            gamedb._votes = {
                'vote/1': Vote(id='vote/1', from_id='r1', to_id='b2'),
                'vote/2': Vote(id='vote/2', from_id='r2', to_id='b2'),
                'vote/4': Vote(id='vote/4', from_id='g1', to_id='b2'),
                'vote/5': Vote(id='vote/5', from_id='g2', to_id='b2'),
                'vote/7': Vote(id='vote/7', from_id='b1', to_id='b2'),
                'vote/8': Vote(id='vote/8', from_id='b2', to_id='r1'),
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
            elif isinstance(event, events.NotifyMultiTribeCouncilEvent) and not council_worker_queue.empty():
                council_worker = council_worker_queue.get_nowait()
                council_worker(gamedb)

        engine.add_event = event_fn
        tribe = self._game._play_multi_tribe(tribe1=gamedb.tribe_from_id('TOKYO'),
                                             tribe2=gamedb.tribe_from_id('LONDON'), gamedb=gamedb, engine=engine)

        # round 4: [a$apmob (r1 r2 g1 g2 b1) (y1 y2 k1 k2 x1 x2)]
        # single tribe should be returned
        self.assertEqual(tribe.name, self._game._options.merge_tribe_name)
        self.assertListEqual([player.id for player in gamedb._players.values() if player.active and player.tribe_id == tribe.id], [
            'r1', 'r2', 'g1', 'g2', 'b1', 'y1', 'y2', 'k1', 'k2', 'x1', 'x2'
        ])

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
            'red': Team(id='red', name='name/red', count_players=4, tribe_id='tribe/1'),
            'blue': Team(id='blue', name='name/blue', count_players=4, tribe_id='tribe/1'),
        }

        gamedb._tribes = {
            'tribe/1': Tribe(id='tribe/1', name='name/tribe1', count_players=8),
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
            'team/7': Team(id='team/7', name='name/team7', count_players=4, tribe_id='tribe/2')
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

        gamedb._players = {
            'player/1': Player(id='player/1', tribe_id='tribe/1', team_id='team/1'),
            'player/2': Player(id='player/2', tribe_id='tribe/1', team_id='team/1'),
            'player/3': Player(id='player/3', tribe_id='tribe/1', team_id='team/1'),
            'player/4': Player(id='player/4', tribe_id='tribe/1', team_id='team/1'),
            'player/5': Player(id='player/5', tribe_id='tribe/2', team_id='team/2'),
            'player/6': Player(id='player/6', tribe_id='tribe/2', team_id='team/2'),
            'player/7': Player(id='player/7', tribe_id='tribe/2', team_id='team/2'),
            'player/8': Player(id='player/8', tribe_id='tribe/2', team_id='team/2'),
        }

        gamedb._teams = {
            'team/1': Team(id='team/1', name='name/team1', count_players=4, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', count_players=4, tribe_id='tribe/2'),
        }

        gamedb._tribes = {
            'tribe/1': Tribe(id='tribe/1', name='name/tribe1', count_players=4),
            'tribe/2': Tribe(id='tribe/2', name='name/tribe2', count_players=4)
        }

        # inject votes
        gamedb._votes = {
            'vote/5': Vote(id='vote/5', from_id='player/5', to_id='player/8'),
            'vote/6': Vote(id='vote/6', from_id='player/6', to_id='player/8'),
            'vote/7': Vote(id='vote/7', from_id='player/7', to_id='player/8'),
            'vote/8': Vote(id='vote/8', from_id='player/8', to_id='player/5'),
        }

        self._game._run_multi_tribe_council(winning_tribe=gamedb.tribe_from_id('tribe/1'),
                                            losing_tribe=gamedb.tribe_from_id('tribe/2'), gamedb=gamedb, engine=engine)

        engine.add_event.assert_called()
        gamedb.clear_votes.assert_called_once()
        self.assertFalse(gamedb.player_from_id('player/8').active)

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

    def test_run_finalist_tribe_council(self):
        gamedb = MockDatabase()
        gamedb.clear_votes = Mock()
        engine = Mock()

        finalists = {
            'player/01': Player(id='player/01', tribe_id='tribe/1', team_id='team/1'),
            'player/02': Player(id='player/02', tribe_id='tribe/1', team_id='team/1'),
            'player/03': Player(id='player/03', tribe_id='tribe/1', team_id='team/1'),
            'player/04': Player(id='player/04', tribe_id='tribe/1', team_id='team/1'),
        }

        # inject votes
        gamedb._votes = {
            'vote/1': Vote(id='vote/1', from_id='player/01', to_id='player/04', is_for_win=True),
            'vote/2': Vote(id='vote/2', from_id='player/02', to_id='player/04', is_for_win=True),
            'vote/3': Vote(id='vote/3', from_id='player/03', to_id='player/04', is_for_win=True),
            'vote/4': Vote(id='vote/4', from_id='player/04', to_id='player/01', is_for_win=True),
        }

        winner = self._game._run_finalist_tribe_council(
            finalists=finalists, gamedb=gamedb, engine=engine)
        engine.add_event.assert_called()
        self.assertEqual(winner, gamedb._players['player/04'])

    def test_run_single_team_council(self):
        gamedb = MockDatabase()
        gamedb.clear_votes = Mock()
        engine = Mock()

        gamedb._players = {
            'player/1': Player(id='player/1', tribe_id='tribe/1', team_id='team/1'),
            'player/2': Player(id='player/2', tribe_id='tribe/1', team_id='team/1'),
            'player/3': Player(id='player/3', tribe_id='tribe/1', team_id='team/1'),
            'player/4': Player(id='player/4', tribe_id='tribe/1', team_id='team/1'),
        }

        gamedb._teams = {
            'team/1': Team(id='team/1', name='name/team1', count_players=4, tribe_id='tribe/1'),
        }

        gamedb._tribes = {
            'tribe/1': Tribe(id='tribe/1', name='name/tribe1', count_players=4)
        }

        # inject votes
        gamedb._votes = {
            'vote/1': Vote(id='vote/1', from_id='player/1', to_id='player/4'),
            'vote/2': Vote(id='vote/2', from_id='player/2', to_id='player/4'),
            'vote/3': Vote(id='vote/3', from_id='player/3', to_id='player/4'),
            'vote/4': Vote(id='vote/4', from_id='player/4', to_id='player/1'),
        }

        self._game._run_single_team_council(team=gamedb._teams['team/1'], losing_players=[
            gamedb._players['player/2'],
            gamedb._players['player/3'],
            gamedb._players['player/4'],
        ], gamedb=gamedb, engine=engine)
        # TODO(brandon): assert result
        engine.add_event.assert_called()
        self.assertFalse(gamedb._players['player/4'].active)

    def test_merge_teams_2player(self):
        gamedb = MockDatabase()
        engine = Mock()

        gamedb._players = {
            'player/01': Player(id='player/01', tribe_id='tribe/1', team_id='team/1'),
            'player/02': Player(id='player/02', tribe_id='tribe/1', team_id='team/1'),
        }

        gamedb._teams = {
            'team/1': Team(id='team/1', name='name/team1', count_players=1, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', count_players=1, tribe_id='tribe/1'),
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
            'team/1': Team(id='team/1', name='name/team1', count_players=2, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', count_players=1, tribe_id='tribe/1'),
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
            'team/1': Team(id='team/1', name='name/team1', count_players=2, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', count_players=3, tribe_id='tribe/1'),
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
            'team/1': Team(id='team/1', name='name/team1', count_players=3, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', count_players=3, tribe_id='tribe/1'),
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
            'team/1': Team(id='team/1', name='name/team1', count_players=2, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', count_players=2, tribe_id='tribe/1'),
            'team/3': Team(id='team/3', name='name/team3', count_players=2, tribe_id='tribe/1'),
            'team/4': Team(id='team/4', name='name/team4', count_players=3, tribe_id='tribe/1'),
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
            'team/1': Team(id='team/1', name='name/team1', count_players=2, tribe_id='tribe/1'),
            'team/2': Team(id='team/2', name='name/team2', count_players=4, tribe_id='tribe/1'),
            'team/3': Team(id='team/3', name='name/team3', count_players=4, tribe_id='tribe/1'),
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

    def test_get_next_challenge(self):
        gamedb = MockDatabase()
        challenges = set()
        for _ in range(5):
            challenge = self._game._get_next_challenge(gamedb=gamedb)
            challenges.add(challenge.name)
        self.assertSetEqual(challenges, set(
            ['name/challenge1']))

        for _ in range(5):
            challenge = self._game._get_next_challenge(gamedb=gamedb)
            challenges.add(challenge.name)
            gamedb._challenges[challenge.id].complete = True
        self.assertSetEqual(challenges, set(
            ['name/challenge1', 'name/challenge2', 'name/challenge3', 'name/challenge4', 'name/challenge5']))

    def test_run_challenge(self):
        engine = Mock()
        gamedb = MockDatabase()
        challenge = gamedb.challenge_from_id('challenge/1')
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

    def test_score_entries_top_k_players(self):
        engine = Mock()
        gamedb = MockDatabase()
        tribe = gamedb.tribe_from_id('tribe/1')
        challenge = gamedb.challenge_from_id('challenge/1')

        gamedb._players = {
            'player/1': Player(id='player/1', tribe_id='tribe/1', team_id='team/1'),
            'player/2': Player(id='player/2', tribe_id='tribe/1', team_id='team/1'),
            'player/3': Player(id='player/3', tribe_id='tribe/1', team_id='team/1'),
        }

        gamedb._teams = {
            'team/1': Team(id='team/1', name='name/team1', count_players=3, tribe_id='tribe/1'),
        }

        gamedb._entries = {
            'entry/1': Entry(id='entry/1', likes=3, views=1, player_id='player/1', tribe_id='tribe/1', challenge_id='challenge/1'),
            'entry/2': Entry(id='entry/2', likes=2, views=1, player_id='player/2', tribe_id='tribe/1', challenge_id='challenge/1'),
            'entry/3': Entry(id='entry/3', likes=1, views=1, player_id='player/3', tribe_id='tribe/1', challenge_id='challenge/1'),
        }

        losing_players = self._game._score_entries_top_k_players(team=gamedb.team_from_id(
            'team/1'), challenge=challenge, gamedb=gamedb, engine=engine)

        self.assertListEqual(losing_players, [
            gamedb.player_from_id('player/3'),
            gamedb.player_from_id('player/2')
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
