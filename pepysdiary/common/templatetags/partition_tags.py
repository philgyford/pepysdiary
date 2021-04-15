from django.template import Library

register = Library()

"""
Template tags to partition lists into rows or columns.

Originally filters from https://djangosnippets.org/snippets/401/

A common use-case is for splitting a list into a table with columns::

    {% load partition_tags %}
    {% make_columns mylist 3 as columns %}
    <table>
    {% for row in columns %}
        <tr>
        {% for item in row %}
            <td>{{ item }}</td>
        {% endfor %}
        </tr>
    {% endfor %}
    </table>
"""


@register.simple_tag
def make_rows(thelist, num_rows, threshold=None):
    """
    Break a list into ``num_rows`` rows, filling up each row to the maximum
    equal length possible. For example::

        >>> l = list(range(10))

        >>> make_rows(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        >>> make_rows(l, 3)
        [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]

        >>> make_rows(l, 4)
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

        >>> make_rows(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

        >>> make_rows(l, 9)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [], [], [], []]

    This tag will always return `num_rows` rows, even if some are empty:

        >>> make_rows(list(range(2)), 3)
        [[0], [1], []]

    If ``threshold`` is supplied, the list will only be split if it has
    more items than ``threshold``. Again, `num_rows` rows are always returned:

        >>> make_rows(list(range(4)), num_rows=3, threshold=5)
        [[0,1,2,3], [], []]
    """
    list_len = len(thelist)

    if threshold is not None and list_len <= threshold:
        # Not enough elements to split it up.
        # Return something like [thelist, [], [],] .
        return [thelist] + [[] for i in range(num_rows - 1)]
    else:
        split = list_len // num_rows

        if list_len % num_rows != 0:
            split += 1
        return [thelist[split * i : split * (i + 1)] for i in range(num_rows)]


@register.simple_tag
def make_rows_distributed(thelist, num_rows):
    """
    Break a list into ``num_rows`` rows, distributing columns as evenly as
    possible across the rows. For example::

        >>> l = list(range(10))

        >>> make_rows_distributed(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        >>> make_rows_distributed(l, 3)
        [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]

        >>> make_rows_distributed(l, 4)
        [[0, 1, 2], [3, 4, 5], [6, 7], [8, 9]]

        >>> make_rows_distributed(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

        >>> make_rows_distributed(l, 9)
        [[0, 1], [2], [3], [4], [5], [6], [7], [8], [9]]

        # This filter will always return `num_rows` rows, even if some are
        empty:

        >>> make_rows(list(range(2)), 3)
        [[0], [1], []]
    """
    list_len = len(thelist)
    split = list_len // num_rows

    remainder = list_len % num_rows
    offset = 0
    rows = []
    for i in range(num_rows):
        if remainder:
            start, end = (split + 1) * i, (split + 1) * (i + 1)
        else:
            start, end = split * i + offset, split * (i + 1) + offset
        rows.append(thelist[start:end])
        if remainder:
            remainder -= 1
            offset += 1
    return rows


@register.simple_tag
def make_columns(thelist, num_cols):
    """
    Break a list into ``num_cols`` columns, filling up each column to the
    maximum equal length possible. For example::

        >>> from pprint import pprint
        >>> for i in range(7, 11):
        ...     print '%sx%s:' % (i, 3)
        ...     pprint(make_columns(range(i), 3), width=20)
        7x3:
        [[0, 3, 6],
         [1, 4],
         [2, 5]]
        8x3:
        [[0, 3, 6],
         [1, 4, 7],
         [2, 5]]
        9x3:
        [[0, 3, 6],
         [1, 4, 7],
         [2, 5, 8]]
        10x3:
        [[0, 4, 8],
         [1, 5, 9],
         [2, 6],
         [3, 7]]

        # Note that this filter does not guarantee that `num_cols` columns will
        be present:
        >>> pprint(make_columns(list(range(4)), 3), width=10)
        [[0, 2],
         [1, 3]]
    """
    list_len = len(thelist)
    split = list_len // num_cols
    if list_len % num_cols != 0:
        split += 1
    return [thelist[i::split] for i in range(split)]
