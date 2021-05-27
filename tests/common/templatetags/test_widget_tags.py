from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse

from pepysdiary.common.templatetags.widget_tags import (
    admin_link_change,
    summary_year_navigation,
)
from pepysdiary.common.utilities import make_date, make_datetime
from pepysdiary.encyclopedia import topic_lookups
from pepysdiary.encyclopedia.factories import CategoryFactory, TopicFactory
from pepysdiary.indepth.factories import DraftArticleFactory, PublishedArticleFactory
from pepysdiary.news.factories import DraftPostFactory, PublishedPostFactory


class TwitterAndEmailTestCase(TestCase):
    def test_output(self):
        "Just check it generates some of the correct HTML."
        context = Context({})
        template_to_render = Template("{% load widget_tags %}{% twitter_and_email %}")
        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            '<h1 class="aside-title">Email, Twitter &amp;&nbsp;Mastodon</h1>',
            rendered_template,
        )

        self.assertInHTML(
            '<p>Follow in real time <a href="http://twitter.com/samuelpepys" '
            'title="@samuelpepys">on&nbsp;Twitter</a> or '
            '<a href="https://mastodon.social/@samuelpepys" '
            'title="@samuelpepys@mastodon.social">on&nbsp;Mastodon</a></p>',
            rendered_template,
        )


class CreditTestCase(TestCase):
    def test_output(self):
        "Just check it generates some of the correct HTML."
        context = Context({})
        template_to_render = Template("{% load widget_tags %}{% credit %}")
        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            '<h1 class="aside-title">About</h1>',
            rendered_template,
        )

        self.assertInHTML(
            '<p><a href="/about/">More about this site</a></p>',
            rendered_template,
        )


class RSSFeedsTestCase(TestCase):
    def test_all_feeds(self):
        "By default rss_feeds() should include all the feed links"
        context = Context({})
        template_to_render = Template("{% load widget_tags %}{% rss_feeds  %}")
        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            '<h1 class="aside-title">RSS feeds</h1>',
            rendered_template,
        )

        self.assertIn("https://feeds.feedburner.com/PepysDiary", rendered_template)
        self.assertIn(
            "https://feeds.feedburner.com/PepysDiary-Encyclopedia", rendered_template
        )
        self.assertIn(
            "https://feeds.feedburner.com/PepysDiary-InDepthArticles", rendered_template
        )
        self.assertIn(
            "https://feeds.feedburner.com/PepysDiary-SiteNews", rendered_template
        )

    def test_only_one_feed(self):
        "rss_feeds() should only include the Diary Entries RSS feed link if asked"
        context = Context({})
        template_to_render = Template("{% load widget_tags %}{% rss_feeds 'entries' %}")
        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            '<h1 class="aside-title">RSS feeds</h1>',
            rendered_template,
        )

        self.assertInHTML(
            '<ul class="feeds"><li class="feed"><a href="https://feeds.feedburner.com/PepysDiary">Diary entries</a></li></ul>',  # noqa: E501
            rendered_template,
        )

    def test_invalid_kind(self):
        "It should quiety ignore any invalid kinds it's given"
        context = Context({})
        template_to_render = Template("{% load widget_tags %}{% rss_feeds 'foo' %}")
        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            '<h1 class="aside-title">RSS feeds</h1>',
            rendered_template,
        )

        self.assertInHTML('<ul class="feeds"></ul>', rendered_template)


class LatestPostsTestCase(TestCase):
    def test_output(self):
        "Check it includes the correct objects in the correct order."

        posts = []

        for n in range(1, 6):
            post = PublishedPostFactory(
                title=f"Post {n}",
                date_published=make_datetime(f"2021-04-0{n} 12:00:00"),
            )
            posts.append(post)

        # Should not be included:
        PublishedPostFactory(
            title="Post 6", date_published=make_datetime("2021-03-31 12:00:00")
        )
        DraftPostFactory(
            title="Draft Post", date_published=make_datetime("2021-04-10 12:00:00")
        )

        context = Context({"date_format_long": "Y-m-d"})
        template_to_render = Template("{% load widget_tags %}{% latest_posts %}")
        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            '<h1 class="aside-title">Latest Site News</h1>',
            rendered_template,
        )

        self.assertIn("Post 1", rendered_template)
        self.assertIn("Post 2", rendered_template)
        self.assertIn("Post 3", rendered_template)
        self.assertIn("Post 4", rendered_template)
        self.assertIn("Post 5", rendered_template)
        self.assertNotIn("Post 6", rendered_template)
        self.assertNotIn("Draft Post", rendered_template)

        # Quick check that they're in the correct order, and with correct HTML.
        self.assertInHTML(
            f"""
            <dt><a href="{posts[-1].get_absolute_url()}">Post 5</a></dt>
            <dd class="text-muted">2021-04-05</dd>
            <dt><a href="{posts[-2].get_absolute_url()}">Post 4</a></dt>
            <dd class="text-muted">2021-04-04</dd>
            """,
            rendered_template,
        )


