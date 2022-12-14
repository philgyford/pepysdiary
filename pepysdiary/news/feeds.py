from pepysdiary.common.feeds import BaseRSSFeed

from .models import Post


class LatestPostsFeed(BaseRSSFeed):
    title = "The Diary of Samuel Pepys - Site News"
    description = "News about the Diary of Samuel Pepys website"

    def items(self):
        return Post.published_posts.all().order_by("-date_published")[:3]

    def item_description(self, item):
        return self.make_item_description(item.intro_html)

    def item_content_encoded(self, item):
        return self.make_item_content_encoded(
            texts=[item.intro_html, item.text_html],
            url=item.get_absolute_url(),
            comment_name=item.comment_name,
        )
