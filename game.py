from multiprocessing import Process

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

    def _get_tribe_size(self, tribe: Tribe):
        pass

    def play(self, tribe1: Tribe, tribe2: Tribe) -> List[Player]:
        last_tribe_standing = self._play_multi_tribe(tribe1, tribe2)
        finalists = self._play_single_tribe(last_tribe_standing)
        # TODO(someone): should the finalist game be manual or completely automated
        # for the pick of who win's the money?

    def _play_multi_tribe(self, tribe1: Tribe, tribe2: Tribe) -> Tribe:
        while (tribe1.size() > MultiTribeGame.MIN_TRIBE_SIZE and 
        tribe2.size() > MultiTribeGame.MIN_TRIBE_SIZE):
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

    # fraction of teams in losing tribe must vote
    def _run_multi_tribe_council(self, winning_tribe: Tribe, losing_tribe: Tribe, gamedb: Database, engine: Engine):
        teams = gamedb.get_teams(tribe=losing_tribe)

        for team in teams:
            immunity_granted = random.random() < MultiTribeGame.IMMUNITY_THRESHOLD
            if not immunity_granted:
                non_immune_teams.append(team)
            else:
                engine.add_event(ImmunityNotificationEvent(team=team))

        # announce winner and tribal council for losing tribe
        engine.add_event(MultiTribeCouncilAnnouncementEvent(winning_tribe=winning_tribe, losing_tribe=losing_tribe))

        tribal_council_start_timestamp = engine_lib.get_unix_timestamp()
        gamdb.reset_all_votes()
        non_immune_teams = list()

        # wait for votes
        while (((engine_lib.get_unix_timestamp() - tribal_council_start_timestamp) 
            < Game.TRIBAL_COUNCIL_INTERVAL_SEC) and not self._stop.is_set()):
            engine_lib.log_message("Waiting for tribal council to end.")
            time.sleep(self._options.game_wait_sleep_interval_sec)

        # count votes
        for team in non_immune_teams:
            voted_out_player = gamedb.get_max_voted_player(team=team)
            gamedb.deactivate_player(player=voted_out_player)
            engine.add_event(VotedOutNotificationEvent(player=player))

        # notify all players of what happened at tribal council
        engine.add_event(TribalCouncilCompletedEvent())
    
    # keep top K teams
    def _run_single_tribe_council(self, winning_teams: List[Team], losing_teams: List[Team],
        gamedb: Database, engine: Engine):
        
        # announce winner and tribal council for losing tribe
        engine.add_event(SingleTribeCouncilAnnouncementEvent(winning_teams=winning_teams, losing_teams=losing_teams))
        tribal_council_start_timestamp = engine_lib.get_unix_timestamp()
        gamdb.reset_all_votes()

        # wait for votes
        while (((engine_lib.get_unix_timestamp() - tribal_council_start_timestamp) 
            < Game.TRIBAL_COUNCIL_INTERVAL_SEC) and not self._stop.is_set()):
            engine_lib.log_message("Waiting for tribal council to end.")
            time.sleep(self._options.game_wait_sleep_interval_sec)

        # count votes
        for team in losing_teams:
            voted_out_player = gamedb.get_max_voted_player(team=team)
            gamedb.deactivate_player(player=voted_out_player)
            engine.add_event(VotedOutNotificationEvent(player=player))

        # notify all players of what happened at tribal council
        engine.add_event(TribalCouncilCompletedEvent())

    def _merge_teams(self, target_team_size: int, tribe: Tribe, gamedb: Database, engine: Engine):
        # team merging is only necessary when the size of the team == 2
        # once a team size == 2, it should be merged with another team. the optimal
        # choice is to keep team sizes as close to the intended size as possible
        
        # find all teams with size = 2, these players need to be merged
        small_teams = gamedb.get_teams(tribe=Tribe, size=2)
        merge_candidates = Queue()
        for team in small_teams:
            for player in gamedb.get_players(team=team):
                merge_candidates.put(player)
                
        # count the team sizes for all remaining teams and sort, with smallest teams first
        teams = gamedb.get_teams(tribe=Tribe)
        sorted_teams = sorted(teams, key=lambda team: team.size())
        for team in sorted_teams:
            members_to_add_count = target_team_size - team.size()

            # for each team (excluding merge candidates), in increasing order of size, continue to
            # merge in members from the merge candidate pool until the team size == target size.
            # once the target size is reached go to the next team. 
            while (members_to_add_count > 0) and not merge_candidates.empty():
                player = merge_candidates.get()
                if player.team_id == team.id:
                    merge_candidates.put(player)
                else:
                    player.team_id = team.id
                    members_to_add_count = members_to_add_count - 1

                    # this one at a time DB paradigm is going to perform awfully
                    # TODO(brandon) batch DB updates once we figure out final DB API.
                    player.save()

                    # notify player of new team assignment
                    engine.add_event(NewTeamAssignmentEvent(player=player, team=team))

    def _get_challenge(self, gamedb: Database) -> Challenge:
        return gamedb.get_next_challenge()

    def _run_challenge(self, challenge: Challenge, engine: Engine):
        # wait for challenge to begin
        while (engine_lib.get_unix_timestamp() < challenge.start_timestamp) and not self._stop.is_set():
            engine_lib.log_message("Waiting {}s for challenge to {} to begin.".format(
                challenge.start_timestamp - engine_lib.get_unix_timestamp(), challenge))
            time.sleep(Game.self._options.game_wait_sleep_interval_sec)
            
        # notify players
        engine.add_event(NewChallengeAnnouncement(challenge=challenge))

        # wait for challenge to end
        while (engine_lib.get_unix_timestamp() < challenge.start_timestamp) and not self._stop.is_set():
            engine_lib.log_message("Waiting {}s for challenge to {} to end.".format(
                challenge.start_timestamp - engine_lib.get_unix_timestamp(), challenge))
            time.sleep(self._options.game_wait_sleep_interval_sec)

    def _score_entries(self, tribe: Tribe, challenge: Challenge, gamedb: Database, engine: Engine):
        # trivial scorer for now.

        score = 0
        players = gamedb.count_players(tribe=tribe)

        # TODO(brandon): note, this is a harder problem at scale. scoring each entry and notifying
        # each individual user of their score in realtime. could require a machine cluster to get right
        # and may be overkill. rethink depending on number of players
        entries = gamedb.get_challenge_entries(tribe=tribe, challenge=challenge)

        # TODO(someone): parallelize w/ async multiprocess pool
        for entry in entries:
            points = entry.likes / entry.views
            player = gamedb.get_player(entry.player_id)
            engine.add_event(ScoreEvent(player=player, entry=entry, points=points))
            score = score + points

        # tribe score = avg score of all tribe members
        return score / players

    def _merge_tribes(self, tribe1: Tribe, tribe2: Tribe, gamedb: Database, new_tribe_name: Text) -> Tribe:
        new_tribe = gamedb.create_tribe(Tribe(name=new_tribe_name))
        gamedb.replace_tribe(tribe1, new_tribe)
        gamedb.replace_tribe(tribe2, new_tribe)
        return new_tribe