class LatestArticlesTestCase(TestCase):
    def test_output(self):
        "Check it includes the correct objects in the correct order."

        articles = []

        for n in range(1, 6):
            article = PublishedArticleFactory(
                title=f"Article {n}",
                date_published=make_datetime(f"2021-04-0{n} 12:00:00"),
            )
            articles.append(article)

        # Should not be included:
        PublishedArticleFactory(
            title="Article 6", date_published=make_datetime("2021-03-31 12:00:00")
        )
        DraftArticleFactory(
            title="Draft Article", date_published=make_datetime("2021-04-10 12:00:00")
        )

        context = Context({"date_format_long": "Y-m-d"})
        template_to_render = Template("{% load widget_tags %}{% latest_articles %}")
        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            '<h1 class="aside-title">Latest In-Depth Articles</h1>',
            rendered_template,
        )

        self.assertIn("Article 1", rendered_template)
        self.assertIn("Article 2", rendered_template)
        self.assertIn("Article 3", rendered_template)
        self.assertIn("Article 4", rendered_template)
        self.assertIn("Article 5", rendered_template)
        self.assertNotIn("Article 6", rendered_template)
        self.assertNotIn("Draft Article", rendered_template)

        # Quick check that they're in the correct order, and with correct HTML.
        self.assertInHTML(
            f"""
            <dt><a href="{articles[-1].get_absolute_url()}">Article 5</a></dt>
            <dd class="text-muted">2021-04-05</dd>
            <dt><a href="{articles[-2].get_absolute_url()}">Article 4</a></dt>
            <dd class="text-muted">2021-04-04</dd>
            """,
            rendered_template,
        )


class LatestTopicsTestCase(TestCase):
    def test_output(self):
        "Check it includes the correct objects in the correct order."
        topics = []

        for n in range(1, 6):
            topic = TopicFactory(
                title=f"Topic {n}",
            )
            topic.date_created = make_datetime(f"2021-04-0{n} 12:00:00")
            topic.save()
            topics.append(topic)

        # Should not be included; too old:
        topic = TopicFactory(title="Topic 6")
        topic.date_created = make_datetime("2021-03-31 12:00:00")
        topic.save()

        context = Context({"date_format_long": "Y-m-d"})
        template_to_render = Template("{% load widget_tags %}{% latest_topics %}")
        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            '<h1 class="aside-title">Latest Encyclopedia Topics</h1>',
            rendered_template,
        )

        self.assertIn("Topic 1", rendered_template)
        self.assertIn("Topic 2", rendered_template)
        self.assertIn("Topic 3", rendered_template)
        self.assertIn("Topic 4", rendered_template)
        self.assertIn("Topic 5", rendered_template)
        self.assertNotIn("Topic 6", rendered_template)

        # Quick check that they're in the correct order, and with correct HTML.
        self.assertInHTML(
            f"""
            <dt><a href="{topics[-1].get_absolute_url()}">Topic 5</a></dt>
            <dd class="text-muted">2021-04-05</dd>
            <dt><a href="{topics[-2].get_absolute_url()}">Topic 4</a></dt>
            <dd class="text-muted">2021-04-04</dd>
            """,
            rendered_template,
        )


class AllArticlesTestCase(TestCase):
    def test_output(self):
        "Check it includes the correct objects in the correct order."

        articles = []

        for n in range(1, 6):
            article = PublishedArticleFactory(
                title=f"Article {n}",
                date_published=make_datetime(f"2021-04-0{n} 12:00:00"),
                slug=f"article-{n}",
            )
            articles.append(article)

        # Should not be included:
        DraftArticleFactory(
            title="Draft Article", date_published=make_datetime("2021-04-10 12:00:00")
        )

        context = Context({"date_format_long": "Y-m-d"})
        template_to_render = Template("{% load widget_tags %}{% all_articles %}")
        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            '<h1 class="aside-title">All In-Depth Articles</h1>',
            rendered_template,
        )

        self.assertIn("Article 1", rendered_template)
        self.assertIn("Article 2", rendered_template)
        self.assertIn("Article 3", rendered_template)
        self.assertIn("Article 4", rendered_template)
        self.assertIn("Article 5", rendered_template)
        self.assertNotIn("Draft Article", rendered_template)

        # Quick check that they're in the correct order, and with correct HTML.
        self.assertInHTML(
            f"""
            <li><a href="{articles[-1].get_absolute_url()}">Article 5</a><br>
            2021-04-05</li>
            <li><a href="{articles[-2].get_absolute_url()}">Article 4</a><br>
            2021-04-04</li>
            """,
            rendered_template,
        )

    def test_exclude_id(self):
        "It shouldn't link the exclude_id Article"
        article_1 = PublishedArticleFactory(
            title="Article 1",
            date_published=make_datetime("2021-04-01 12:00:00"),
            slug="article-1",
        )
        article_2 = PublishedArticleFactory(
            title="Article 2",
            date_published=make_datetime("2021-04-02 12:00:00"),
        )

        context = Context({"date_format_long": "Y-m-d"})
        template_to_render = Template(
            "{% load widget_tags %}{% all_articles exclude_id="
            + str(article_2.pk)
            + " %}"
        )
        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            f"""
            <li>Article 2<br>
            2021-04-02</li>
            <li><a href="{article_1.get_absolute_url()}">Article 1</a><br>
            2021-04-01</li>
            """,
            rendered_template,
        )


