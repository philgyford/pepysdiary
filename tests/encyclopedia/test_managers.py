from unittest.mock import call, patch

from django.test import TestCase

from pepysdiary.encyclopedia.models import Category, Topic


class CategoryManagerTestCase(TestCase):
    def test_map_catwgory_choices(self):
        "Just checking some of it's as it should be."
        choices = Category.objects.map_category_choices()
        self.assertEqual(len(choices), 5)
        self.assertEqual(choices[0][0], "London")
        self.assertEqual(choices[0][1][9], (29, "Other London buildings"))
        self.assertEqual(choices[4], (45, "Rest of the world"))

    def test_valid_map_category_ids(self):
        "Is there any point to this?"
        ids = Category.objects.valid_map_category_ids()
        self.assertEqual(
            ids, [196, 31, 199, 201, 28, 27, 197, 180, 200, 29, 214, 209, 30, 45]
        )


class TopicManagerTestCase(TestCase):
    "Testing any TopicManager stuff not covered by the other classes"

    def test_pepys_homes_ids(self):
        self.assertEqual(Topic.objects.pepys_homes_ids(), [102, 1023])


class TopicManagerFetchWikipediaTextsTestCase(TestCase):
    "Testing TopicManager.fetch_wikipedia_texts()"

    # ./manage.py dumpdata encyclopedia.Topic --pks=344,112,6079 --indent 4 > pepysdiary/encyclopedia/fixtures/wikipedia_test.json  # noqa: E501
    fixtures = ["tests/encyclopedia/fixtures/wikipedia_test.json"]

    # Of the topics in the fixture, two have `wikipedia_fragment`s:
    page_names = [
        "Edward_Montagu%2C_1st_Earl_of_Sandwich",
        "Elisabeth_Pepys",
        "Charles_II_of_England",
        "Zeeland",
        "Christopher_Wren",
    ]

    responses = [
        {"success": True, "content": "112 html"},
        {"success": True, "content": "150 html"},
        {"success": True, "content": "344 html"},
        {"success": True, "content": "480 html"},
        {"success": True, "content": "9711 html"},
    ]

    @patch("pepysdiary.encyclopedia.wikipedia_fetcher.WikipediaFetcher.fetch")
    def test_it_calls_fetcher_with_ids(self, fetch_method):
        # What the mocked method will return on successive calls:
        fetch_method.side_effect = self.responses
        # 2 names with Wikipedia pages, 1 without, 1 invalid ID:
        updated = Topic.objects.fetch_wikipedia_texts(
            topic_ids=[112, 344, 6079, 9999999]
        )
        calls = [call(self.page_names[0]), call(self.page_names[2])]
        fetch_method.assert_has_calls(calls, any_order=True)
        self.assertEqual(len(updated["success"]), 2)
        self.assertEqual(len(updated["failure"]), 0)

    @patch("pepysdiary.encyclopedia.wikipedia_fetcher.WikipediaFetcher.fetch")
    def test_it_calls_fetcher_with_all(self, fetch_method):
        # Ensure we get notified if one of these fails:
        responses = list(self.responses)
        responses[0] = {"success": False}
        fetch_method.side_effect = responses
        updated = Topic.objects.fetch_wikipedia_texts(num="all")
        calls = [
            call(self.page_names[0]),
            call(self.page_names[1]),
            call(self.page_names[2]),
            call(self.page_names[3]),
            call(self.page_names[4]),
        ]
        fetch_method.assert_has_calls(calls, any_order=True)
        self.assertEqual(len(updated["success"]), 4)
        self.assertEqual(len(updated["failure"]), 1)

    @patch("pepysdiary.encyclopedia.wikipedia_fetcher.WikipediaFetcher.fetch")
    def test_it_calls_fetcher_with_num(self, fetch_method):
        fetch_method.side_effect = [
            self.responses[4],
            self.responses[2],
            self.responses[1],
        ]
        updated = Topic.objects.fetch_wikipedia_texts(num=3)
        calls = [
            call(self.page_names[4]),  # Has null wikipedia_last_fetch
            call(self.page_names[2]),  #
            call(self.page_names[1]),  #
        ]
        fetch_method.assert_has_calls(calls, any_order=True)
        self.assertEqual(len(updated["success"]), 3)
        self.assertEqual(len(updated["failure"]), 0)

    @patch("pepysdiary.encyclopedia.wikipedia_fetcher.WikipediaFetcher.fetch")
    def test_it_saves_returned_texts(self, fetch_method):
        fetch_method.side_effect = [
            self.responses[0],
            self.responses[2],
        ]
        updated = Topic.objects.fetch_wikipedia_texts(
            topic_ids=[112, 344, 6079, 9999999]
        )
        self.assertEqual(len(updated["success"]), 2)
        self.assertEqual(len(updated["failure"]), 0)
        self.assertEqual(Topic.objects.get(pk=112).wikipedia_html, "112 html")
        self.assertEqual(Topic.objects.get(pk=344).wikipedia_html, "344 html")

    @patch("pepysdiary.encyclopedia.wikipedia_fetcher.WikipediaFetcher.fetch")
    def test_no_topics(self, fetch_method):
        "If there are no matching topics to fetch, it doesn't"
        updated = Topic.objects.fetch_wikipedia_texts(topic_ids=[6079])
        fetch_method.assert_has_calls([])
        self.assertEqual(len(updated["success"]), 0)
        self.assertEqual(len(updated["failure"]), 0)


