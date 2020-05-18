import smartypants

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.contrib.sites.models import Site
from django.contrib.syndication.views import add_domain, Feed
from django.db.models import F
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.html import strip_tags
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, RedirectView
from django.views.generic.base import TemplateView

from pepysdiary.common.paginator import DiggPaginator
from pepysdiary.common.utilities import ExtendedRSSFeed
from pepysdiary.annotations.models import Annotation
from pepysdiary.diary.models import Entry
from pepysdiary.encyclopedia.models import Topic
from pepysdiary.indepth.models import Article
from pepysdiary.letters.models import Letter
from pepysdiary.news.models import Post


class CacheMixin(object):
    """
    Add this mixin to a class-based view to specify caching.
    Set the cache_timeout on the view to change the timeout.
    """

    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super().dispatch)(*args, **kwargs)


class PaginatedListView(ListView):
    """Replacement for ListView that uses our DiggPaginator."""

    paginator_class = DiggPaginator
    paginate_by = 30
    page_kwarg = "page"
    allow_empty = False

    # See pepysdiary.common.paginator for what these mean:
    paginator_body = 5
    paginator_margin = 2
    paginator_padding = 2
    paginator_tail = 1

    def get_paginator(
        self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs
    ):
        """Return an instance of the paginator for this view."""
        return self.paginator_class(
            queryset,
            per_page,
            orphans=orphans,
            allow_empty_first_page=allow_empty_first_page,
            body=self.paginator_body,
            margin=self.paginator_margin,
            padding=self.paginator_padding,
            tail=self.paginator_tail,
            **kwargs
        )


class HomeView(TemplateView):
    """Front page of the whole site."""

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        # Show the most recent "published" entries:
        # If we change the number of Entries, the template will need tweaking
        # too...
        context["entry_list"] = Entry.objects.filter(
            diary_date__lte=Entry.objects.most_recent_entry_date()
        ).order_by("-diary_date")[:8]

        context["tooltip_references"] = Entry.objects.get_brief_references(
            objects=context["entry_list"]
        )

        context["post_list"] = Post.published_posts.all()[:2]
        return context


class GoogleSearchView(TemplateView):
    """Legacy view/template that uses Google's site search to provide search
    results via JavaScript.
    """

    template_name = "search_google.html"


class SearchView(PaginatedListView):
    """For searching different kinds of models.

    If adding a new Kind:
        * Add a clause for it in set_model().
        * Add an option for it in search.html.
        * Add a mention of it further down search.html ("Searching for
          [string] in [kind]").
        * Maybe customise its search result display in search.html
        * Add it to the search_tags.search_summary() template tag.

    GET arguments allowed:
        * 'q': The search term(s)
        * 'k': Kind; which model to search. Valid values are:
            * 'c': Annotation
            * 'd': Diary Entry (default)
            * 'a': Indepth Article
            * 'l': Letter
            * 'p': Site News Post
            * 't': Topic
        * 'o': Order; how to order results. Valid values are:
            * 'r': Relevancy (default)
            * 'da': Date ascending
            * 'dd': Date descending
            * 'az': Title ascending
    """

    template_name = "search.html"
    allow_empty = True

    # Will be set when we set self.model.
    # date_order_field is the model's field we use when ordering by date.
    # az_order_field is the model's field we use when ordering alphabetically.
    date_order_field = None
    az_order_field = "title"

    def dispatch(self, request, *args, **kwargs):
        """Before the parent's dispatch() method, set self.model based on
        supplied GET args.
        """
        self.set_model()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query_string = self.get_search_string()

        if query_string == "":
            queryset = self.model.objects.none()
        else:

            # if self.model == Annotation:
            #     queryset = self.model.objects.filter(comment__search=query_string)
            # else:
            query = SearchQuery(query_string)
            queryset = self.model.objects.filter(search_document=query)

            ordering = self.get_ordering()
            if ordering:
                if ordering == "-rank" or ordering == "rank":
                    # Need to annotate the queryset to display in rank order.
                    # Assumes that all our searchable models have a search_document
                    # attribute that's a SearchVectorField().
                    rank_annotation = SearchRank(F("search_document"), query)
                    queryset = queryset.annotate(rank=rank_annotation)
                queryset = queryset.order_by(ordering)

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context["model_name"] = self.model.__name__
        context["order_string"] = self.get_order_string()
        context["search_string"] = self.get_search_string()

        return context

    def get_search_string(self):
        return self.request.GET.get("q", "").strip()

    def get_order_string(self):
        return self.request.GET.get("o", "").strip()

    def get_ordering(self):
        """Get the order for the queryset, based on the 'o' GET arg.
        Assumes we've set self.model already, as orders are model-specific.
        """
        order_string = self.get_order_string()

        # Default, order by most-relevant first:
        order = "-rank"

        if order_string == "az":
            order = self.az_order_field
        elif order_string == "da":
            order = self.date_order_field
        elif order_string == "dd":
            order = "-{}".format(self.date_order_field)

        return order

    def set_model(self):
        """Work out what model we're searching, based on the 'k' GET arg.
        """
        kind = self.request.GET.get("k", "").strip()

        if kind == "a":
            self.model = Article
            self.date_order_field = "date_published"
        elif kind == "c":
            self.model = Annotation
            self.date_order_field = "submit_date"
            # We don't have a 'title' field on Annotations, so:
            self.az_order_field = "comment"
        elif kind == "l":
            self.model = Letter
            self.date_order_field = "letter_date"
        elif kind == "p":
            self.model = Post
            self.date_order_field = "date_published"
        elif kind == "t":
            self.model = Topic
            self.date_order_field = "date_created"
            self.az_order_field = "order_title"
        else:
            # 'd' and default
            self.model = Entry
            self.date_order_field = "diary_date"


