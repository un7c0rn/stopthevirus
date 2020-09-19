import attr
import pytz
from typing import Iterable, Dict
import datetime
from dataclasses import dataclass, field
from game_engine.database import Database
from game_engine.database import Player, Challenge, Entry, Team, Tribe
from game_engine.common import GameError

# event message spec
# https://docs.google.com/spreadsheets/d/1sOB5sMfvXaziBMegMmY0I2ANF4Vbu41MNPRwylCr6dY/edit#gid=0

VIR_US_SMS_HEADER = 'TRIBE'
VIR_US_HOSTNAME = 'stopthevirus-alpha.netlify.app'

_SMS_OPTION_LETTER_TABLE = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P'
]

_SMS_MAX_OPTION_COUNT = 16


def game_sms_header(gamedb: Database = None, hashtag: str = None) -> str:
    if gamedb:
        game = gamedb.game_from_id(gamedb.get_game_id())
        hashtag = game.hashtag
    return f'{hashtag}\ntiktok.com/tag/{hashtag}'


@dataclass
class OptionsMap:
    formatted_string: str = ''
    options: Dict[str, str] = field(default_factory=dict)


def _normalize_tiktok_username(username: str) -> str:
    return username.replace('@', '')


def _short_link_from_tiktok_username(username: str) -> str:
    return "tiktok.com/@{}".format(_normalize_tiktok_username(username))


def format_tiktok_username(username: str) -> str:
    return "{}".format(_short_link_from_tiktok_username(username))


def players_as_formatted_list(players: Iterable[Player]) -> str:
    fmt_string = ""
    last_player_index = len(players) - 1
    for i, player in enumerate(players):
        suffix = "\n\n" if i < last_player_index else ""
        fmt_string += "{}{}".format(
            _short_link_from_tiktok_username(player.tiktok), suffix)
    return fmt_string


def players_as_formatted_options_map(players: Iterable[Player], exclude_player: Player = None) -> OptionsMap:
    fmt_string = ""
    option_index = 0
    options = {}

    last_player_index = len(players) - 1
    for n, player in enumerate(players):
        if exclude_player:
            if player.id == exclude_player.id:
                continue

        if option_index >= (_SMS_MAX_OPTION_COUNT - 1):
            raise GameError('The maximum number of in-game options for SMS is {}.'.format(
                _SMS_MAX_OPTION_COUNT))
        option_letter = _SMS_OPTION_LETTER_TABLE[option_index]
        suffix = "\n\n" if n < last_player_index else ""
        fmt_string += "{}. {}{}".format(option_letter,
                                        _short_link_from_tiktok_username(player.tiktok), suffix)
        options[option_letter] = player.id
        option_index += 1
    return OptionsMap(formatted_string=f'{fmt_string}', options=options)


NOTIFY_PLAYER_SCORE_EVENT_MSG_FMT = """
{header}

You scored {points} points with your video.

Winning teams for the day will be announced by {time}.
"""

NOTIFY_TEAM_REASSIGNMENT_EVENT_MSG_FMT = """
{header}

You have survived elimination but your team did not.

Here's your new team:

{team}

Next challenge begins tomorrow {date} at {time}.
"""

NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_LOSING_MSG_FMT = """
{header}

{winner} has won today's challenge and cannot be voted out. There are now {players} players remaining.

Reply by {time} with the letter of the player you're voting OUT.

{options}

If you do not reply your vote will count against you.
"""

NOTIFY_SINGLE_TEAM_COUNCIL_EVENT_WINNING_MSG_FMT = """
{header}

Congratulations!

You have won today's challenge and can not be voted out. There are now {players} players remaining.

Reply by {time} with the letter of the player you're voting OUT.

{options}
"""

NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_LOSING_MSG_FMT = """
{header}

Your team has lost today's challenge and you must vote a player off of your team.

Reply by {time} with the letter of the player you're voting OUT.

{options}

If you do not reply, your vote will count against you.
"""

