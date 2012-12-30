from django.conf import settings

# Things that we want to be available in the context of every page.


def date_formats(request):
    return {
        'date_format_longest': 'l jS F Y',
        'date_format_long': 'j F Y',
        'date_format_mid': 'j M Y',
        'time_format': 'g:ia',
    }


def api_keys(request):
    return {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
    }
