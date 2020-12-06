import unittest
from game_engine.common import GameSchedule, STV_I18N_TABLE
import datetime
from datetime import datetime, date, time, timedelta
import pytz


class CommonTest(unittest.TestCase):

    def test_us_today_localized_string(self):
        schedule = STV_I18N_TABLE['US']
        self.assertRegex(
            schedule.today_localized_string,
            "[0-9]+/[0-9]+"
        )

    def test_us_tomorrow_localized_string(self):
        schedule = STV_I18N_TABLE['US']
        self.assertRegex(
            schedule.tomorrow_localized_string,
            "[0-9]+/[0-9]+"
        )

    def test_us_localized_time_string(self):
        schedule = STV_I18N_TABLE['US']
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.game_start_time
            ),
            "12pm (EST|EDT)"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_challenge_start_time
            ),
            "12pm (EST|EDT)"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_challenge_end_time
            ),
            "6pm (EST|EDT)"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_tribal_council_start_time
            ),
            "7pm (EST|EDT)"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_tribal_council_end_time
            ),
            "9pm (EST|EDT)"
        )

    def test_us_localized_time_delta_sec(self):
        schedule = STV_I18N_TABLE['US']
        self.assertAlmostEqual(
            schedule.localized_time_delta_sec(
                end_time=(datetime.now() + timedelta(seconds=5.0)).time()
            ),
            5.0,
            places=3
        )

    def test_uk_today_localized_string(self):
        schedule = STV_I18N_TABLE['UK']
        self.assertRegex(
            schedule.today_localized_string,
            "[0-9]+/[0-9]+"
        )

    def test_uk_tomorrow_localized_string(self):
        schedule = STV_I18N_TABLE['UK']
        self.assertRegex(
            schedule.tomorrow_localized_string,
            "[0-9]+/[0-9]+"
        )

    def test_uk_localized_time_string(self):
        schedule = STV_I18N_TABLE['UK']
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.game_start_time
            ),
            "12pm BST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_challenge_start_time
            ),
            "12pm BST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_challenge_end_time
            ),
            "6pm BST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_tribal_council_start_time
            ),
            "7pm BST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_tribal_council_end_time
            ),
            "9pm BST"
        )

    def test_uk_localized_time_delta_sec(self):
        schedule = STV_I18N_TABLE['UK']
        self.assertAlmostEqual(
            schedule.localized_time_delta_sec(
                end_time=(datetime.now() + timedelta(seconds=5.0)).time()
            ),
            5.0,
            places=3
        )

    def test_jp_today_localized_string(self):
        schedule = STV_I18N_TABLE['JP']
        self.assertRegex(
            schedule.today_localized_string,
            "[0-9]+/[0-9]+"
        )

    def test_jp_tomorrow_localized_string(self):
        schedule = STV_I18N_TABLE['JP']
        self.assertRegex(
            schedule.tomorrow_localized_string,
            "[0-9]+/[0-9]+"
        )

    def test_jp_localized_time_string(self):
        schedule = STV_I18N_TABLE['JP']
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.game_start_time
            ),
            "12pm JST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_challenge_start_time
            ),
            "12pm JST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_challenge_end_time
            ),
            "6pm JST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_tribal_council_start_time
            ),
            "7pm JST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_tribal_council_end_time
            ),
            "9pm JST"
        )

    def test_jp_localized_time_delta_sec(self):
        schedule = STV_I18N_TABLE['JP']
        self.assertAlmostEqual(
            schedule.localized_time_delta_sec(
                end_time=(datetime.now() + timedelta(seconds=5.0)).time()
            ),
            5.0,
            places=3
        )

    def test_it_today_localized_string(self):
        schedule = STV_I18N_TABLE['IT']
        self.assertRegex(
            schedule.today_localized_string,
            "[0-9]+/[0-9]+"
        )

    def test_it_tomorrow_localized_string(self):
        schedule = STV_I18N_TABLE['IT']
        self.assertRegex(
            schedule.tomorrow_localized_string,
            "[0-9]+/[0-9]+"
        )

    def test_it_localized_time_string(self):
        schedule = STV_I18N_TABLE['IT']
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.game_start_time
            ),
            "12pm CEST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_challenge_start_time
            ),
            "12pm CEST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_challenge_end_time
            ),
            "6pm CEST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_tribal_council_start_time
            ),
            "7pm CEST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_tribal_council_end_time
            ),
            "9pm CEST"
        )

    def test_it_localized_time_delta_sec(self):
        schedule = STV_I18N_TABLE['IT']
        self.assertAlmostEqual(
            schedule.localized_time_delta_sec(
                end_time=(datetime.now() + timedelta(seconds=5.0)).time()
            ),
            5.0,
            places=3
        )

    def test_de_today_localized_string(self):
        schedule = STV_I18N_TABLE['DE']
        self.assertRegex(
            schedule.today_localized_string,
            "[0-9]+/[0-9]+"
        )

    def test_de_tomorrow_localized_string(self):
        schedule = STV_I18N_TABLE['DE']
        self.assertRegex(
            schedule.tomorrow_localized_string,
            "[0-9]+/[0-9]+"
        )

    def test_de_localized_time_string(self):
        schedule = STV_I18N_TABLE['DE']
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.game_start_time
            ),
            "12pm CEST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_challenge_start_time
            ),
            "12pm CEST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_challenge_end_time
            ),
            "6pm CEST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_tribal_council_start_time
            ),
            "7pm CEST"
        )
        self.assertRegex(
            schedule.localized_time_string(
                time=schedule.daily_tribal_council_end_time
            ),
            "9pm CEST"
        )

    def test_de_localized_time_delta_sec(self):
        schedule = STV_I18N_TABLE['DE']
        self.assertAlmostEqual(
            schedule.localized_time_delta_sec(
                end_time=(datetime.now() + timedelta(seconds=5.0)).time()
            ),
            5.0,
            places=3
        )

if __name__ == '__main__':
    unittest.main()
