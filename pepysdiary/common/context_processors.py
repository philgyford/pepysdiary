
# Things that we want to be available in the context of every page.


def date_formats(request):
    return {
        'date_format_longest': 'l jS F Y',
        'date_format_long': 'j F Y',
        'date_format_mid': 'j M Y',
        'time_format': 'g:ia',
    }
