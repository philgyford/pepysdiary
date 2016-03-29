# -*- coding: utf-8 -*-
from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.simple_tag
def map_key():
    """
    The description under both maps.
    """
    return mark_safe("""
<div class="text-muted mapkey">
    <p>The overlays that highlight 17th century London features are approximate and derived from:</p>
    <ul>
        <li>Built-up London – <a href="http://link.library.utoronto.ca/hollar/digobject.cfm?Idno=Hollar_k_2465&amp;size=zoom&amp;query=london&amp;type=search">Hollar's 1666 map before the Fire</a></li>
        <li>City of London wall and Great Fire damage – <a href="http://commons.wikimedia.org/wiki/File:Map.London.gutted.1666.jpg">Hollar's 1666 map after the Fire</a></li>
    </ul>
</div>
""")

