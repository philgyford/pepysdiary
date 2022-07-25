import re
from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.html import strip_tags


def make_date(d):
    "For convenience."
    return datetime.strptime(d, "%Y-%m-%d").date()


def make_datetime(dt):
    "For convenience."
    return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)


def smart_truncate(content, length=80, suffix="…"):
    """Truncate a string at word boundaries."""
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(" ", 1)[0] + suffix


def hilite_words(content, words):
    """
    Hilites matching words in a piece of text content.
    Given a bunch of text/HTML, this will strip any HTML tags, and then
    hilite any occurrences of the separate strings in `words` by wrapping
    them in <b></b> tags.

    content -- Some text or HTML. Any existing HTML tags will be stripped.
    words -- Words to hilite. e.g. "cat dog" would result in any
             occurrences of "cat", "dog", "cats" or "dogs" being hilited.
             Ignores any punctuation characters in the words.

    Returns a string.
    """
    # The HTML tags we'll wrap the hilited words in:
    start_tag = "<b>"
    end_tag = "</b>"

    # In case it's HTML.
    content = strip_tags(content)

    # Get rid of any non-word characters.
    # Mainly because I think the Posgresql search ignores them, so if
    # the user has searched for <"my wife"> (including quotes), we'll have
    # results containing <my> and <wife> and <my wife>. And if we don't
    # strip non-word chars we're trying to hilite the strings <"my> and <wife">
    # But leave apostrophes.
    regex = re.compile(r"[^\s'0-9a-zA-Z]")
    words = regex.sub(" ", words)

    # If words = 'cat dog' then we look for '(\bcats?\b)|(\bdogs?\b)'
    # Note the optional trailing 's', because the search sometimes returns
    # matches for plurals, but we weren't hiliting them.
    find = "s?\\b)|(\\b".join(words.split())
    regex = re.compile(r"(\b{}s?\b)".format(find), re.IGNORECASE)

    output = ""
    i = 0
    for m in regex.finditer(content):
        output += "".join(
            [content[i : m.start()], start_tag, content[m.start() : m.end()], end_tag]
        )
        i = m.end()

    if i == 0:
        html = content
    else:
        html = "".join([output, content[m.end() :]])

    return html


def trim_hilites(
    content, chars_before=20, chars_after=40, allow_empty=True, max_hilites_to_show=None
):
    """
    Given some text that contains no HTML tags except <b> and </b>,
    used to hilite words/phrases, this will return text that only includes
    those hilites, plus chars_before and chars_after characters around
    them. These excerpts are all joined by ellipses.

    Designed to take the output from hilite_words().

    content -- Text optionally containing <b>hilites</b> (and NO other HTML).
    chars_before -- Number of characters to include before a <b>.
    chars_after -- Number of characters to include after a </b>.
    allow_empty -- Boolean. If True and there are no hilites, an empty
                   string will be returned. If False, and no hilites,
                   the start of `content` will be returned.
    max_hilites_to_show -- The maximum number of the matches to return
                   in the HTML.

    Returns a dict with three keys:

    html - String. The HTML to display.
    hilites_shown - Int. The number of matches displayed.
    total_hilites - Int. The total number of hilites in content, whether
        displayed in html or not.
    """
    start_tag = "<b>"
    end_tag = "</b>"
    joiner = " … "

    # Replace multiple spaces and linebreaks with one, otherwise they
    # throw off some of the counting.
    content = re.sub(r"\s+", " ", content).strip()

    tag_re = re.compile(r"{}[^<]*?{}".format(start_tag, end_tag))
    iters = tag_re.finditer(content)
    # Get list of start and end positions of all '<b>blah</b>' substrings:
    positions = [(m.start(0), m.end(0)) for m in iters]

    # If there are hilited substrings close to each other, we want to
    # keep them together.
    # This will store the start and end positions of the strings to keep,
    # e.g. for "Hi <b>there</b> this <b>is</b> close"
    # positions will be like [(3,14), (21,29)]
    # and positions_to_use will be like [(3,29)]
    # and positions_to_discard will be [(21,29)]
    positions_to_use = []
    positions_to_discard = []
    for idx, pos in enumerate(positions):
        if pos in positions_to_discard:
            # When looking at an earlier position, we realised this position
            # is very close, so we don't want to treat this one spearately.
            # Skip it.
            continue
        start = pos[0]
        end = pos[1]
        for t in range(idx + 1, len(positions)):
            # Go through all the subsequent positions, to see if they are
            # close enough to this one to keep them together.
            # What would be the cut-off point for the string sorrounding this position:
            trunc_point = end + chars_after
            if (
                trunc_point >= (positions[t][0] - chars_before)
                and trunc_point <= (positions[t][1] + chars_after)
            ) or (trunc_point >= (positions[t][1] + chars_after)):
                # The cut-off point would be either within the text
                # surrounding the next hilited word
                # OR
                # after the next hilited-word.
                # So, we know we don't want to treat the next position separately:
                positions_to_discard.append(positions[t])
                # And we move the end point of this fragment ahead to
                # include this next position:
                end = positions[t][1]
            else:
                # The next position isn't close to this one, so move on.
                break

        # Store these start and end positions:
        positions_to_use.append((start, end))

    # Now we know the start and end positions of all the fragments, each
    # of which starts with a start_tag and ends with an end_tag (but might
    # include multiple hilited words).
    excerpts = []
    for pos in positions_to_use:
        if pos[0] > chars_before:
            fragment = "{}".format(content[pos[0] - chars_before :])
        else:
            fragment = content

        # We have to allow for the length of the HTML tags:
        trunc_len = chars_before + (pos[1] - pos[0]) + chars_after
        truncated = fragment[:trunc_len]
        if truncated != "":
            excerpts.append(truncated.strip())

    total_hilites = len(excerpts)

    if max_hilites_to_show is None:
        text = joiner.join(excerpts)
        hilites_shown = total_hilites
    else:
        text = joiner.join(excerpts[:max_hilites_to_show])
        hilites_shown = max_hilites_to_show

    if len(positions) == 0:
        if allow_empty is False:
            excerpt = content[: (chars_before + chars_after)]
            text = "{}{}".format(excerpt, joiner)
    else:
        if (positions[0][0] - chars_before) > 0:
            text = joiner.lstrip() + text

        if (positions[-1][1] + chars_after) < len(content):
            text += joiner.rstrip()

    return {
        "html": text,
        "hilites_shown": hilites_shown,
        "total_hilites": total_hilites,
    }