NOTIFY_SINGLE_TRIBE_COUNCIL_EVENT_WINNING_MSG_FMT = """
{header}

Congratulations!

Your team is a winner of today's challenge and none of your team members will be eliminated.

All other teams will be voting players out of the game tonight at {time}.

Next challenge begins tomorrow at {challenge_time}."
"""

NOTIFY_TRIBAL_CHALLENGE_EVENT_MSG_FMT = """
{header}

Your challenge today is:

"{challenge}"

Post a video to your TikTok feed and use this link to submit it to the game:

{link}

All entries must be submitted by {time}. Winning teams stay, losing teams must vote someone out of the game.

Good luck!
"""

NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_LOSING_MSG_FMT = """
{header}

Your team's tribe {tribe} has lost today's challenge and you must vote a player off of your team.

Reply by {time} with the letter of the player you're voting OUT.

{options}

If you do not reply your vote will count against you.
"""

NOTIFY_MULTI_TRIBE_COUNCIL_EVENT_WINNING_MSG_FMT = """
{header}

Congratulations! Your tribe {winning_tribe} has won today's challenge.

{losing_tribe} will be voting players out of the game TONIGHT at {time}.

Next challenge begins tomorrow at {challenge_time}.
"""

NOTIFY_FINAL_TRIBAL_COUNCIL_EVENT_MSG_FMT = """
{header}

There are only {players} players left and it's your chance to vote for a winner of {game}.

Reply by {time} with the letter of the player you're voting to WIN!

{options}
"""

NOTIFY_PLAYER_VOTED_OUT_MSG_FMT = """
{header}

The tribe has spoken and you have been voted out of the game.

Stay tuned, you still have a chance to vote for the final winner.
"""

NOTIFY_PLAYER_VOTED_OUT_TEAM_MSG_FMT = """
{header}

The tribe has spoken.

{player}

Has been voted out of the game.

Next challenge begins tomorrow at {time}.
"""

NOTIFY_TRIBAL_COUNCIL_COMPLETION_EVENT_MSG_FMT = """
{header}

You have survived elimination.

Next challenge starts tomorrow {date} at {time}.
"""

NOTIFY_WINNER_ANNOUNCEMENT_EVENT_WINNER_MSG_FMT = """
{header}

Congratulations!

You are the last survivor and WINNER of {game}.
"""

NOTIFY_WINNER_ANNOUNCEMENT_EVENT_GENERAL_MSG_FMT = """
{header}

{player} is the last survivor and WINNER of {game}!
"""

NOTIFY_IMMUNITY_AWARDED_EVENT_MSG_FMT = """
{header}

You have received immunity and cannot be voted out tonight.

Next challenge starts tomorrow {date} at {time}.
"""

NOTIFY_GAME_STARTED_EVENT_MSG_FMT = """
{header}

Game {game} has begun. Stay tuned for the first challenge.
"""

NOTIFY_GAME_CANCELLED_EVENT_MSG_FMT = """
{header}

Due to {reason} this game {game} has been cancelled.
"""

NOTIFY_GAME_RESCHEDULED_EVENT_MSG_FMT = """
{header}

Due to {reason} this game {game} has been rescheduled
and will begin on {date} at {time}.
"""

GAME_START_MSG_FMT = """
{header}

Your game {game} has been created and will begin on {date} at {time}.

Invite players to join your game using this link:

{link}

If at least {players} players do not join your game will be cancelled.

To read official rules, see stats, and add challenges to your game please click here:

{info}
"""

GAME_WILL_MERGE_MSG_FMT = """
{header}

Unfortunately, the {game} game has been cancelled.

Start a new game of your own using this link:

{link}
"""

PLAYER_LEFT_GAME_MSG_FMT = """
{header}

You have quit {game}.

You won't be able to rejoin this game but you can still join new games or start a game of your own using this link:

{link}
"""

VERIFY_START_GAME_MSG_FMT = """
{header}

Verify your phone number by clicking this link:

{link}

Your game information and invitation link will
be texted back to you once your phone number is confirmed.
"""

VERIFY_JOIN_GAME_MSG_FMT = """
{header}

Verify your phone number by clicking this link:

{link}

You will be entered into the {game} game and receive
a text with instructions after confirmation.
"""
