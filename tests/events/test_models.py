from django.test import TestCase

from pepysdiary.common.utilities import make_date
from pepysdiary.events.factories import DayEventFactory
from pepysdiary.events.models import DayEvent


class DayEventModelsTestCase(TestCase):
    def test_str(self):
        event = DayEventFactory.build(title="My Event")
        self.assertEqual(str(event), "My Event")

    def test_ordering(self):
        "It should return events in chronological order"
        event_1 = DayEventFactory.build(event_date=make_date("1660-01-01"))
        event_2 = DayEventFactory.build(event_date=make_date("1660-01-03"))
        event_3 = DayEventFactory.build(event_date=make_date("1660-01-02"))

        events = DayEvent.objects.all()

        self.assertEqual(events[0], event_1)
        self.assertEqual(events[1], event_3)
        self.assertEqual(events[2], event_2)

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