# def hilite_words(content, words, chars_before=30, chars_after=50):

#     # The name of the HTML tag we'll wrap the hilited words in:
#     tag = 'b'
#     # What we'll use to join the excerpts together:
#     joiner = ' … '

#     # In case it's HTML.
#     content = strip_tags(content)


#     for word in words.split():
#         find = r'({})'.format(re.escape(word))
#         replace = r'<{}>\1</{}>'.format(tag, tag)
#         hilite_re = re.compile(find, re.IGNORECASE)
#         content = hilite_re.sub(replace, content)

#     # Find all the matches, that we've now marked with <b></b>:
#     iters = re.finditer('<{}>[^<]*?</{}>'.format(tag, tag), content)

#     # The indexes of the start and end of every match:
#     positions = [(m.start(0), m.end(0)) for m in iters]

#     excerpts = []
#     for pos in positions:
#         if pos[0] > chars_before:
#             fragment = '{}'.format(content[pos[0]-chars_before:])
#         else:
#             fragment = content

#         # We have to allow for the length of the HTML tags:
#         trunc_len = chars_before + (
#             pos[1] - pos[0]
#         ) + chars_after - ((len(tag) * 2) + 5)
#         truncated = Truncator(fragment).chars(
#                                        trunc_len, truncate='', html=True)
#         if truncated != '':
#             excerpts.append(truncated)

#         content = content[trunc_len:]

#     text = joiner.join(excerpts)

#     return text


def is_leap_year(year):
    """Determine whether a year is a leap year."""

    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def expire_view_cache(
    view_name, args=[], namespace=None, key_prefix=None, method="GET"
):
    """
    This function allows you to invalidate any view-level cache.
        view_name: view function you wish to invalidate or it's named url pattern
        args: any arguments passed to the view function
        namepace: optioal, if an application namespace is needed
        key prefix: for the @cache_page decorator for the function (if any)

        from: https://gist.github.com/1223933
        which said:
        from: http://stackoverflow.com/questions/2268417/expire-a-view-cache-in-django
        added: method to request to get the key generating properly
    """
    from django.conf import settings
    from django.core.cache import cache
    from django.http import HttpRequest
    from django.urls import reverse
    from django.utils.cache import get_cache_key

    # create a fake request object
    request = HttpRequest()
    request.method = method
    if settings.USE_I18N:
        request.LANGUAGE_CODE = settings.LANGUAGE_CODE
    # Loookup the request path:
    if namespace:
        view_name = namespace + ":" + view_name
    request.path = reverse(view_name, args=args)
    # get cache key, expire if the cached item exists:
    key = get_cache_key(request, key_prefix=key_prefix)
    if key:
        if cache.get(key):
            cache.set(key, None, 0)
        return True
    return False


