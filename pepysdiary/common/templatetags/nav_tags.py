from django import template

register = template.Library()


@register.simple_tag
def get_subnav(url_name):
    """
    Determines which subnavigation is needed for the current page.

    Usage:
        {% load nav_tags %}
        {% get_subnav url_name as subnav %}
        {% if subnav == 'diary' %}
            ...
        {% endif %}

    This either returns the name of the subnav (eg, `diary`) or False, if there
    is no subnav specified for this URL name.
    """
    subnavs = (
        (
            "diary",
            (
                "home",
                "entry_archive",
                "entry_month_archive",
                "entry_detail",
                "diary_summary",
                "summary_year_archive",
                "1893_introduction",
                "1893_introduction_preface",
                "1893_introduction_previous",
                "1893_introduction_pepys",
            ),
        ),
        (
            "letters",
            (
                "letters",
                "letter_detail",
                "letter_person",
                "letter_from_person",
                "letter_to_person",
            ),
        ),
        (
            "encyclopedia",
            (
                "encyclopedia",
                "topic_detail",
                "category_map",
                "category_detail",
                "encyclopedia_familytree",
            ),
        ),
        (
            "indepth",
            (
                "indepth",
                "article_detail",
                "article_category_archive",
            ),
        ),
        (
            "news",
            (
                "news",
                "post_category_archive",
                "post_detail",
            ),
        ),
        ("recent", ("recent",)),
        (
            "about",
            (
                "about",
                "about_text",
                "about_faq",
                "about_annotations",
                "about_formats",
                "about_support",
                "about_api",
            ),
        ),
    )
    for subnav, names in subnavs:
        if url_name in names:
            return subnav
    return False
