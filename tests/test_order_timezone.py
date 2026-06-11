import datetime as dt
import unittest
from zoneinfo import ZoneInfo

from app.steps_bot.db.repo import build_order_bounds


class OrderTimezoneTest(unittest.TestCase):
    def test_moscow_day_bounds(self) -> None:
        start, end = build_order_bounds(dt.date(2026, 6, 10), dt.date(2026, 6, 10))

        moscow = ZoneInfo("Europe/Moscow")
        self.assertEqual(start, dt.datetime(2026, 6, 10, 0, 0, tzinfo=moscow))
        self.assertEqual(end, dt.datetime(2026, 6, 10, 23, 59, 59, 999999, tzinfo=moscow))
        self.assertEqual(start.astimezone(dt.timezone.utc), dt.datetime(2026, 6, 9, 21, 0, tzinfo=dt.timezone.utc))
        self.assertEqual(end.astimezone(dt.timezone.utc), dt.datetime(2026, 6, 10, 20, 59, 59, 999999, tzinfo=dt.timezone.utc))


if __name__ == "__main__":
    unittest.main()
