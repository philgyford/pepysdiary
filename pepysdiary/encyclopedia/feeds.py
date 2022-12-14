from pepysdiary.common.feeds import BaseRSSFeed

from .models import Topic


class LatestTopicsFeed(BaseRSSFeed):
    title = "Pepys' Diary - Encyclopedia Topics"
    description = "New topics about Samuel Pepys and his world"

    def items(self):
        return Topic.objects.all().order_by("-date_created")[:8]

    def item_pubdate(self, item):
        return item.date_created

    def item_description(self, item):
        desc = ""

        if item.summary_html:
            desc = item.summary_html
        elif item.wheatley_html:
            desc = item.wheatley_html
        elif item.tooltip_text:
            desc = item.tooltip_text

        return self.make_item_description(desc)

    def item_content_encoded(self, item):
        text1 = ""

        if item.summary_html:
            text1 = item.summary_html
        elif item.tooltip_text:
            text1 = f"<p>{item.tooltip_text}</p>"

        return self.make_item_content_encoded(
            texts=[text1, item.wheatley_html],
            url=item.get_absolute_url(),
            comment_name=item.comment_name,
        )
