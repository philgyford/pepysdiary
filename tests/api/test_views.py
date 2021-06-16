from collections import OrderedDict
from decimal import Decimal
import json

from django.contrib.sites.models import Site
from django.urls import reverse
from rest_framework.test import APITestCase

from pepysdiary.annotations.factories import (
    EntryAnnotationFactory,
    TopicAnnotationFactory,
)
from pepysdiary.common.utilities import make_date, make_datetime
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.encyclopedia.models import Category
from pepysdiary.encyclopedia.factories import (
    PersonTopicFactory,
    PlaceTopicFactory,
    TopicFactory,
)


class SiteAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        site = Site.objects.first()
        site.domain = "example.com"
        site.save()


class APIRootViewTestCase(SiteAPITestCase):
    "Testing views.api_root()"

    def test_response_200(self):
        "It should return 200"
        response = self.client.get(reverse("api:api-root"))
        self.assertEqual(response.status_code, 200)

    def test_response_data(self):
        "It should return the correct data"
        response = self.client.get(reverse("api:api-root"), SERVER_NAME="example.com")
        self.assertEqual(
            response.data,
            {
                "categories": "http://example.com/api/v1/categories",
                "entries": "http://example.com/api/v1/entries",
                "topics": "http://example.com/api/v1/topics",
            },
        )


class CategoryListViewTestCase(SiteAPITestCase):
    def test_response_200(self):
        "It should return 200"
        response = self.client.get(reverse("api:category-list"))
        self.assertEqual(response.status_code, 200)

    def test_response_data(self):
        "It should return the correct data"
        cat_1 = Category.add_root(title="Animals", slug="animals")
        cat_2 = cat_1.add_child(title="Dogs", slug="dogs")
        cat_3 = cat_2.add_child(title="Terriers", slug="terriers")

        TopicFactory(categories=[cat_2])
        TopicFactory(categories=[cat_2, cat_3])

        response = self.client.get(
            reverse("api:category-list"), SERVER_NAME="example.com"
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
                                ["http://example.com/api/v1/categories/dogs"],
                            ),
                            ("apiURL", "http://example.com/api/v1/categories/animals"),
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
                                ["http://example.com/api/v1/categories/animals"],
                            ),
                            (
                                "children",
                                ["http://example.com/api/v1/categories/terriers"],
                            ),
                            ("apiURL", "http://example.com/api/v1/categories/dogs"),
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
                                    "http://example.com/api/v1/categories/animals",
                                    "http://example.com/api/v1/categories/dogs",
                                ],
                            ),
                            ("children", []),
                            (
                                "apiURL",
                                "http://example.com/api/v1/categories/terriers",
                            ),
                            (
                                "webURL",
                                "http://example.com/encyclopedia/animals/dogs/terriers/",  # noqa: E501
                            ),
                        ]
                    ),
                ],
            },
        )

    def test_response_pagination(self):
        """Pagination-related results should be correct.
        Assuming we've set REST_FRAMEWORK["PAGE_SIZE"] = 5 in test settings.
        """
        site = Site.objects.first()
        site.domain = "example.com"
        site.save()
        parent_cat = Category.add_root(title="Animals", slug="animals")
        child_cats = []
        for n in range(0, 10):
            child_cats.append(
                parent_cat.add_child(title=f"Title {n}", slug=f"slug-{n}")
            )

        response = self.client.get(
            reverse("api:category-list") + "?page=2", SERVER_NAME="example.com"
        )

        self.assertEqual(response.data["totalResults"], 11)
        self.assertEqual(response.data["totalPages"], 3)
        self.assertEqual(
            response.data["nextPageURL"],
            f"http://example.com{reverse('api:category-list')}?page=3",
        )
        self.assertEqual(
            response.data["previousPageURL"],
            f"http://example.com{reverse('api:category-list')}",
        )
        self.assertEqual(len(response.data["results"]), 5)


