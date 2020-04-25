# -*- coding: utf-8 -*-
from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.simple_tag
def map_key():
    """
    The description under both maps.
    """
    return mark_safe(
        """
<div class="text-muted mapkey">
    <p>The overlays that highlight 17th century London features are approximate and derived from <a href="https://www.pepysdiary.com/encyclopedia/10563/">Wenceslaus Hollar’s</a> maps:</p>
    <ul>
        <li>Built-up London – <a href="https://artsandculture.google.com/asset/map-of-london-before-the-fire-of-1666-wenceslaus-hollar/nAH1rSiZWIibkA?hl=en">London before the Fire</a></li>
        <li>City of London wall and Great Fire damage – <a href="http://commons.wikimedia.org/wiki/File:Map.London.gutted.1666.jpg">London after the Fire</a></li>
    </ul>
</div>
"""
    )
