from django.test import TestCase

from pepysdiary.common.utilities import make_date
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.events.factories import DayEventFactory
from pepysdiary.events.models import DayEvent
from pepysdiary.events.templatetags.event_tags import (
    events_for_day,
    events_for_day_in_sidebar,
)
from pepysdiary.letters.factories import LetterFactory


class EventsTemplateTagsTestCase(TestCase):
    # The HTML generated for different parts, so we don't have to repeat
    # it in each of the relevant tests.

    dayevents_html = """<h2>John Gadbury’s London Diary</h2>
<ul>
<li>Event 1</li>
<li>Event 2</li>
</ul>
<h2>In Parliament</h2>
<ul>
<li>Event 3</li>
</ul>
<h2>In Earl’s Colne, Essex</h2>
<ul>
<li>Event 4</li>
</ul>
"""

    entries_html = """<h2>In the Diary</h2>
<ul>
<li><a href="/diary/1660/01/01/">Entry 1</a></li>
</ul>
"""

    letters_html = """<h2>Letters</h2>
<ul>
<li><a href="/letters/1660/01/01/letter1/">Letter 1</a></li>
</ul>
"""

    link_html = (
        '<p class="text-right"><small>'
        '<a href="/about/text/#on-this-day">About these events</a>'
        "</small></p>"
    )

    sidebar_start_html = """<aside class="aside-block">
    <header class="aside-header">
        <h1 class="aside-title">Also on this day</h1>
    </header>
    <div class="aside-body">
"""

    sidebar_end_html = """
    </div>
</aside>
"""

    def setUp(self):
        "Some DayEvents, Entries and Letters to use."
        self.date = make_date("1660-01-01")
        DayEventFactory(
            title="Event 1", source=DayEvent.Source.GADBURY, event_date=self.date
        )
        DayEventFactory(
            title="Event 2", source=DayEvent.Source.GADBURY, event_date=self.date
        )
        DayEventFactory(
            title="Event 3", source=DayEvent.Source.PARLIAMENT, event_date=self.date
        )
        DayEventFactory(
            title="Event 4", source=DayEvent.Source.JOSSELIN, event_date=self.date
        )

        EntryFactory(title="Entry 1", diary_date=self.date)

        LetterFactory(title="Letter 1", slug="letter1", letter_date=self.date)

        # Shouldn't be included:
        DayEventFactory(event_date=make_date("1660-01-02"))
        EntryFactory(diary_date=make_date("1660-01-02"))
        LetterFactory(letter_date=make_date("1660-01-02"))

    # Testing events_for_day()

    def test_events_for_day_with_no_exclude(self):
        "If there's no exclude, Entries, DayEvents and Letters should be included."
        html = events_for_day(self.date)

        self.assertEqual(
            html,
            f"{self.entries_html}{self.letters_html}{self.dayevents_html}{self.link_html}",
        )

    def test_events_for_day_with_exclude_entries(self):
        "If exclude='entries', Entries should be omitted"
        html = events_for_day(self.date, exclude="entries")

        self.assertEqual(
            html, f"{self.letters_html}{self.dayevents_html}{self.link_html}"
        )

    def test_events_for_day_with_exclude_letters(self):
        "If exclude='letters', Letters should be omitted"
        html = events_for_day(self.date, exclude="letters")

        self.assertEqual(
            html, f"{self.entries_html}{self.dayevents_html}{self.link_html}"
        )

    def test_events_for_day_with_no_events(self):
        "When there's nothing to show, an empty string should be returned"
        html = events_for_day(make_date("1660-02-01"))
        self.assertEqual(html, "")

    def test_events_for_day_dayevents_with_same_title(self):
        "When DayEvents have the same title they should be grouped."
        date = make_date("1660-02-01")
        DayEventFactory(title="Event", source=DayEvent.Source.GADBURY, event_date=date)
        DayEventFactory(title="Event", source=DayEvent.Source.GADBURY, event_date=date)

        html = events_for_day(make_date("1660-02-01"))

        self.assertEqual(
            html,
            f"""<h2>John Gadbury’s London Diary</h2>
<ul>
<li>Event: <a href="">1</a> <a href="">2</a> </li>
</ul>
{self.link_html}""",
        )

    def test_order(self):
        "The Event.order field should be used to order a Source's events"
        DayEventFactory(
            title="4:14 pm sunset",
            source=DayEvent.Source.TIMEANDDATE,
            event_date=self.date,
            order=2,
        )
        DayEventFactory(
            title="8:02 am sunrise",
            source=DayEvent.Source.TIMEANDDATE,
            event_date=self.date,
            order=1,
        )

        html = events_for_day(make_date("1660-01-01"))
        self.assertInHTML(
            "<li>8:02 am sunrise</li><li>4:14 pm sunset</li>",
            html,
        )

    # Testing events_for_day_in_sidebar()

    def test_events_for_day_in_sidebar_with_no_exclude(self):
        "If there's no exclude, Entries, DayEvents and Letters should be included."
        html = events_for_day_in_sidebar(self.date)

        self.assertEqual(
            html,
            f"{self.sidebar_start_html}{self.entries_html}{self.letters_html}{self.dayevents_html}{self.link_html}{self.sidebar_end_html}",
        )

    def test_events_for_day_in_sidebar_with_exclude_entries(self):
        "If exclude='entries', Entries should be omitted"
        html = events_for_day_in_sidebar(self.date, exclude="entries")

        self.assertEqual(
            html,
            f"{self.sidebar_start_html}{self.letters_html}{self.dayevents_html}{self.link_html}{self.sidebar_end_html}",
        )

    def test_events_for_day_in_sidebar_with_exclude_letters(self):
        "If exclude='letters', Letters should be omitted"
        html = events_for_day_in_sidebar(self.date, exclude="letters")

        self.assertEqual(
            html,
            f"{self.sidebar_start_html}{self.entries_html}{self.dayevents_html}{self.link_html}{self.sidebar_end_html}",
        )

    def test_events_for_day_in_sidebar_with_no_events(self):
        "When there's nothing to show, an empty string should be returned"
        html = events_for_day_in_sidebar(make_date("1660-02-01"))
        self.assertEqual(html, "")
