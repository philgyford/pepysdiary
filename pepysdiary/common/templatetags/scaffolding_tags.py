from django import template

register = template.Library()


@register.simple_tag
def full_row_start():
    return """<div class="row-fluid">
    <div class="span12">
"""


@register.simple_tag
def full_row_end():
    return """
    </div> <!-- .span12 -->
</div> <!-- .row-fluid -->
"""


@register.simple_tag
def sidebar_row_start():
    return """<div class="row-fluid">
    <div class="span8">
"""


@register.simple_tag
def sidebar_row_middle():
    return """    </div> <!-- .span8 -->
    <div class="span4">
        <div class="well">
"""


@register.simple_tag
def sidebar_row_end():
    return """      </div> <!-- .well -->
    </div> <!-- .span4 -->
</div> <!-- .row-fluid -->
"""
