import json
import logging
import sys
from typing import Text, Union, Any, Dict
import attr
import pytz
from typing import Text
import datetime
from datetime import date
import enum

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class GameError(Exception):
    pass


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
    country: Text = attr.ib()
    country_code: Text = attr.ib()
    game_time_zone: pytz.timezone = attr.ib()
    game_start_day_of_week: ISODayOfWeek = attr.ib()
    game_start_time: datetime.time = attr.ib()
    daily_challenge_start_time: datetime.time = attr.ib()
    daily_challenge_end_time: datetime.time = attr.ib()
    daily_tribal_council_start_time: datetime.time = attr.ib()
    daily_tribal_council_end_time: datetime.time = attr.ib()

    @property
    def tomorrow_localized_string(self) -> Text:
        tomorrow_l = self.game_time_zone.localize(
            datetime.datetime.today() + datetime.timedelta(days=1)
        )
        return tomorrow_l.strftime("%B %d, %Y")

    @property
    def today_localized_string(self) -> Text:
        today_l = self.game_time_zone.localize(
            datetime.datetime.today()
        )
        return today_l.strftime("%B %d, %Y")

    def localized_time_string(self, time: datetime.time) -> Text:
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
    single_tribe_council_time_sec: int = attr.ib(300)
    single_team_council_time_sec: int = attr.ib(300)
    final_tribal_council_time_sec: int = attr.ib(300)
    multi_tribe_min_tribe_size: int = attr.ib(default=10)
    multi_tribe_target_team_size: int = attr.ib(default=5)
    multi_tribe_council_time_sec: int = attr.ib(300)
    multi_tribe_team_immunity_likelihood: float = attr.ib(0.0)
    merge_tribe_name: Text = attr.ib(default='a$apmob')
    single_tribe_top_k_threshold: float = attr.ib(default=0.5)
    game_schedule: GameSchedule = attr.ib(default=None)


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
        log_message('to_dict called for {}'.format(self.__class__))
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


def log_message(message):
    logging.info(message)
