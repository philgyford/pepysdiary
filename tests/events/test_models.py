from django.test import TestCase

from pepysdiary.common.utilities import make_date
from pepysdiary.events.factories import DayEventFactory


class DayEventModelsTestCase(TestCase):
    def test_str(self):
        event = DayEventFactory.build(title="My Event")
        self.assertEqual(str(event), "My Event")

    # Testing PepysModel methods

    def test_short_title_exists(self):
        event = DayEventFactory.build(title="My Event")
        self.assertEqual(event.short_title, "My Event")

    def test_get_a_comment_name(self):
        event = DayEventFactory.build()
        self.assertEqual(event.get_a_comment_name(), "a comment")

    # Testing OldDateMixin properties/methods:

    def test_old_dates(self):
        "The properties should return the correct data"
        event = DayEventFactory(diary_date=make_date("1660-01-02"))
        self.assertEqual(event.year, "1660")
        self.assertEqual(event.month, "01")
        self.assertEqual(event.month_b, "Jan")
        self.assertEqual(event.day, "02")
        self.assertEqual(event.day_e, "2")
