from django import template
from django.utils.safestring import mark_safe

from pepysdiary.common.utilities import hilite_words, trim_hilites


register = template.Library()


@register.simple_tag()
def search_summary(obj, search_string):
    obj_name = obj.__class__.__name__

    contents = []

    if obj_name == "Entry":
        contents = [obj.text, obj.footnotes]
    elif obj_name == "Topic":
        contents = [obj.title, obj.summary_html, obj.wheatley_html]
    elif obj_name == "Annotation":
        contents = [obj.comment]
    else:
        # Letter, Article, Post
        contents = [obj.title, obj.intro_html, obj.text_html]

    content = " ".join(contents)

    content = hilite_words(content, search_string)

    content = trim_hilites(content)

    return mark_safe(content)
