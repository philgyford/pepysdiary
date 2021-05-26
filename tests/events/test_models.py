from django.test import TestCase

from pepysdiary.events.factories import DayEventFactory


class DayEventModelsTestCase(TestCase):
    def test_str(self):
        event = DayEventFactory(title="My Event")
        self.assertEqual(str(event), "My Event")
