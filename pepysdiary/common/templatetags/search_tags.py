from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from pepysdiary.common.utilities import hilite_words, trim_hilites


register = template.Library()


@register.simple_tag()
def search_summary(obj, search_string):
    """
    Returns the HTML to display search results summary text for an object.

    It's a series of bits of the object's text fields that contain the
    searched-for string, with the search term highlighted.

    obj - One of Annotation, Article, Entry, Letter, Post, Topic
    search_string - The string that was searched for.
    """
    obj_name = obj.__class__.__name__

    contents = []

    if obj_name == "Entry":
        contents = [obj.text, obj.footnotes]
    elif obj_name == "Topic":
        contents = [obj.title, obj.summary_html, obj.wheatley_html, obj.wikipedia_html]
    elif obj_name == "Annotation":
        contents = [obj.comment]
    elif obj_name == "Letter":
        contents = [obj.title, obj.text, obj.footnotes]
    else:
        # Article, Post
        contents = [obj.title, obj.intro_html, obj.text_html]

    content = " ".join(contents)

    content = hilite_words(content, search_string)

    hilites = trim_hilites(content, allow_empty=False, max_hilites_to_show=10)

    if hilites["hilites_shown"] < hilites["total_hilites"]:
        difference = hilites["total_hilites"] - hilites["hilites_shown"]
        extra = f" <em>and {difference} more.</em>"
    else:
        extra = ""

    return format_html("{}{}", mark_safe(hilites["html"]), mark_safe(extra))
