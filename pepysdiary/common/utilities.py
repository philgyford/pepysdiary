import re

from django.utils.feedgenerator import Rss201rev2Feed


def is_leap_year(year):
    """Determine whether a year is a leap year."""

    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def expire_view_cache(view_name, args=[], namespace=None, key_prefix=None, method="GET"):
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
    from django.core.urlresolvers import reverse
    from django.http import HttpRequest
    from django.utils.cache import get_cache_key
    from django.core.cache import cache
    from django.conf import settings
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
    text = re.sub(r'pepysdiary\.com\/p\/(\d+)\.php',
                    r'pepysdiary.com/encyclopedia/\1/',
                    text)
    # From pepysdiary.com/indepth/archive/2012/12/23/slug.php
    # to   pepysdiary.com/indepth/2012/12/23/slug/
    text = re.sub(r'pepysdiary\.com\/indepth\/archive\/(.*?)\.php',
                    r'pepysdiary.com/indepth/\1/',
                    text)
    # From pepysdiary.com/archive/1666/12/23/
    # or   pepysdiary.com/archive/1666/12/23/index.php
    # to   pepysdiary.com/diary/1666/12/23/
    text = re.sub(r'pepysdiary\.com\/archive\/(\d\d\d\d\/\d\d\/\d\d)\/(index\.php)?',
                    r'pepysdiary.com/diary/\1/',
                    text)
    # From pepysdiary.com/letters/1666/12/23/pepys-to-evelyn.pyp
    # to   pepysdiary.com/letters/1666/12/23/pepys-to-evelyn/
    text = re.sub(r'pepysdiary\.com\/letters\/(\d\d\d\d\/\d\d\/\d\d\/[\w-]+)\.php',
                    r'pepysdiary.com/letters/\1/',
                    text)
    # IMAGES

    # From pepysdiary.com/indepth/images/2012/05/31/SamuelPepys_1666.jpg
    # to   pepysdiary.com/static/img/indepth/2012/05/31/SamuelPepys_1666.jpg
    text = re.sub(r'pepysdiary\.com\/indepth\/images\/(.*?\.(?:jpg|png|gif))',
                    r'pepysdiary.com/static/img/indepth/\1',
                    text)
    # From pepysdiary.com/about/archive/files/2012/05/31/SamuelPepys_1666.jpg
    # to   pepysdiary.com/static/img/news/2012/05/31/SamuelPepys_1666.jpg
    text = re.sub(r'pepysdiary\.com\/about\/archive\/files\/(.*?\.(?:jpg|png|gif))',
                    r'pepysdiary.com/static/img/news/\1',
                    text)

    # OTHER FILES

    # From pepysdiary.com/about/archive/files/2009/03/23/ParallelLivesFlyer2009.pdf
    # to   pepysdiary.com/static/files/news/2009/03/23/ParallelLivesFlyer2009.pdf
    text = re.sub(r'pepysdiary\.com\/about\/archive\/files\/(.*?\.(?:mp3|pdf|doc|docx|zip|html))',
                    r'pepysdiary.com/static/files/news/\1',
                    text)
    return text


def get_year(date_obj):
    """
    Return the year from the date like '1660', '1661', etc.
    Because strftime can't cope with very old dates.
    `date` is a date object.
    """
    return date_obj.isoformat().split('T')[0].split('-')[0]


def get_month(date_obj):
    """
    Return month from the date like '01', '02', '12', etc.
    Because strftime can't cope with very old dates.
    """
    return date_obj.isoformat().split('T')[0].split('-')[1]


def get_month_b(date_obj):
    """
    Return month from the date like 'Jan', 'Feb', 'Dec', etc.
    Because strftime can't cope with very old dates.
    """
    months = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
                '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
                '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec', }
    return months[get_month(date_obj)]


def get_day(date_obj):
    """
    Return day from the date like '01', '02', '31', etc.
    Because strftime can't cope with very old dates.
    """
    return date_obj.isoformat().split('T')[0].split('-')[2]


def get_day_e(date_obj):
    """
    Return day from the date like '1', '2', '31', etc.
    Because strftime can't cope with very old dates.
    """
    d = get_day(date_obj)
    if d[:1] == '0':
        return d[1:]
    else:
        return d


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    Should be used as the feed_type for View classes that inherit Feed.
    """
    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs

    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)
        handler.addQuickElement(u'content:encoded', item['content_encoded'])
