import random
import logging
from datetime import datetime, time
import pytz
import os

class HumanScheduler:
    """
    Simulates human circadian rhythms.
    Determines if the user is 'awake' or 'sleeping' based on timezone and day of week.
    """
    def __init__(self):
        # Get timezone from env or default to UTC
        self.tz_name = os.getenv("TZ", "UTC")
        self.timezone = pytz.timezone(self.tz_name)

        # Probabilities
        self.weekend_skip_prob = 0.85  # 85% chance to skip working on weekends completely

        # Dynamic daily schedule (will be reset each day)
        self.current_day = None
        self.start_hour = 8
        self.end_hour = 21
        self.is_day_off = False

    def _reset_daily_schedule(self, current_date):
        """Randomizes the schedule for the new day to avoid patterns."""
        self.current_day = current_date

        # Randomize start time (e.g., between 07:00 and 10:30)
        self.start_hour = random.uniform(7.0, 10.5)

        # Randomize end time (e.g., between 22:00 and 01:00 next day)
        self.end_hour = random.uniform(22.0, 25.0)   # 25.0 means 01:00 AM next day technically

        # Check for weekend (5=Saturday, 6=Sunday)
        weekday = current_date.weekday()
        if weekday >= 5:
            # Most weekends we do nothing, but sometimes we browse
            self.is_day_off = random.random() < self.weekend_skip_prob
            if not self.is_day_off:
                # On active weekends, we start later and end earlier
                self.start_hour = random.uniform(10.0, 12.0)
                self.end_hour = random.uniform(20.0, 23.0)
                logging.info(f"📅 It's a weekend, but I decided to be active today (Light mode).")
            else:
                logging.info(f"📅 It's a weekend. Taking a day off.")
        else:
            self.is_day_off = False
            logging.info(f"📅 New day schedule: Wake up ~{self.start_hour:.2f}h, Sleep ~{self.end_hour:.2f}h")

    def get_sleep_time(self) -> float:
        """
        Returns the number of seconds to sleep if outside of working hours.
        Returns 0 if we should be active.
        """
        now = datetime.now(self.timezone)

        # Initialize or reset if day changed
        if self.current_day != now.date():
            self._reset_daily_schedule(now.date())

        # If today is a "day off", sleep for a long chunk (e.g., 1 hour checks)
        if self.is_day_off:
            return 3600.0

        current_hour = now.hour + (now.minute / 60.0)

        # Check if we are in the active window (including past midnight)
        is_active = False
        if self.start_hour <= current_hour <= self.end_hour:
            is_active = True
        elif self.end_hour > 24 and current_hour <= (self.end_hour - 24):
            is_active = True

        if is_active:
            return 0.0

        # If not active, determine how long to sleep
        if current_hour < self.start_hour:
            # Check if we just haven't reached the start time yet
            if self.end_hour > 24 and current_hour > (self.end_hour - 24):
                hours_to_wait = self.start_hour - current_hour
                logging.info(f"😴 Finished late night session. Sleeping for {hours_to_wait:.1f} hours.")
                return hours_to_wait * 3600
            elif self.end_hour <= 24:
                hours_to_wait = self.start_hour - current_hour
                logging.info(f"😴 Too early. Sleeping for {hours_to_wait:.1f} hours.")
                return hours_to_wait * 3600

        # Default sleep for late night or gap
        logging.info("😴 Outside active hours. Going to sleep.")
        return 3600.0
