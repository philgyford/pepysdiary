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
        if item.summary_html:
            return self.make_item_description(item.summary_html)
        elif item.wheatley_html:
            return self.make_item_description(item.wheatley_html)
        elif item.tooltip_text:
            return self.make_item_description(item.tooltip_text)
        else:
            return ""

    def item_content_encoded(self, item):
        return self.make_item_content_encoded(
            text1=item.summary_html,
            text2=item.wheatley_html,
            url=item.get_absolute_url(),
            comment_name=item.comment_name,
        )
