from pepysdiary.common.feeds import BaseRSSFeed

from .models import Entry


class LatestEntriesFeed(BaseRSSFeed):
    title = "The Diary of Samuel Pepys"
    description = "Daily entries from the 17th century London diary"

    def items(self):
        return Entry.objects.filter(
            diary_date__lte=Entry.objects.most_recent_entry_date()
        ).order_by("-diary_date")[:5]

    def item_description(self, item):
        return self.make_item_description(item.text)

    def item_author_name(self, item):
        return "Samuel Pepys"

    def item_content_encoded(self, item):
        footnotes = ""
        if item.footnotes:
            footnotes = f"<p><strong>Footnotes</strong></p>{item.footnotes_for_rss}"

        return self.make_item_content_encoded(
            texts=[item.text_for_rss, footnotes],
            url=item.get_absolute_url(),
            comment_name=item.comment_name,
        )
