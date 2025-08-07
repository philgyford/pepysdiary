import json
from collections import OrderedDict
from decimal import Decimal

import time_machine
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from pepysdiary.annotations.factories import (
    EntryAnnotationFactory,
    TopicAnnotationFactory,
)
from pepysdiary.common.utilities import make_date, make_datetime
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.encyclopedia.factories import (
    PersonTopicFactory,
    PlaceTopicFactory,
    TopicFactory,
)
from pepysdiary.encyclopedia.models import Category


class SiteAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        site = Site.objects.first()
        site.domain = "example.com"
        site.save()
        cache.clear()


class APIRootViewTestCase(SiteAPITestCase):
    "Testing views.api_root()"

    def test_response_200(self):
        "It should return 200"
        response = self.client.get(reverse("api:api-root", kwargs={"format": "json"}))
        self.assertEqual(response.status_code, 200)

    def test_response_data(self):
        "It should return the correct data"
        response = self.client.get(reverse("api:api-root"), SERVER_NAME="example.com")

        self.assertEqual(
            json.loads(response.content),
            {
                "categories": "http://example.com/api/v1/categories",
                "entries": "http://example.com/api/v1/entries",
                "topics": "http://example.com/api/v1/topics",
            },
        )

    def test_response_html(self):
        "It should return the correct HTML if the Accept html header is sent."
        response = self.client.get(
            reverse("api:api-root"), SERVER_NAME="example.com", HTTP_ACCEPT="text/html"
        )

        self.assertContains(
            response,
            (
                '<a href="http://example.com/api/v1/categories" rel="nofollow">'
                "http://example.com/api/v1/categories</a>"
            ),
            html=True,
        )
        self.assertContains(
            response,
            (
                '<a href="http://example.com/api/v1/entries" rel="nofollow">'
                "http://example.com/api/v1/entries</a>"
            ),
            html=True,
        )
        self.assertContains(
            response,
            (
                '<a href="http://example.com/api/v1/topics" rel="nofollow">'
                "http://example.com/api/v1/topics</a>"
            ),
            html=True,
        )


class CategoryListViewTestCase(SiteAPITestCase):
    def test_response_200(self):
        "It should return 200"
        response = self.client.get(
            reverse("api:category-list", kwargs={"format": "json"})
        )
        self.assertEqual(response.status_code, 200)

    def test_response_data(self):
        "It should return the correct data"
        cat_1 = Category.add_root(title="Animals", slug="animals")
        cat_2 = cat_1.add_child(title="Dogs", slug="dogs")
        cat_3 = cat_2.add_child(title="Terriers", slug="terriers")

        TopicFactory(categories=[cat_2])
        TopicFactory(categories=[cat_2, cat_3])

        response = self.client.get(
            reverse("api:category-list", kwargs={"format": "json"}),
            SERVER_NAME="example.com",
        )

        self.assertEqual(
            response.data,
            {
                "totalResults": 3,
                "totalPages": 1,
                "nextPageURL": None,
                "previousPageURL": None,
                "results": [
                    OrderedDict(
                        [
                            ("slug", "animals"),
                            ("title", "Animals"),
                            ("topicCount", 0),
                            ("depth", 1),
                            ("parents", []),
                            (
                                "children",
                                ["http://example.com/api/v1/categories/dogs.json"],
                            ),
                            (
                                "apiURL",
                                "http://example.com/api/v1/categories/animals.json",
                            ),
                            ("webURL", "http://example.com/encyclopedia/animals/"),
                        ]
                    ),
                    OrderedDict(
                        [
                            ("slug", "dogs"),
                            ("title", "Dogs"),
                            ("topicCount", 2),
                            ("depth", 2),
                            (
                                "parents",
                                ["http://example.com/api/v1/categories/animals.json"],
                            ),
                            (
                                "children",
                                ["http://example.com/api/v1/categories/terriers.json"],
                            ),
                            (
                                "apiURL",
                                "http://example.com/api/v1/categories/dogs.json",
                            ),
                            ("webURL", "http://example.com/encyclopedia/animals/dogs/"),
                        ]
                    ),
                    OrderedDict(
                        [
                            ("slug", "terriers"),
                            ("title", "Terriers"),
                            ("topicCount", 1),
                            ("depth", 3),
                            (
                                "parents",
                                [
                                    "http://example.com/api/v1/categories/animals.json",
                                    "http://example.com/api/v1/categories/dogs.json",
                                ],
                            ),
                            ("children", []),
                            (
                                "apiURL",
                                "http://example.com/api/v1/categories/terriers.json",
                            ),
                            (
                                "webURL",
                                "http://example.com/encyclopedia/animals/dogs/terriers/",
                            ),
                        ]
                    ),
                ],
            },
        )

    def test_response_pagination(self):
        """Pagination-related results should be correct."""
        site = Site.objects.first()
        site.domain = "example.com"
        site.save()
        parent_cat = Category.add_root(title="Animals", slug="animals")
        child_cats = []
        for n in range(1, 101):
            child_cats.append(
                parent_cat.add_child(title=f"Title {n}", slug=f"slug-{n}")
            )

        url = reverse("api:category-list", kwargs={"format": "json"})
        response = self.client.get(url + "?page=2", SERVER_NAME="example.com")

        self.assertEqual(response.data["totalResults"], 101)
        self.assertEqual(response.data["totalPages"], 3)
        self.assertEqual(
            response.data["nextPageURL"],
            f"http://example.com{url}?page=3",
        )
        self.assertEqual(
            response.data["previousPageURL"],
            f"http://example.com{url}",
        )
        self.assertEqual(len(response.data["results"]), 50)


