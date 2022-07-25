from django.test import TestCase

from pepysdiary.common.templatetags.partition_tags import (
    make_columns,
    make_rows,
    make_rows_distributed,
)


class MakeRowsTestCase(TestCase):
    def test_result(self):
        "It should split into the correct number of rows"
        self.assertEqual(
            make_rows(list(range(9)), 3), [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        )
        self.assertEqual(
            make_rows(list(range(10)), 4), [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        )

    def test_empty_rows(self):
        "It should return empty rows if there aren't enough items"
        self.assertEqual(
            make_rows(list(range(10)), 9),
            [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [], [], [], []],
        )

    def test_threshold(self):
        "It only splits if it has more items than threshold"
        self.assertEqual(
            make_rows(list(range(4)), num_rows=3, threshold=5), [[0, 1, 2, 3], [], []]
        )


class MakeRowsDistributedTestCase(TestCase):
    def test_result(self):
        "It should split into the correct number of rows"
        self.assertEqual(
            make_rows_distributed(list(range(10)), 2),
            [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]],
        )

        self.assertEqual(
            make_rows_distributed(list(range(10)), 9),
            [[0, 1], [2], [3], [4], [5], [6], [7], [8], [9]],
        )

    def test_empty_rows(self):
        "It should return empty rows if there aren't enough items"
        self.assertEqual(make_rows_distributed(list(range(2)), 3), [[0], [1], []])


class MakeColumnsTestCase(TestCase):
    def test_result(self):
        "It should split into the correct number of columns"
        self.assertEqual(make_columns(list(range(7)), 3), [[0, 3, 6], [1, 4], [2, 5]])
        self.assertEqual(
            make_columns(list(range(9)), 3), [[0, 3, 6], [1, 4, 7], [2, 5, 8]]
        )
        self.assertEqual(
            make_columns(list(range(10)), 3), [[0, 4, 8], [1, 5, 9], [2, 6], [3, 7]]
        )

    def test_not_empty(self):
        "It shouldn't return empty columns"
        self.assertEqual(make_columns(list(range(4)), 3), [[0, 2], [1, 3]])
