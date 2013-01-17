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
        # 12:39p.m.
        'time_format': 'g:ia',

        # We also include a datetime object of the time now.
        # Why? Because the {% now %} template tag doesn't seem to accept
        # variables for a format, so we can't use all those formats above.
        # So we also send this so we can do {{ time_now|time_format }} etc.
        'time_now': now(),
    }


def api_keys(request):
    return {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
    }


def config(request):
    return {'config': Config.objects.get_site_config()}
