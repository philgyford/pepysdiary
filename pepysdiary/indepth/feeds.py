from pepysdiary.common.feeds import BaseRSSFeed

from .models import Article


class LatestArticlesFeed(BaseRSSFeed):
    title = "The Diary of Samuel Pepys - In-Depth Articles"
    description = "Articles about Samuel Pepys and his world"

    def items(self):
        return Article.published_articles.all().order_by("-date_published")[:2]

    def item_description(self, item):
        return self.make_item_description(item.intro_html)

    def item_content_encoded(self, item):
        return self.make_item_content_encoded(
            texts=[item.intro_html, item.text_html],
            url=item.get_absolute_url(),
            comment_name=item.comment_name,
        )
