import datetime
import pytz

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse_lazy

from pepysdiary.diary.models import Entry
from pepysdiary.encyclopedia.models import Topic
from pepysdiary.indepth.models import Article
from pepysdiary.letters.models import Letter
from pepysdiary.news.models import Post


class EntrySitemap(Sitemap):
    """Lists all Diary Entries for the sitemap."""
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return Entry.objects.all()

    def lastmod(self, obj):
        return obj.date_modified


class LetterSitemap(Sitemap):
    """Lists all Letters for the sitemap."""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Letter.objects.all()

    def lastmod(self, obj):
        return obj.date_modified


class TopicSitemap(Sitemap):
    """Lists all Topics for the sitemap."""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Topic.objects.all()

    def lastmod(self, obj):
        return obj.date_modified


class ArticleSitemap(Sitemap):
    """Lists all In-Depth Articles for the sitemap."""
    changefreq = 'never'
    priority = 0.5

    def items(self):
        return Article.published_articles.all()

    def lastmod(self, obj):
        return obj.date_published


class PostSitemap(Sitemap):
    """Lists all Site News Posts for the sitemap."""
    changefreq = 'never'
    priority = 0.5

    def items(self):
        return Post.published_posts.all()

    def lastmod(self, obj):
        return obj.date_published


class AbstractSitemapClass():
    """
    An abstract class for defining static page's attributes.
    """
    changefreq = 'daily'
    url = None

    def get_absolute_url(self):
        return self.url


class StaticSitemap(Sitemap):
    """
    The place to add general one-off pages to the Sitemap.
    Just add them and their URL to the pages list.
    """
    changefreq = 'hourly'
    priority = 1

    pages = {
                'home': reverse_lazy('home'),
                'recent': reverse_lazy('recent'),
                'letters': reverse_lazy('letters'),
                'encyclopedia': reverse_lazy('encyclopedia'),
                'indepth': reverse_lazy('indepth'),
                'news': reverse_lazy('news'),
            }

    # def __init__(self):
    #     """
    #     Set the lastmod to either the date of the most recent Article,
    #     or now (if there's no published Article).
    #     """
    #     try:
    #         a = Article.published_articles.latest('date_published')
    #         self.lastmod = a.date_published
    #     except:
    #         self.lastmod = datetime.datetime.now(pytz.utc)

    main_sitemaps = []
    for page in pages.keys():
        sitemap_class = AbstractSitemapClass()
        sitemap_class.url = pages[page]
        main_sitemaps.append(sitemap_class)

    def items(self):
        return self.main_sitemaps
