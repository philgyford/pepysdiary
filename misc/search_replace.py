from pepysdiary.indepth.models import Article
from pepysdiary.news.models import Post
from pepysdiary.encyclopedia.models import Topic

# This was used to replace all the instances of old Media URLs with new
# ones. Saved in case we need it, or similar, again.


to_find = 'http://www.pepysdiary.com/media/'
to_replace = '/media/'


def replace_func(field_name, find_str, replace_str):
    return Func(
        F(field_name),
        Value(find_str), Value(replace_str),
        function='replace'
    )


Article.objects.update(
    intro       = replace_func('intro', to_find, to_replace),
    intro_html  = replace_func('intro_html', to_find, to_replace),
    text        = replace_func('text', to_find, to_replace),
    text_html   = replace_func('text_html', to_find, to_replace),
)

Post.objects.update(
    intro       = replace_func('intro', to_find, to_replace),
    intro_html  = replace_func('intro_html', to_find, to_replace),
    text        = replace_func('text', to_find, to_replace),
    text_html   = replace_func('text_html', to_find, to_replace),
)

Topic.objects.update(
    summary = replace_func('summary', to_find, to_replace),
    summary_html  = replace_func('summary_html', to_find, to_replace),
)