class CategoryDetailViewTestCase(SiteAPITestCase):
    def test_response_200(self):
        "It should return 200"
        Category.add_root(title="Animals", slug="animals")
        response = self.client.get(
            reverse(
                "api:category-detail",
                kwargs={"category_slug": "animals", "format": "json"},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        "It should return 404 if the category doesn't exist"
        response = self.client.get(
            reverse(
                "api:category-detail",
                kwargs={"category_slug": "animals", "format": "json"},
            )
        )
        self.assertEqual(response.data["status_code"], 404)

    @time_machine.travel("2021-06-01 12:00:00 +0000", tick=False)
    def test_response_data(self):
        "It should return the correct data"
        cat_1 = Category.add_root(title="Animals", slug="animals")
        cat_2 = cat_1.add_child(title="Dogs", slug="dogs")
        cat_2.add_child(title="Terriers", slug="terriers")
        topic = TopicFactory(categories=[cat_2])

        response = self.client.get(
            reverse(
                "api:category-detail",
                kwargs={"category_slug": "dogs", "format": "json"},
            ),
            SERVER_NAME="example.com",
        )

        self.assertEqual(
            response.data,
            {
                "slug": "dogs",
                "title": "Dogs",
                "topicCount": 1,
                "depth": 2,
                "parents": ["http://example.com/api/v1/categories/animals.json"],
                "children": ["http://example.com/api/v1/categories/terriers.json"],
                "topics": [f"http://example.com/api/v1/topics/{topic.pk}.json"],
                "apiURL": "http://example.com/api/v1/categories/dogs.json",
                "webURL": "http://example.com/encyclopedia/animals/dogs/",
            },
        )


class EntryListViewTestCase(SiteAPITestCase):
    def test_response_200(self):
        "It should return 200"
        response = self.client.get(reverse("api:entry-list", kwargs={"format": "json"}))
        self.assertEqual(response.status_code, 200)

    @time_machine.travel("2021-06-01 12:00:00 +0000", tick=False)
    def test_response_data(self):
        "It should return the correct data"
        EntryFactory(diary_date=make_date("1660-01-02"), title="2 January 1660")

        response = self.client.get(
            reverse("api:entry-list", kwargs={"format": "json"}),
            SERVER_NAME="example.com",
        )

        self.assertEqual(
            response.data,
            {
                "totalResults": 1,
                "totalPages": 1,
                "nextPageURL": None,
                "previousPageURL": None,
                "results": [
                    OrderedDict(
                        [
                            ("date", "1660-01-02"),
                            ("title", "2 January 1660"),
                            ("lastModifiedTime", "2021-06-01T12:00:00Z"),
                            (
                                "apiURL",
                                "http://example.com/api/v1/entries/1660-01-02.json",
                            ),
                            ("webURL", "http://example.com/diary/1660/01/02/"),
                        ]
                    )
                ],
            },
        )

    def test_response_pagination(self):
        """Pagination-related results should be correct."""
        # Enough entries for three pages of results:
        for m in range(1, 5):
            for d in range(1, 27):
                EntryFactory(diary_date=make_date(f"1660-{m:02}-{d:02}"))

        url = reverse("api:entry-list", kwargs={"format": "json"})
        response = self.client.get(url + "?page=2", SERVER_NAME="example.com")

        self.assertEqual(response.data["totalResults"], 104)
        self.assertEqual(response.data["totalPages"], 3)
        self.assertEqual(
            response.data["nextPageURL"],
            f"http://example.com{url}?page=3",
        )
        self.assertEqual(
            response.data["previousPageURL"],
            f"http://example.com{url}",
        )
        self.assertEqual(len(response.data["results"]), 50)

    def test_reponse_with_start_date(self):
        EntryFactory(diary_date=make_date("1660-01-01"))
        EntryFactory(diary_date=make_date("1661-01-01"))
        EntryFactory(diary_date=make_date("1662-01-01"))

        response = self.client.get(
            reverse("api:entry-list", kwargs={"format": "json"}) + "?start=1661-01-01",
            SERVER_NAME="example.com",
        )

        self.assertEqual(response.data["totalResults"], 2)
        self.assertEqual(response.data["results"][0]["date"], "1661-01-01")
        self.assertEqual(response.data["results"][1]["date"], "1662-01-01")

    def test_response_with_end_date(self):
        EntryFactory(diary_date=make_date("1660-01-01"))
        EntryFactory(diary_date=make_date("1661-01-01"))
        EntryFactory(diary_date=make_date("1662-01-01"))

        response = self.client.get(
            reverse("api:entry-list", kwargs={"format": "json"}) + "?end=1661-01-01",
            SERVER_NAME="example.com",
        )

        self.assertEqual(response.data["totalResults"], 2)
        self.assertEqual(response.data["results"][0]["date"], "1660-01-01")
        self.assertEqual(response.data["results"][1]["date"], "1661-01-01")

    def test_response_with_start_and_end_dates(self):
        EntryFactory(diary_date=make_date("1660-01-01"))
        EntryFactory(diary_date=make_date("1661-01-01"))
        EntryFactory(diary_date=make_date("1662-01-01"))

        response = self.client.get(
            reverse("api:entry-list", kwargs={"format": "json"})
            + "?start=1661-01-01&end=1661-12-31",
            SERVER_NAME="example.com",
        )

        self.assertEqual(response.data["totalResults"], 1)
        self.assertEqual(response.data["results"][0]["date"], "1661-01-01")


class EntryDetailViewTestCase(SiteAPITestCase):
    def test_response_200(self):
        "It should return 200"
        EntryFactory(diary_date=make_date("1660-01-02"))
        response = self.client.get(
            reverse(
                "api:entry-detail",
                kwargs={"entry_date": "1660-01-02", "format": "json"},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        "It should return 404 if the entry doesn't exist"
        response = self.client.get(
            reverse(
                "api:entry-detail",
                kwargs={"entry_date": "1660-01-02", "format": "json"},
            )
        )
        self.assertEqual(response.data["status_code"], 404)

    @time_machine.travel("2021-06-01 12:00:00 +0000", tick=False)
    def test_response_data(self):
        "It should return the correct data"

        topic_1 = TopicFactory()
        # Shouldn't be included in entry's topics:
        TopicFactory()

        # Linking to the topic in text will add it to the Entry's topics:
        EntryFactory(
            diary_date=make_date("1660-01-02"),
            title="2 January 1660",
            text=(
                '<p>My entry text. <a href="http://www.pepysdiary.com/'
                f'encyclopedia/{topic_1.pk}/">Link</a></p>'
            ),
            footnotes="<p>My footnotes.</p>",
        )

        response = self.client.get(
            reverse(
                "api:entry-detail",
                kwargs={"entry_date": "1660-01-02", "format": "json"},
            ),
            SERVER_NAME="example.com",
        )

        self.assertEqual(
            response.data,
            {
                "date": "1660-01-02",
                "title": "2 January 1660",
                "entryHTML": (
                    "<p>My entry text. "
                    f'<a href="http://www.pepysdiary.com/encyclopedia/{topic_1.pk}/">'
                    "Link</a></p>"
                ),
                "footnotesHTML": "<p>My footnotes.</p>",
                "annotationCount": 0,
                "lastAnnotationTime": None,
                "topics": [f"http://example.com/api/v1/topics/{topic_1.pk}.json"],
                "lastModifiedTime": "2021-06-01T12:00:00Z",
                "apiURL": "http://example.com/api/v1/entries/1660-01-02.json",
                "webURL": "http://example.com/diary/1660/01/02/",
            },
        )

    def test_response_data_annotations(self):
        "It should return the correct data if there are annotations"
        entry = EntryFactory(diary_date=make_date("1660-01-02"))

        EntryAnnotationFactory(
            content_object=entry, submit_date=make_datetime("2021-01-02 12:00:00")
        )
        # Shouldn't be counted:
        EntryAnnotationFactory(content_object=entry, is_public=False, is_removed=False)
        EntryAnnotationFactory(content_object=entry, is_public=True, is_removed=True)
        EntryAnnotationFactory()

        response = self.client.get(
            reverse(
                "api:entry-detail",
                kwargs={"entry_date": "1660-01-02", "format": "json"},
            ),
            SERVER_NAME="example.com",
        )
        self.assertEqual(response.data["annotationCount"], 1)
        self.assertEqual(response.data["lastAnnotationTime"], "2021-01-02T12:00:00Z")


class TopicListViewTestCase(SiteAPITestCase):
    def test_response_200(self):
        "It should return 200"
        response = self.client.get(reverse("api:topic-list", kwargs={"format": "json"}))
        self.assertEqual(response.status_code, 200)

    @time_machine.travel("2021-06-01 12:00:00 +0000", tick=False)
    def test_response_data(self):
        "It should return the correct data"
        cat = Category.add_root(
            # Set ID so that it's definitely not a person or place:
            id=9999,
            title="Animals",
            slug="animals",
        )
        topic = TopicFactory(title="Dogs", categories=[cat])

        response = self.client.get(
            reverse("api:topic-list", kwargs={"format": "json"}),
            SERVER_NAME="example.com",
        )

        self.assertEqual(
            response.data,
            {
                "totalResults": 1,
                "totalPages": 1,
                "nextPageURL": None,
                "previousPageURL": None,
                "results": [
                    OrderedDict(
                        [
                            ("id", topic.pk),
                            ("title", "Dogs"),
                            ("orderTitle", "Dogs"),
                            ("kind", "default"),
                            ("lastModifiedTime", "2021-06-01T12:00:00Z"),
                            (
                                "apiURL",
                                f"http://example.com/api/v1/topics/{topic.pk}.json",
                            ),
                            ("webURL", f"http://example.com/encyclopedia/{topic.pk}/"),
                        ]
                    ),
                ],
            },
        )

    @time_machine.travel("2021-06-01 12:00:00 +0000", tick=False)
    def test_response_data_person(self):
        "It should correctly mark a Person as being one"
        topic = PersonTopicFactory(title="Mr Bob Ferris")

        response = self.client.get(
            reverse("api:topic-list", kwargs={"format": "json"}),
            SERVER_NAME="example.com",
        )

        self.assertEqual(
            response.data["results"][0],
            OrderedDict(
                [
                    ("id", topic.pk),
                    ("title", "Mr Bob Ferris"),
                    ("orderTitle", "Ferris, Mr Bob"),
                    ("kind", "person"),
                    ("lastModifiedTime", "2021-06-01T12:00:00Z"),
                    ("apiURL", f"http://example.com/api/v1/topics/{topic.pk}.json"),
                    ("webURL", f"http://example.com/encyclopedia/{topic.pk}/"),
                ]
            ),
        )

    @time_machine.travel("2021-06-01 12:00:00 +0000", tick=False)
    def test_response_data_place(self):
        "It should correctly mark a Place as being one"
        topic = PlaceTopicFactory(title="London")

        response = self.client.get(
            reverse("api:topic-list", kwargs={"format": "json"}),
            SERVER_NAME="example.com",
        )

        self.assertEqual(
            response.data["results"][0],
            OrderedDict(
                [
                    ("id", topic.pk),
                    ("title", "London"),
                    ("orderTitle", "London"),
                    ("kind", "place"),
                    ("lastModifiedTime", "2021-06-01T12:00:00Z"),
                    ("apiURL", f"http://example.com/api/v1/topics/{topic.pk}.json"),
                    ("webURL", f"http://example.com/encyclopedia/{topic.pk}/"),
                ]
            ),
        )

    def test_response_pagination(self):
        """Pagination-related results should be correct."""
        cat = Category.add_root(title="Animals", slug="animals")
        for _ in range(1, 102):
            TopicFactory(categories=[cat])

        url = reverse("api:topic-list", kwargs={"format": "json"})
        response = self.client.get(url + "?page=2", SERVER_NAME="example.com")

        self.assertEqual(response.data["totalResults"], 101)
        self.assertEqual(response.data["totalPages"], 3)
        self.assertEqual(
            response.data["nextPageURL"],
            f"http://example.com{url}?page=3",
        )
        self.assertEqual(
            response.data["previousPageURL"],
            f"http://example.com{url}",
        )
        self.assertEqual(len(response.data["results"]), 50)


class TopicDetailViewTestCase(SiteAPITestCase):
    def test_response_200(self):
        "It should return 200"
        topic = TopicFactory()
        response = self.client.get(
            reverse(
                "api:topic-detail", kwargs={"topic_id": str(topic.pk), "format": "json"}
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        "It should return 404 if the entry doesn't exist"
        response = self.client.get(
            reverse("api:topic-detail", kwargs={"topic_id": "123", "format": "json"})
        )
        self.assertEqual(response.data["status_code"], 404)

    @time_machine.travel("2021-06-01 12:00:00 +0000", tick=False)
    def test_response_data(self):
        "It should return the correct data"

        cat = Category.add_root(
            # Set ID so that it's definitely not a person or place:
            id=9999,
            title="Animals",
            slug="animals",
        )

        topic = TopicFactory(
            title="Dogs",
            wheatley="My Wheatley text.",
            tooltip_text="My tooltip text.",
            wikipedia_fragment="Dogs",
            categories=[cat],
        )

        response = self.client.get(
            reverse(
                "api:topic-detail", kwargs={"topic_id": str(topic.pk), "format": "json"}
            ),
            SERVER_NAME="example.com",
        )

        self.assertEqual(
            response.data,
            {
                "id": topic.pk,
                "title": "Dogs",
                "orderTitle": "Dogs",
                "wheatleyHTML": "<p>My Wheatley text.</p>",
                "tooltipText": "My tooltip text.",
                "wikipediaURL": "https://en.wikipedia.org/wiki/Dogs",
                "thumbnailURL": None,
                "annotationCount": 0,
                "lastAnnotationTime": None,
                "kind": "default",
                "latitude": None,
                "longitude": None,
                "zoom": None,
                "shape": "",
                "categories": [f"http://example.com/api/v1/categories/{cat.slug}.json"],
                "entries": [],
                "lastModifiedTime": "2021-06-01T12:00:00Z",
                "apiURL": f"http://example.com/api/v1/topics/{topic.pk}.json",
                "webURL": f"http://example.com/encyclopedia/{topic.pk}/",
            },
        )

    def test_response_data_person(self):
        "It should contain the correct data if the Topic is a person"
        topic = PersonTopicFactory(title="Mr Bob Ferris")

        response = self.client.get(
            reverse(
                "api:topic-detail", kwargs={"topic_id": str(topic.pk), "format": "json"}
            ),
            SERVER_NAME="example.com",
        )

        self.assertEqual(response.data["kind"], "person")
        self.assertEqual(response.data["orderTitle"], "Ferris, Mr Bob")

    def test_response_data_place(self):
        "It should contain the correct data if the Topic is a place"
        topic = PlaceTopicFactory(
            title="London",
            latitude=51.123,
            longitude=-0.456,
            zoom=12,
            shape="0,0;1,0;1,1;1,0;0,0",
        )

        response = self.client.get(
            reverse(
                "api:topic-detail", kwargs={"topic_id": str(topic.pk), "format": "json"}
            ),
            SERVER_NAME="example.com",
        )

        self.assertEqual(response.data["kind"], "place")
        self.assertEqual(response.data["latitude"], Decimal("51.123000"))
        self.assertEqual(response.data["longitude"], Decimal("-0.456000"))
        self.assertEqual(response.data["shape"], "0,0;1,0;1,1;1,0;0,0")

        # Check they come out OK in the JSON:
        content = json.loads(response.content)
        self.assertEqual(content["latitude"], 51.123)
        self.assertEqual(content["longitude"], -0.456)

    def test_response_data_annotations(self):
        "It should contain the correct info if there are annotations."
        topic = TopicFactory()
        TopicAnnotationFactory(
            content_object=topic, submit_date=make_datetime("2021-01-02 12:00:00")
        )
        # Shouldn't be counted:
        TopicAnnotationFactory(content_object=topic, is_public=False, is_removed=False)
        TopicAnnotationFactory(content_object=topic, is_public=True, is_removed=True)
        TopicAnnotationFactory()

        response = self.client.get(
            reverse(
                "api:topic-detail", kwargs={"topic_id": str(topic.pk), "format": "json"}
            ),
            SERVER_NAME="example.com",
        )

        self.assertEqual(response.data["annotationCount"], 1)
        self.assertEqual(response.data["lastAnnotationTime"], "2021-01-02T12:00:00Z")

    def test_response_data_entries(self):
        "It should contain the correct info if the topic has entries"
        topic = TopicFactory()

        EntryFactory(
            diary_date=make_date("1660-01-02"),
            text=(
                f'<a href="http://www.pepysdiary.com/encyclopedia/{topic.pk}/">Link</a>'
            ),
        )
        # This Entry shouldn't be included (different/no topic):
        EntryFactory(diary_date=make_date("1660-01-03"))

        response = self.client.get(
            reverse(
                "api:topic-detail", kwargs={"topic_id": str(topic.pk), "format": "json"}
            ),
            SERVER_NAME="example.com",
        )

        self.assertEqual(
            response.data["entries"],
            ["http://example.com/api/v1/entries/1660-01-02.json"],
        )
