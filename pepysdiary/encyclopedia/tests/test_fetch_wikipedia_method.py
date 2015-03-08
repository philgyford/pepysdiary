from mock import call, patch

from django.test import TestCase

from pepysdiary.encyclopedia.models import Topic


class FetchDataTest(TestCase):

    # Passed n items, should call thing n times.
    # Returned n responses (some False) should save n-False times, with dates.


    # ./manage.py dumpdata encyclopedia.Topic --pks=344,112,6079 --indent 4 > pepysdiary/encyclopedia/fixtures/wikipedia_test.json
    fixtures = ['wikipedia_test.json']

    # Of the topics in the fixture, two have `wikipedia_fragment`s:
    page_names = [
        'Edward_Montagu%2C_1st_Earl_of_Sandwich',
        'Charles_II_of_England'
    ]

    @patch('pepysdiary.encyclopedia.wikipedia_fetcher.WikipediaFetcher.fetch')
    def test_it_calls_fetcher_with_ids(self, fetch_method):
        # 2 names with Wikipedia pages, 1 without, 1 invalid ID:
        fetch_method.side_effect = ['112 html', '344 html']
        num_updated = Topic.objects.fetch_wikipedia_texts(
                                        topic_ids=[112, 344, 6079, 9999999])
        calls = [call(self.page_names[0]), call(self.page_names[1])]
        fetch_method.assert_has_calls(calls, any_order=True)
        self.assertEqual(num_updated, 2)
        
    @patch('pepysdiary.encyclopedia.wikipedia_fetcher.WikipediaFetcher.fetch')
    def test_it_calls_fetcher_with_all(self, fetch_method):
        fetch_method.side_effect = ['112 html', '344 html']
        num_updated = Topic.objects.fetch_wikipedia_texts(topic_ids='all')
        calls = [call(self.page_names[0]), call(self.page_names[1])]
        fetch_method.assert_has_calls(calls, any_order=True)
        self.assertEqual(num_updated, 2)
        
    @patch('pepysdiary.encyclopedia.wikipedia_fetcher.WikipediaFetcher.fetch')
    def test_it_saves_returned_texts(self, fetch_method):
        # The values it'll return:
        fetch_method.side_effect = ['112 html', '344 html']
        num_updated = Topic.objects.fetch_wikipedia_texts(
                                        topic_ids=[112, 344, 6079, 9999999])
        self.assertEqual(num_updated, 2)
        self.assertEqual(Topic.objects.get(pk=112).wikipedia_html, '112 html')
        self.assertEqual(Topic.objects.get(pk=344).wikipedia_html, '344 html')




        


