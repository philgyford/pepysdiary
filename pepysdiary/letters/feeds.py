from pepysdiary.common.feeds import BaseRSSFeed

from .models import Letter


class LatestLettersFeed(BaseRSSFeed):
    title = "Pepys' Diary - Letters"
    description = "Letters sent by or to Samuel Pepys"

    def items(self):
        return Letter.objects.all().order_by("-date_created")[:3]

    def item_pubdate(self, item):
        return item.date_created

    def item_description(self, item):
        return self.make_item_description(item.text)

    def item_content_encoded(self, item):
        return self.make_item_content_encoded(
            text1=item.text,
            text2=item.footnotes,
            url=item.get_absolute_url(),
            comment_name=item.comment_name,
        )
