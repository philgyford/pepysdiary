from django.conf import settings
from django.utils.timezone import now

from pepysdiary.common.models import Config

# Things that we want to be available in the context of every page.


def date_formats(request):
    return {
        # Monday 31st December 2012
        'date_format_longest': 'l jS F Y',

        # 31 December 2012
        'date_format_long': 'j F Y',
        'date_format_long_strftime': '%d %B %Y',

        # 31 Dec 2012
        'date_format_mid': 'j M Y',
        'date_format_mid_strftime': '%d %b %Y',

        # 12:39PM (apply "|lower" to it too)
        'time_format': 'g:iA',
        # May want to do .lstrip('0').lower() on this:
        'time_format_strftime': '%I:%M%p',

        # We also include a datetime object of the time now.
        # Why? Because the {% now %} template tag doesn't seem to accept
        # variables for a format, so we can't use all those formats above.
        # So we also send this so we can do {{ time_now|time_format }} etc.
        'time_now': now(),
    }


def api_keys(request):
    return {
        'MAPBOX_MAP_ID': settings.MAPBOX_MAP_ID,
        'MAPBOX_ACCESS_TOKEN': settings.MAPBOX_ACCESS_TOKEN,
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
    }


def config(request):
    return {'config': Config.objects.get_site_config()}


def url_name(request):
    """
    So we can test things in the templates based on the current named URL.
    """
    url_name = False
    if request.resolver_match:
        url_name = request.resolver_match.url_name
    return {'url_name': url_name}