def fix_old_links(text):
    """
    Fix any old-style internal links in a piece of text, changing to new
    style.
    So far, only used when importing all the old Movable Type data.
    """
    # URLS

    # From pepysdiary.com/p/42.php
    # to   pepysdiary.com/encyclopedia/42/
    text = re.sub(
        r"pepysdiary\.com\/p\/(\d+)\.php", r"pepysdiary.com/encyclopedia/\1/", text
    )
    # From pepysdiary.com/indepth/archive/2012/12/23/slug.php
    # to   pepysdiary.com/indepth/2012/12/23/slug/
    text = re.sub(
        r"pepysdiary\.com\/indepth\/archive\/(.*?)\.php",
        r"pepysdiary.com/indepth/\1/",
        text,
    )
    # From pepysdiary.com/archive/1666/12/23/
    # or   pepysdiary.com/archive/1666/12/23/index.php
    # to   pepysdiary.com/diary/1666/12/23/
    text = re.sub(
        r"pepysdiary\.com\/archive\/(\d\d\d\d\/\d\d\/\d\d)\/(index\.php)?",
        r"pepysdiary.com/diary/\1/",
        text,
    )
    # From pepysdiary.com/letters/1666/12/23/pepys-to-evelyn.php
    # to   pepysdiary.com/letters/1666/12/23/pepys-to-evelyn/
    text = re.sub(
        r"pepysdiary\.com\/letters\/(\d\d\d\d\/\d\d\/\d\d\/[\w-]+)\.php",
        r"pepysdiary.com/letters/\1/",
        text,
    )
    # IMAGES

    # From pepysdiary.com/indepth/images/2012/05/31/SamuelPepys_1666.jpg
    # to   pepysdiary.com/static/img/indepth/2012/05/31/SamuelPepys_1666.jpg
    text = re.sub(
        r"pepysdiary\.com\/indepth\/images\/(.*?\.(?:jpg|png|gif))",
        r"pepysdiary.com/static/img/indepth/\1",
        text,
    )
    # From pepysdiary.com/about/archive/files/2012/05/31/SamuelPepys_1666.jpg
    # to   pepysdiary.com/static/img/news/2012/05/31/SamuelPepys_1666.jpg
    text = re.sub(
        r"pepysdiary\.com\/about\/archive\/files\/(.*?\.(?:jpg|png|gif))",
        r"pepysdiary.com/static/img/news/\1",
        text,
    )

    # OTHER FILES

    # From pepysdiary.com/about/archive/files/2009/03/23/ParallelLivesFlyer2009.pdf
    # to   pepysdiary.com/static/files/news/2009/03/23/ParallelLivesFlyer2009.pdf
    text = re.sub(
        r"pepysdiary\.com\/about\/archive\/files\/(.*?\.(?:mp3|pdf|doc|docx|zip|html))",
        r"pepysdiary.com/static/files/news/\1",
        text,
    )
    return text


def get_year(date_obj):
    """
    Return the year from the date like '1660', '1661', etc.
    Because strftime can't cope with very old dates.
    `date` is a date object.
    """
    return date_obj.isoformat().split("T")[0].split("-")[0]


def get_month(date_obj):
    """
    Return month from the date like '01', '02', '12', etc.
    Because strftime can't cope with very old dates.
    """
    return date_obj.isoformat().split("T")[0].split("-")[1]


def get_month_b(date_obj):
    """
    Return month from the date like 'Jan', 'Feb', 'Dec', etc.
    Because strftime can't cope with very old dates.
    """
    months = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Sep",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec",
    }
    return months[get_month(date_obj)]


def get_day(date_obj):
    """
    Return day from the date like '01', '02', '31', etc.
    Because strftime can't cope with very old dates.
    """
    return date_obj.isoformat().split("T")[0].split("-")[2]


def get_day_e(date_obj):
    """
    Return day from the date like '1', '2', '31', etc.
    Because strftime can't cope with very old dates.
    """
    d = get_day(date_obj)
    if d[:1] == "0":
        return d[1:]
    else:
        return d


def make_url_absolute(url):
    """
    Pass a url like '/encyclopedia/123/' and it will return a url more like
    'https://yourdomain.com/encyclopedia/123/'
    """
    if url.startswith("http"):
        # It's already absolute!
        return url
    else:
        protocol = "https" if settings.SECURE_SSL_REDIRECT else "http"

        domain = Site.objects.get_current().domain

        return "{}://{}{}".format(protocol, domain, url)