class SummaryYearNavigationTestCase(TestCase):
    def test_before_active(self):
        "It should output the correct HTML when current_year='before'"
        result = summary_year_navigation("before")

        self.assertInHTML(
            '<a class="list-group-item active" href="/diary/summary/">Before the diary</a>',  # noqa: E501
            result,
        )

    def test_year_active(self):
        "It should output the correct HTML when current_year is a Date object"
        result = summary_year_navigation(make_date("1663-01-01"))

        self.assertInHTML(
            '<a class="list-group-item active" href="/diary/summary/1663/">1663</a>',
            result,
        )


class FamilyTreeLinkTestCase(TestCase):
    def test_output_with_with_topic_on_tree(self):
        "It should output the correct HTML when a Topic on the tree is supplied"
        topic = TopicFactory(on_pepys_family_tree=True)
        template_to_render = Template(
            "{% load widget_tags %}{% family_tree_link topic=topic %}"
        )
        rendered_template = template_to_render.render(Context({"topic": topic}))

        self.assertIn(
            "See this person on the Pepys family&nbsp;tree", rendered_template
        )

    def test_output_with_with_topic_not_on_tree(self):
        "It should output the correct HTML when a Topic NOT on the tree is supplied"
        topic = TopicFactory(on_pepys_family_tree=False)
        template_to_render = Template(
            "{% load widget_tags %}{% family_tree_link topic=topic %}"
        )
        rendered_template = template_to_render.render(Context({"topic": topic}))

        self.assertNotIn(
            "See this person on the Pepys family&nbsp;tree", rendered_template
        )

    def test_output_with_no_topic(self):
        "It should output the correct HTML when no Topic is supplied"
        template_to_render = Template("{% load widget_tags %}{% family_tree_link %}")
        rendered_template = template_to_render.render(Context())

        self.assertNotIn(
            "See this person on the Pepys family&nbsp;tree", rendered_template
        )


class PepysWealthLinkTestCase(TestCase):
    def test_output(self):
        "It should output some of the correct HTML"
        template_to_render = Template("{% load widget_tags %}{% pepys_wealth_link %}")
        rendered_template = template_to_render.render(Context({}))

        self.assertInHTML(
            '<h1 class="aside-title">Samuel Pepys’s wealth</h1>',
            rendered_template,
        )

        url = reverse("topic_detail", kwargs={"pk": topic_lookups.PEPYS_WEALTH})

        self.assertInHTML(
            f'<a href="{url}">See his wealth during the diary</a>',
            rendered_template,
        )


class CategoryMapLink(TestCase):
    def test_output_with_no_category(self):
        "It should output correct HTML when no category ID is supplied"
        template_to_render = Template("{% load widget_tags %}{% category_map_link %}")
        rendered_template = template_to_render.render(Context({}))

        self.assertInHTML(
            '<h1 class="aside-title">Maps</h1>',
            rendered_template,
        )

        url = reverse("category_map")

        self.assertInHTML(
            f'<a href="{url}">See places from the Diary on a&nbsp;map</a>',
            rendered_template,
        )

    def test_output_with_category(self):
        "It should output correct HTML when a category ID is supplied"
        category = CategoryFactory()

        template_to_render = Template(
            "{% load widget_tags %}{% category_map_link category_id="
            + str(category.pk)
            + " %}"
        )
        rendered_template = template_to_render.render(Context({}))

        self.assertInHTML(
            '<h1 class="aside-title">Maps</h1>',
            rendered_template,
        )

        url = reverse("category_map", kwargs={"category_id": category.pk})

        self.assertInHTML(
            f'<a href="{url}">See all places in this category on one&nbsp;map</a>',
            rendered_template,
        )


class AdminLinkChangeTestCase(TestCase):
    def test_output(self):
        self.assertEqual(
            admin_link_change("/foo/"),
            """<p class="admin-links"><a class="admin" href="/foo/">Edit</a></p>""",
        )


class DetailedTopicsTestCase(TestCase):
    def test_output(self):
        "Check it outputs some of the correct HTML"
        template_to_render = Template("{% load widget_tags %}{% detailed_topics %}")
        rendered_template = template_to_render.render(Context({}))

        url = reverse("topic_detail", kwargs={"pk": 150})

        self.assertInHTML(f"""<a href="{url}">Elizabeth Pepys</a>""", rendered_template)