class RecentView(CacheMixin, TemplateView):
    """Recent Activity page."""

    cache_timeout = 60 * 5
    template_name = "recent.html"


class BaseRSSFeed(Feed):
    feed_type = ExtendedRSSFeed

    link = "/"
    # Children should also have:
    # title
    # description

    def item_extra_kwargs(self, item):
        return {"content_encoded": self.item_content_encoded(item)}

    def item_title(self, item):
        return force_str(item.title)

    def item_pubdate(self, item):
        return item.date_published

    def item_author_name(self, item):
        return "Phil Gyford"

    def make_item_description(self, text):
        "Called by item_description() in children."
        length = 250
        text = strip_tags(text)
        if len(text) <= length:
            return force_str(text)
        else:
            return " ".join(text[: length + 1].split(" ")[0:-1]) + "..."

    def make_item_content_encoded(self, text1, text2, url, comment_name):
        """
        Called from item_content_encoded() in children.
        text1 and text2 are chunks of HTML text (or empty strings).
        url is the URL of the item (no domain needed, eg '/diary/1666/10/31/').
        comment_name is one of 'comment' or 'annotation'.
        """
        return '%s %s <p><strong><a href="%s#%ss">Read the %ss</a></strong></p>' % (
            force_str(smartypants.smartypants(text1)),
            force_str(smartypants.smartypants(text2)),
            add_domain(Site.objects.get_current().domain, url),
            comment_name,
            comment_name,
        )


# ALL THE REDIRECT VIEWS:


class DiaryMonthRedirectView(RedirectView):
    """
    To help with redirecting from old /archive/1660/01/ URLs to the
    new Diary Month URLs.
    """

    def get_redirect_url(self, year, month):
        return reverse("entry_month_archive", kwargs={"year": year, "month": month})


class DiaryEntryRedirectView(RedirectView):
    """
    To help with redirecting from old /archive/1660/01/01/index.php URLs to the
    new Diary Entry URLs.
    """

    def get_redirect_url(self, year, month, day):
        return reverse(
            "entry_detail", kwargs={"year": year, "month": month, "day": day}
        )


class EncyclopediaCategoryRedirectView(RedirectView):
    """
    To redirect from old /background/cat/subcat1/subcat2.php URLs to the new
    Category URLs.
    """

    def get_redirect_url(self, slugs):
        slugs = slugs.replace("_", "-")
        return reverse("category_detail", kwargs={"slugs": slugs})


class EncyclopediaTopicRedirectView(RedirectView):
    """
    To help with redirecting from old /p/348.php URLs to the new Topic URLs.
    """

    def get_redirect_url(self, pk):
        return reverse("topic_detail", kwargs={"pk": int(pk)})


class LetterRedirectView(RedirectView):
    """
    To help with redirecting from old /letter/1660/01/01/slug-field.php URLs
    to the new Letter URLs.
    """

    def get_redirect_url(self, year, month, day, slug):
        return reverse(
            "letter_detail",
            kwargs={"year": year, "month": month, "day": day, "slug": slug},
        )


class ArticleRedirectView(RedirectView):
    """
    To help with redirecting from old
    /indepth/archive/2012/05/31/slug_field.php URLs to the new Article URLs.
    """

    def get_redirect_url(self, year, month, day, slug):
        slug = slug.replace("_", "-")
        return reverse(
            "article_detail",
            kwargs={"year": year, "month": month, "day": day, "slug": slug},
        )


class PostRedirectView(RedirectView):
    """
    To help with redirecting from old
    /about/archive/2012/05/31/3456/ URLs to the new News Post URLs.
    """

    def get_redirect_url(self, year, month, day, pk):
        return reverse(
            "post_detail", kwargs={"year": year, "month": month, "day": day, "pk": pk}
        )


class SummaryYearRedirectView(RedirectView):
    """
    To help with redirecting from old
    /about/history/1660/ URLs to the new Summary URLs.
    """

    def get_redirect_url(self, year):
        return reverse("summary_year_archive", kwargs={"year": year})
