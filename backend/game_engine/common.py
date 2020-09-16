from sentry_sdk import push_scope
from sentry_sdk import configure_scope
from sentry_sdk import capture_message
import sentry_sdk
import json
import logging
import sys
from typing import Union, Any, Dict
import attr
import pytz
import datetime
from datetime import date
import enum

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class GameError(Exception):
    pass


class GameClockMode(enum.Enum):
    # Synchronized timing. Game events are synchronized to global clock,
    # on a schedule which is relative to the timezone of the game initiator.
    # For example, challenges always begin at 9am PST.
    SYNC = 0,

    # Asyncrhonized timing. Game events are relatively timed. For example
    # a challenge may always start N minutes after tribal council. This is only
    # used for test purposes.
    ASYNC = 1


class ISODayOfWeek(enum.Enum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Sunday = 7


@attr.s
class GameSchedule(object):
    country: str = attr.ib()
    country_code: str = attr.ib()
    game_time_zone: pytz.timezone = attr.ib()
    game_start_day_of_week: ISODayOfWeek = attr.ib()
    game_start_time: datetime.time = attr.ib()
    daily_challenge_start_time: datetime.time = attr.ib()
    daily_challenge_end_time: datetime.time = attr.ib()
    daily_tribal_council_start_time: datetime.time = attr.ib()
    daily_tribal_council_end_time: datetime.time = attr.ib()

    @property
    def tomorrow_localized_string(self) -> str:
        tomorrow_l = self.game_time_zone.localize(
            datetime.datetime.today() + datetime.timedelta(days=1)
        )
        return tomorrow_l.strftime("%B %d, %Y")

    @property
    def nextweek_localized_string(self) -> str:
        nextweek_l = self.game_time_zone.localize(
            datetime.datetime.today() + datetime.timedelta(days=7)
        )
        return nextweek_l.strftime("%B %d, %Y")

    @property
    def today_localized_string(self) -> str:
        today_l = self.game_time_zone.localize(
            datetime.datetime.today()
        )
        return today_l.strftime("%B %d, %Y")

    def localized_time_string(self, time: datetime.time) -> str:
        return "{} {}".format(time.strftime("%-I%p"), self.game_time_zone.localize(
            datetime.datetime.now()
        ).tzname())

    def localized_time_delta_sec(self, end_time: datetime.time) -> int:
        now_l = self.game_time_zone.localize(
            datetime.datetime.now()
        )
        end_l = self.game_time_zone.localize(datetime.datetime.combine(
            date=datetime.date.today(),
            time=end_time
        ))
        return (end_l - now_l).total_seconds()

#   USA Programming Schedule
# -------------------------------------------------------------
# US (EST)  12pm Challenge Announced
#           6pm All Submissions Must Be In
#           7pm Winners / Losers Announced, Voting Window Opens
#           9pm Voting Window Closes, Exiles Announced

# US (PST)  9am Challenge Announced
#           3pm All Submissions Must Be In
#           4pm Winners / Losers Announced, Voting Window Opens
#           6pm Voting Window Closes, Exiles Announced
# -------------------------------------------------------------


STV_I18N_TABLE = {
    'US': GameSchedule(
        country='United States',
        country_code='US',
        game_time_zone=pytz.timezone('America/New_York'),
        game_start_day_of_week=ISODayOfWeek.Friday,
        game_start_time=datetime.time(hour=12),
        daily_challenge_start_time=datetime.time(hour=12),
        daily_challenge_end_time=datetime.time(hour=18),
        daily_tribal_council_start_time=datetime.time(hour=19),
        daily_tribal_council_end_time=datetime.time(hour=21),
    ),
    'UK': GameSchedule(
        country='United Kingdom',
        country_code='UK',
        game_time_zone=pytz.timezone('Europe/London'),
        game_start_day_of_week=ISODayOfWeek.Friday,
        game_start_time=datetime.time(hour=12),
        daily_challenge_start_time=datetime.time(hour=12),
        daily_challenge_end_time=datetime.time(hour=18),
        daily_tribal_council_start_time=datetime.time(hour=19),
        daily_tribal_council_end_time=datetime.time(hour=21),
    ),
    'JP': GameSchedule(
        country='Japan',
        country_code='JP',
        game_time_zone=pytz.timezone('Asia/Tokyo'),
        game_start_day_of_week=ISODayOfWeek.Friday,
        game_start_time=datetime.time(hour=12),
        daily_challenge_start_time=datetime.time(hour=12),
        daily_challenge_end_time=datetime.time(hour=18),
        daily_tribal_council_start_time=datetime.time(hour=19),
        daily_tribal_council_end_time=datetime.time(hour=21),
    ),
    'IT': GameSchedule(
        country='Italy',
        country_code='IT',
        game_time_zone=pytz.timezone('Europe/Rome'),
        game_start_day_of_week=ISODayOfWeek.Friday,
        game_start_time=datetime.time(hour=12),
        daily_challenge_start_time=datetime.time(hour=12),
        daily_challenge_end_time=datetime.time(hour=18),
        daily_tribal_council_start_time=datetime.time(hour=19),
        daily_tribal_council_end_time=datetime.time(hour=21),
    ),
    'DE': GameSchedule(
        country='Germany',
        country_code='DE',
        game_time_zone=pytz.timezone('Europe/Berlin'),
        game_start_day_of_week=ISODayOfWeek.Friday,
        game_start_time=datetime.time(hour=12),
        daily_challenge_start_time=datetime.time(hour=12),
        daily_challenge_end_time=datetime.time(hour=18),
        daily_tribal_council_start_time=datetime.time(hour=19),
        daily_tribal_council_end_time=datetime.time(hour=21),
    )
    # TODO: Add support for additional countries
}


@attr.s
class GameOptions(object):
    engine_worker_thread_count: int = attr.ib(default=5)
    engine_worker_sleep_interval_sec: int = attr.ib(default=1)
    game_wait_sleep_interval_sec: int = attr.ib(default=30)
    target_team_size: int = attr.ib(default=5)
    target_finalist_count: int = attr.ib(default=2)
    tribe_council_time_sec: int = attr.ib(300)
    multi_tribe_min_tribe_size: int = attr.ib(default=5)
    multi_tribe_target_team_size: int = attr.ib(default=5)
    multi_tribe_team_immunity_likelihood: float = attr.ib(0.0)
    merge_tribe_name: str = attr.ib(default='a$apmob')
    single_tribe_top_k_threshold: float = attr.ib(default=0.5)
    game_schedule: GameSchedule = attr.ib(default=STV_I18N_TABLE['US'])
    game_clock_mode: GameClockMode = attr.ib(default=GameClockMode.ASYNC)


def _isprimitive(value: Any):
    if (isinstance(value, int) or
            isinstance(value, str) or isinstance(value, float) or isinstance(value, bool)):
        return True
    else:
        return False


class Serializable(object):

    def _to_dict_item(self, v):
        if _isprimitive(v):
            return v
        if isinstance(v, list):
            l = list()
            for item in v:
                l.append(self._to_dict_item(item))
            return l
        elif isinstance(v, Serializable):
            return v.to_dict()
        elif isinstance(v, GameOptions):
            pass
        else:
            raise GameError(
                'Serializable object contains unsupported attribute {}'.format(v))

    def to_dict(self):
        d = {'class': self.__class__.__name__}
        for k, v in vars(self).items():
            d[k] = self._to_dict_item(v)
        return d

    @classmethod
    def from_dict(cls, json_dict: Dict):
        o = cls()
        for k, v in json_dict.items():
            if k == 'class':
                continue

            if k in attr.fields_dict(cls) and _isprimitive(v):
                setattr(o, k, v)
            else:
                raise GameError(
                    'Unable to instantiate type {} from dict {} with attribute {}={}'.format(str(cls), json_dict, k, v))
        return o

    def to_json(self):
        return json.dumps(self.to_dict())


class GameIntegrationTestLogStream:
    def __init__(self, game_id: str, test_id: str):
        self._game_id = game_id
        self._test_id = test_id
        self._inputs = []
        self._outputs = []

    def add_user_sent_sms(self, request: Dict) -> None:
        self._inputs.append(json.dumps(request))

    def add_user_received_sms(self, user_name: str, message: str) -> None:
        self._outputs.append({'name': user_name, 'message': message})

    def add_user_challenge_entry(self, entry: Serializable) -> None:
        self._inputs.append(entry.to_json())

    def persist(self) -> str:
        return json.dumps({
            "game_id": self._game_id,
            "test_id": self._test_id,
            "inputs": self._inputs,
            "outputs": self._outputs
        })


def init_sentry():
    sentry_sdk.init(dsn='https://7ece3e1e345248a19475ea1ed503d28e@o391894.ingest.sentry.io/5238617',
                    attach_stacktrace=True)


def log_message(message: str, game_id: str = None, additional_tags: Dict = None, push_to_sentry=False):
    if push_to_sentry:
        # Sentry automatically pushes exceptions. To avoid this in local env, only init sentry when needed
        init_sentry()
    with push_scope() as scope:
        if game_id:
            scope.set_tag("game_id", game_id)

        logging.info(message)

        if additional_tags:
            for tag, value in additional_tags.items():
                logging.info("{} -> {}".format(tag, str(value)))
                scope.set_tag(tag, str(value))

        if push_to_sentry:
            capture_message(message)