class CategoryDetailViewTestCase(SiteAPITestCase):
    def test_response_200(self):
        "It should return 200"
        Category.add_root(title="Animals", slug="animals")
        response = self.client.get(
            reverse("api:category-detail", kwargs={"category_slug": "animals"})
        )
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        "It should return 404 if the category doesn't exist"
        response = self.client.get(
            reverse("api:category-detail", kwargs={"category_slug": "animals"})
        )
        self.assertEqual(response.data, {"detail": "Not found.", "status_code": 404})

    def test_response_data(self):
        "It should return the correct data"
        cat_1 = Category.add_root(title="Animals", slug="animals")
        cat_2 = cat_1.add_child(title="Dogs", slug="dogs")
        cat_2.add_child(title="Terriers", slug="terriers")
        topic = TopicFactory(categories=[cat_2])

        response = self.client.get(
            reverse("api:category-detail", kwargs={"category_slug": "dogs"}),
            SERVER_NAME="example.com",
        )

        self.assertEqual(
            response.data,
            {
                "slug": "dogs",
                "title": "Dogs",
                "topicCount": 1,
                "depth": 2,
                "parents": ["http://example.com/api/v1/categories/animals"],
                "children": ["http://example.com/api/v1/categories/terriers"],
                "topics": [f"http://example.com/api/v1/topics/{topic.pk}"],
                "apiURL": "http://example.com/api/v1/categories/dogs",
                "webURL": "http://example.com/encyclopedia/animals/dogs/",
            },
        )


class EntryListViewTestCase(SiteAPITestCase):
    def test_response_200(self):
        "It should return 200"
        response = self.client.get(reverse("api:entry-list"))
        self.assertEqual(response.status_code, 200)

    def test_response_data(self):
        "It should return the correct data"
        EntryFactory(diary_date=make_date("1660-01-02"), title="2 January 1660")

        response = self.client.get(reverse("api:entry-list"), SERVER_NAME="example.com")

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
                            ("apiURL", "http://example.com/api/v1/entries/1660-01-02"),
                            ("webURL", "http://example.com/diary/1660/01/02/"),
                        ]
                    )
                ],
            },
        )

    def test_response_pagination(self):
        """Pagination-related results should be correct.
        Assuming we've set REST_FRAMEWORK["PAGE_SIZE"] = 5 in test settings.
        """
        for n in range(1, 12):
            EntryFactory(diary_date=make_date(f"1660-01-{n:02}"))

        response = self.client.get(
            reverse("api:entry-list") + "?page=2", SERVER_NAME="example.com"
        )

        self.assertEqual(response.data["totalResults"], 11)
        self.assertEqual(response.data["totalPages"], 3)
        self.assertEqual(
            response.data["nextPageURL"],
            f"http://example.com{reverse('api:entry-list')}?page=3",
        )
        self.assertEqual(
            response.data["previousPageURL"],
            f"http://example.com{reverse('api:entry-list')}",
        )
        self.assertEqual(len(response.data["results"]), 5)

    def test_reponse_with_start_date(self):
        EntryFactory(diary_date=make_date("1660-01-01"))
        EntryFactory(diary_date=make_date("1661-01-01"))
        EntryFactory(diary_date=make_date("1662-01-01"))

        response = self.client.get(
            reverse("api:entry-list") + "?start=1661-01-01",
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
            reverse("api:entry-list") + "?end=1661-01-01",
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
            reverse("api:entry-list") + "?start=1661-01-01&end=1661-12-31",
            SERVER_NAME="example.com",
        )

        self.assertEqual(response.data["totalResults"], 1)
        self.assertEqual(response.data["results"][0]["date"], "1661-01-01")


class EntryDetailViewTestCase(SiteAPITestCase):
    def test_response_200(self):
        "It should return 200"
        EntryFactory(diary_date=make_date("1660-01-02"))
        response = self.client.get(
            reverse("api:entry-detail", kwargs={"entry_date": "1660-01-02"})
        )
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        "It should return 404 if the entry doesn't exist"
        response = self.client.get(
            reverse("api:entry-detail", kwargs={"entry_date": "1660-01-02"})
        )
        self.assertEqual(response.data, {"detail": "Not found.", "status_code": 404})

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
            reverse("api:entry-detail", kwargs={"entry_date": "1660-01-02"}),
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
                "topics": [f"http://example.com/api/v1/topics/{topic_1.pk}"],
                "apiURL": "http://example.com/api/v1/entries/1660-01-02",
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
            reverse("api:entry-detail", kwargs={"entry_date": "1660-01-02"}),
            SERVER_NAME="example.com",
        )
        self.assertEqual(response.data["annotationCount"], 1)
        self.assertEqual(response.data["lastAnnotationTime"], "2021-01-02T12:00:00Z")


