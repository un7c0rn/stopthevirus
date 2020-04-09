import math
from typing import Tuple

# Document writes $0.18/100K
# Document reads $0.06/100K
_GCP_COST_PER_WRITE = .18 / 100e3
_GCP_COST_PER_READ = .06 / 100e3
_IMMUNITY_CHANCE = 0.2


def _analyze_cost(players: int, immunity: int, team_size: int, merge1_player_count: int, merge2_player_count: int):
    avg_team_size = team_size
    immunity_chance = immunity
    start_players_count = players
    first_merge_at_num_players = merge1_player_count
    second_merge_at_num_players = merge2_player_count

    # phase 1
    phase1_end_players_count = first_merge_at_num_players
    phi = 1 - ((1 / (2 * avg_team_size)) * (1 - immunity_chance))
    phase1_rounds = math.log(
        phase1_end_players_count / start_players_count, phi)
    print("phase 1 appx rounds = {}.".format(phase1_rounds))

    # every round consists of roughly 1 vote write op + 1 vote read op per active player
    # plus 1 entry write op + 1 entry read op per active player
    # + 1 write op per deactivated player
    # therefore:
    # writes = 2 * active_player + 3 * deactivated_players each round
    # reads = 2 * active_player each round

    writes = 0
    reads = 0
    for round in range(0, math.ceil(phase1_rounds)):
        active_players = start_players_count * math.pow(phi, round)
        deactivated_players = start_players_count - active_players
        writes += 2 * active_players + 3 * deactivated_players
        reads += 2 * active_players

    # phase 2
    P0 = first_merge_at_num_players
    PN = second_merge_at_num_players
    alpha = immunity_chance
    S = avg_team_size
    Z = 1 - alpha
    beta = 1 - (Z/S)
    C = 1 - beta
    n = math.log((PN - (Z/C)) / (P0 - (Z/C)), beta)
    phase2_rounds = n
    phase2_end_players_count = PN
    print("phase 2 appx rounds = {}.".format(phase2_rounds))

    for round in range(0, math.ceil(phase2_rounds)):
        active_players = P0 * \
            math.pow(beta, round) + (Z/C) - Z*math.pow(beta, round)/C
        deactivated_players = P0 - active_players
        writes += 2 * active_players + 3 * deactivated_players
        reads += 2 * active_players

    # phase 3
    phase3_end_players_count = 2  # 2 finalists
    phase3_rounds = phase2_end_players_count - phase3_end_players_count
    print("phase 3 appx rounds = {}.".format(phase3_rounds))

    for round in range(0, math.ceil(phase3_rounds)):
        active_players = phase2_end_players_count - round
        deactivated_players = round
        writes += 2 * active_players + 3 * deactivated_players
        reads += 2 * active_players

    # phase 4
    phase4_rounds = 1  # 1 round to choose between 2 finalists
    writes += start_players_count + 2
    reads += start_players_count + 2

    print("writes: {} reads: {}".format(writes, reads))
    print("game cost: ${}".format(_GCP_COST_PER_WRITE *
                                  writes + _GCP_COST_PER_READ * reads))
    print("game time: {} days.".format(phase1_rounds +
                                       phase2_rounds + phase3_rounds + phase4_rounds))


players = [5e6, 1e6, 500e3, 10e3, 1000]
team_sizes = range(3, 6)
merge2_player_count = [10, 6]

for P in players:
    for T in team_sizes:
        for M2 in merge2_player_count:
            M1 = math.ceil(P/2)
            print('players: {} team_size: {} M1: {} M2: {}'.format(P, T, M1, M2))
            _analyze_cost(players=P, immunity=_IMMUNITY_CHANCE, team_size=T,
                          merge1_player_count=M1, merge2_player_count=M2)
            print('\n\n')