class TopicManagerMakeOrderTitleTestCase(TestCase):
    "Testing TopicManager.make_order_title()"

    # NOT PEOPLE.

    def test_unchanged(self):
        self.assertEqual(
            Topic.objects.make_order_title("Ale, buttered", is_person=False),
            "Ale, buttered",
        )

    def test_the(self):
        self.assertEqual(
            Topic.objects.make_order_title("The Royal Prince", is_person=False),
            "Royal Prince, The",
        )

    def test_the_fail(self):
        self.assertNotEqual(
            Topic.objects.make_order_title("The Royal Prince", is_person=False),
            "The Royal Prince",
        )

    def test_the_parentheses(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "The Alchemist (Ben Jonson)", is_person=False
            ),
            "Alchemist, The (Ben Jonson)",
        )

    def test_make_order_starts_with_apostrophe(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "'A dialogue concerning the rights of his most christian majesty'",
                is_person=False,
            ),
            "A dialogue concerning the rights of his most christian majesty'",
        )

    # PEOPLE THAT NEED CHANGING.

    def test_name(self):
        self.assertEqual(
            Topic.objects.make_order_title("Thomas Agar", is_person=True),
            "Agar, Thomas",
        )

    def test_name_parentheses(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "Sidney Smythe (1st Lord Smythe)", is_person=True
            ),
            "Smythe, Sidney (1st Lord Smythe)",
        )

    def test_name_capt(self):
        self.assertEqual(
            Topic.objects.make_order_title("Capt. Henry Terne", is_person=True),
            "Terne, Capt. Henry",
        )

    def test_name_mr(self):
        self.assertEqual(
            Topic.objects.make_order_title("Mr Hazard", is_person=True), "Hazard, Mr"
        )

    def test_name_mrs(self):
        self.assertEqual(
            Topic.objects.make_order_title("Mrs Andrews", is_person=True),
            "Andrews, Mrs",
        )

    def test_name_middle(self):
        self.assertEqual(
            Topic.objects.make_order_title("Johann Heinrich Alstead", is_person=True),
            "Alstead, Johann Heinrich",
        )

    def test_name_d(self):
        self.assertEqual(
            Topic.objects.make_order_title("Monsieur d'Esquier", is_person=True),
            "Esquier, Monsieur d'",
        )

    def test_name_de(self):
        self.assertEqual(
            Topic.objects.make_order_title("Adriaen de Haes", is_person=True),
            "Haes, Adriaen de",
        )

    def test_name_de_parentheses(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "Jan de Witt (Grand Pensionary of Holland)", is_person=True
            ),
            "Witt, Jan de (Grand Pensionary of Holland)",
        )

    def test_name_de_la(self):
        self.assertEqual(
            Topic.objects.make_order_title("Peter de la Roche", is_person=True),
            "Roche, Peter de la",
        )

    def test_name_du(self):
        self.assertEqual(
            Topic.objects.make_order_title("Monsieur du Prat", is_person=True),
            "Prat, Monsieur du",
        )

    def test_name_de_du(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "Guillaume de Salluste Du Bartas", is_person=True
            ),
            "Bartas, Guillaume de Salluste Du",
        )

    def test_name_of(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "Catherine of Braganza (Queen)", is_person=True
            ),
            "Braganza, Catherine of (Queen)",
        )

    def test_name_van(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "Michiel van Gogh (Dutch Ambassador, 1664-5)", is_person=True
            ),
            "Gogh, Michiel van (Dutch Ambassador, 1664-5)",
        )

    def test_name_majgenaldsir(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "Maj.-Gen. Ald. Sir Richard Browne", is_person=True
            ),
            "Browne, Maj.-Gen. Ald. Sir Richard",
        )

    def test_name_dr_single(self):
        self.assertEqual(
            Topic.objects.make_order_title("Dr Waldegrave", is_person=True),
            "Waldegrave, Dr",
        )

    def test_name_comte_d(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "Godefroy, Comte d'Estrades", is_person=True
            ),
            "Godefroy, Comte d'Estrades",
        )

    def test_name_al(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                'Abd Allah al-Ghailan ("Guiland", "Gayland")', is_person=True
            ),
            'Ghailan, Abd Allah al- ("Guiland", "Gayland")',
        )

    def test_name_mr_parentheses(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "Mr Butler (Mons. L'impertinent)", is_person=True
            ),
            "Butler, Mr (Mons. L'impertinent)",
        )

    #  PEOPLE THAT STAY THE SAME.

    def test_name_single(self):
        self.assertEqual(
            Topic.objects.make_order_title("Shelston", is_person=True), "Shelston"
        )

    def test_name_single_parentheses(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "Mary (c, Pepys' chambermaid)", is_person=True
            ),
            "Mary (c, Pepys' chambermaid)",
        )

    def test_name_i(self):
        self.assertEqual(
            Topic.objects.make_order_title("Mary I of England", is_person=True),
            "Mary I of England",
        )

    def test_name_iv(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "Philip IV (King of Spain, 1621-1665)", is_person=True
            ),
            "Philip IV (King of Spain, 1621-1665)",
        )

    def test_name_the(self):
        self.assertEqual(
            Topic.objects.make_order_title("Ivan the Terrible", is_person=True),
            "Ivan the Terrible",
        )

    def test_name_sir(self):
        self.assertEqual(
            Topic.objects.make_order_title(
                "Sir Anthony Ashley Cooper (Baron Ashley)", is_person=True
            ),
            "Cooper, Sir Anthony Ashley (Baron Ashley)",
        )

    def test_name_blank(self):
        self.assertEqual(Topic.objects.make_order_title("", is_person=True), "")