class TopicListViewTestCase(SiteAPITestCase):
    def test_response_200(self):
        "It should return 200"
        response = self.client.get(reverse("api:topic-list"))
        self.assertEqual(response.status_code, 200)

    def test_response_data(self):
        "It should return the correct data"
        cat = Category.add_root(title="Animals", slug="animals")
        topic = TopicFactory(title="Dogs", categories=[cat])

        response = self.client.get(reverse("api:topic-list"), SERVER_NAME="example.com")

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
                            ("apiURL", f"http://example.com/api/v1/topics/{topic.pk}"),
                            ("webURL", f"http://example.com/encyclopedia/{topic.pk}/"),
                        ]
                    ),
                ],
            },
        )

    def test_response_data_person(self):
        "It should correctly mark a Person as being one"
        topic = PersonTopicFactory(title="Mr Bob Ferris")

        response = self.client.get(reverse("api:topic-list"), SERVER_NAME="example.com")

        self.assertEqual(
            response.data["results"][0],
            OrderedDict(
                [
                    ("id", topic.pk),
                    ("title", "Mr Bob Ferris"),
                    ("orderTitle", "Ferris, Mr Bob"),
                    ("kind", "person"),
                    ("apiURL", f"http://example.com/api/v1/topics/{topic.pk}"),
                    ("webURL", f"http://example.com/encyclopedia/{topic.pk}/"),
                ]
            ),
        )

    def test_response_data_place(self):
        "It should correctly mark a Place as being one"
        topic = PlaceTopicFactory(title="London")

        response = self.client.get(reverse("api:topic-list"), SERVER_NAME="example.com")

        self.assertEqual(
            response.data["results"][0],
            OrderedDict(
                [
                    ("id", topic.pk),
                    ("title", "London"),
                    ("orderTitle", "London"),
                    ("kind", "place"),
                    ("apiURL", f"http://example.com/api/v1/topics/{topic.pk}"),
                    ("webURL", f"http://example.com/encyclopedia/{topic.pk}/"),
                ]
            ),
        )

    def test_response_pagination(self):
        """Pagination-related results should be correct.
        Assuming we've set REST_FRAMEWORK["PAGE_SIZE"] = 5 in test settings.
        """
        cat = Category.add_root(title="Animals", slug="animals")
        for n in range(0, 11):
            TopicFactory(categories=[cat])

        response = self.client.get(
            reverse("api:topic-list") + "?page=2", SERVER_NAME="example.com"
        )

        self.assertEqual(response.data["totalResults"], 11)
        self.assertEqual(response.data["totalPages"], 3)
        self.assertEqual(
            response.data["nextPageURL"],
            f"http://example.com{reverse('api:topic-list')}?page=3",
        )
        self.assertEqual(
            response.data["previousPageURL"],
            f"http://example.com{reverse('api:topic-list')}",
        )
        self.assertEqual(len(response.data["results"]), 5)


class TopicDetailViewTestCase(SiteAPITestCase):
    def test_response_200(self):
        "It should return 200"
        topic = TopicFactory()
        response = self.client.get(
            reverse("api:topic-detail", kwargs={"topic_id": str(topic.pk)})
        )
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        "It should return 404 if the entry doesn't exist"
        response = self.client.get(
            reverse("api:topic-detail", kwargs={"topic_id": "123"})
        )
        self.assertEqual(response.data, {"detail": "Not found.", "status_code": 404})

    def test_response_data(self):
        "It should return the correct data"

        cat = Category.add_root(title="Animals", slug="animals")

        topic = TopicFactory(
            title="Dogs",
            wheatley="My Wheatley text.",
            tooltip_text="My tooltip text.",
            wikipedia_fragment="Dogs",
            categories=[cat],
        )

        response = self.client.get(
            reverse("api:topic-detail", kwargs={"topic_id": str(topic.pk)}),
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
                "categories": [f"http://example.com/api/v1/categories/{cat.slug}"],
                "entries": [],
                "apiURL": f"http://example.com/api/v1/topics/{topic.pk}",
                "webURL": f"http://example.com/encyclopedia/{topic.pk}/",
            },
        )

    def test_response_data_person(self):
        "It should contain the correct data if the Topic is a person"
        topic = PersonTopicFactory(title="Mr Bob Ferris")

        response = self.client.get(
            reverse("api:topic-detail", kwargs={"topic_id": str(topic.pk)}),
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
            reverse("api:topic-detail", kwargs={"topic_id": str(topic.pk)}),
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
            reverse("api:topic-detail", kwargs={"topic_id": str(topic.pk)}),
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
            reverse("api:topic-detail", kwargs={"topic_id": str(topic.pk)}),
            SERVER_NAME="example.com",
        )

        self.assertEqual(
            response.data["entries"], ["http://example.com/api/v1/entries/1660-01-02"]
        )
