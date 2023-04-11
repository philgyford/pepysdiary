import json
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import DayEvent

# The file that will be created/replaced:
FIXTURE_FILE_PATH = (
    settings.BASE_DIR
    / "pepysdiary"
    / "events"
    / "fixtures"
    / "dayevents_parliament.json"
)

# We prepend this to any links found on the pages that don't start with http:
BASE_URL = "https://www.british-history.ac.uk"

# We discard any events that aren't between these dates, inclusive:
FIRST_DATE = datetime.strptime("1660-01-01", "%Y-%m-%d").date()
LAST_DATE = datetime.strptime("1669-05-31", "%Y-%m-%d").date()

# The URLs that we fetch links from.
# This dict's keys are used for the DayEvent.title field.
URLS = {
    "House of Commons": [
        "https://www.british-history.ac.uk/commons-jrnl/vol7?page=10",
        "https://www.british-history.ac.uk/commons-jrnl/vol7?page=11",
        "https://www.british-history.ac.uk/commons-jrnl/vol8",
        "https://www.british-history.ac.uk/commons-jrnl/vol8?page=1",
        "https://www.british-history.ac.uk/commons-jrnl/vol8?page=2",
        "https://www.british-history.ac.uk/commons-jrnl/vol8?page=3",
        "https://www.british-history.ac.uk/commons-jrnl/vol8?page=4",
        "https://www.british-history.ac.uk/commons-jrnl/vol8?page=5",
        "https://www.british-history.ac.uk/commons-jrnl/vol8?page=6",
        "https://www.british-history.ac.uk/commons-jrnl/vol9",
        "https://www.british-history.ac.uk/commons-jrnl/vol9?page=1",
    ],
    "House of Lords": [
        "https://www.british-history.ac.uk/lords-jrnl/vol11",
        "https://www.british-history.ac.uk/lords-jrnl/vol11?page=1",
        "https://www.british-history.ac.uk/lords-jrnl/vol11?page=2",
        "https://www.british-history.ac.uk/lords-jrnl/vol11?page=3",
        "https://www.british-history.ac.uk/lords-jrnl/vol11?page=4",
        "https://www.british-history.ac.uk/lords-jrnl/vol11?page=5",
        "https://www.british-history.ac.uk/lords-jrnl/vol12",
        "https://www.british-history.ac.uk/lords-jrnl/vol12?page=1",
        "https://www.british-history.ac.uk/lords-jrnl/vol12?page=2",
    ],
}


class Command(BaseCommand):
    """
    Generates a JSON fixture file suitable for importing as DayEvent
    objects linking to British History pages for the Commons and Lords.

    Grabs all of the urls in URLs, and generates a file at FIXTURE_FILE_PATH.

    This could then be loaded into the database as DayEvents:

        ./manage.py loaddata pepysdiary/events/fixtures/dayevents_parliament.json

    BUT FIRST, delete all existing Commons and Lords DayEvents:

        from pepysdiary.events.models import DayEvent
        DayEvent.objects.filter(source=DayEvent.Source.PARLIAMENT).delete()
    """

    help = "Generates a JSON fixture file suitable for importing as DayEvent objects linking to British History pages for the Commons and Lords."  # noqa: E501

    def handle(self, *args, **kwargs):
        data_for_fixture = []

        for place, urls in URLS.items():
            links = self._fetch_links_from_urls(urls)
            link_count = 0

            for link in links:
                if link[1] >= FIRST_DATE and link[1] <= LAST_DATE:
                    data_for_fixture.append(
                        {
                            "pk": None,
                            "model": "events.dayevent",
                            "fields": {
                                "url": link[0],
                                "event_date": link[1].strftime("%Y-%m-%d"),
                                "title": place,
                                "source": DayEvent.Source.PARLIAMENT,
                                # NOTE: These values will actually be used for these
                                # "auto_now" fields:
                                "date_created": timezone.now().strftime(
                                    "%Y-%m-%dT%H:%M:%S%z"
                                ),
                                "date_modified": timezone.now().strftime(
                                    "%Y-%m-%dT%H:%M:%S%z"
                                ),
                            },
                        }
                    )
                    link_count += 1

            self.stdout.write(f"Found {link_count} URLs for {place}")

        with open(FIXTURE_FILE_PATH, "w") as f:
            json.dump(data_for_fixture, f, indent=2)

        self.stdout.write(f"Wrote to {FIXTURE_FILE_PATH}")

    def _fetch_links_from_urls(self, urls):
        """
        Passed a list of URLs, it returns the URLs and dates found in their pages.

        So, it gets each URL passed to it, goes through the table in the page's HTML,
        and gets any URLs it finds whose link text matches our pattern.

        Returns a list of tuples. Each tuple has:
        * Full URL of a dated page
        * A date object
        """
        links = []

        for url in urls:
            self.stdout.write(f"Fetching {url}")
            result = self._fetch_url(url)
            if result["success"] is False:
                self.stderr.write(f"Error fetching: {url}: {result['content']}")
            else:
                links += self._extract_links_from_html(result["content"])
            # Be nice:
            time.sleep(1)

        return links

    def _extract_links_from_html(self, html):
        """
        Given the HTML of a page, returns the links and dates.

        Returns a list of tuples. Each tuple has:
        * Full URL of a dated page
        * A date object
        """
        links = []
        soup = BeautifulSoup(html, "lxml")

        for link in soup.find("table", class_="views-table").find_all("a"):
            try:
                # We're getting the date out of a string like:
                # "House of Commons Journal Volume 7: 16 March 1660"
                date_str = link.string.split(":")[1].strip()
            except IndexError:
                self.stderr.write(f"No date string found in '{link.string}', skipping")
            else:
                # Make a date object from the date string we found:
                try:
                    date = datetime.strptime(date_str, "%d %B %Y").date()
                except ValueError:
                    self.stderr.write(
                        f"Could not create a date object from '{date_str}', skipping"
                    )
                else:
                    # Ensure it's a full URL
                    href = link.get("href")
                    if href.startswith("/"):
                        href = f"{BASE_URL}{href}"

                    links.append((href, date))

        return links

    def _fetch_url(self, url):
        """
        Passed a URL, it returns the cotent.

        Copied from encyclopedia.wikipedia_fetcher.WikipediaFetcher

        Returns a dict with two elements:
            'success' is either True or, if we couldn't fetch the page, False.
            'content' is the HTML if success==True, or else an error message.
        """
        error_message = ""

        try:
            response = requests.get(url, params={"action": "render"}, timeout=5)
        except requests.exceptions.ConnectionError:
            error_message = "Can't connect to domain."
        except requests.exceptions.Timeout:
            error_message = "Connection timed out."
        except requests.exceptions.TooManyRedirects:
            error_message = "Too many redirects."

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            # 4xx or 5xx errors:
            error_message = "HTTP Error: %s" % response.status_code
        except NameError:
            if error_message == "":
                error_message = "Something unusual went wrong."

        if error_message:
            return {"success": False, "content": error_message}
        else:
            return {"success": True, "content": response.text}
