import re


def fix_old_links(text):
    """
    Fix any old-style internal links in a piece of text, changing to new
    style.
    """
    # URLS

    # From pepysdiary.com/p/42.php
    # to   pepysdiary.com/encyclopedia/42/
    text = re.sub(r'pepysdiary\.com\/p\/(\d+)\.php',
                    r'pepysdiary.com/encyclopedia/\1/',
                    text)
    # From pepysdiary.com/indepth/archive/2012/12/23/slug.php
    # to   pepysdiary.com/indepth/2012/12/23/slug/
    text = re.sub(r'pepysdiary\.com\/indepth\/archive\/(.*?)\.php',
                    r'pepysdiary.com/indepth/\1/',
                    text)
    # From pepysdiary.com/archive/1666/12/23/
    # or   pepysdiary.com/archive/1666/12/23/index.php
    # to   pepysdiary.com/diary/1666/12/23/
    text = re.sub(r'pepysdiary\.com\/archive\/(\d\d\d\d\/\d\d\/\d\d)\/(index\.php)?',
                    r'pepysdiary.com/diary/\1/',
                    text)
    # From pepysdiary.com/letters/1666/12/23/pepys-to-evelyn.pyp
    # to   pepysdiary.com/letters/1666/12/23/pepys-to-evelyn/
    text = re.sub(r'pepysdiary\.com\/letters\/(\d\d\d\d\/\d\d\/\d\d\/[\w-]+)\.php',
                    r'pepysdiary.com/letters/\1/',
                    text)
    # IMAGES

    # From pepysdiary.com/indepth/images/2012/05/31/SamuelPepys_1666.jpg
    # to   pepysdiary.com/static/img/indepth/2012/05/31/SamuelPepys_1666.jpg
    text = re.sub(r'pepysdiary\.com\/indepth\/images\/(.*?\.(?:jpg|png|gif))',
                    r'pepysdiary.com/static/img/indepth/\1',
                    text)
    # From pepysdiary.com/about/archive/files/2012/05/31/SamuelPepys_1666.jpg
    # to   pepysdiary.com/static/img/news/2012/05/31/SamuelPepys_1666.jpg
    text = re.sub(r'pepysdiary\.com\/about\/archive\/files\/(.*?\.(?:jpg|png|gif))',
                    r'pepysdiary.com/static/img/news/\1',
                    text)

    # OTHER FILES

    # From pepysdiary.com/about/archive/files/2009/03/23/ParallelLivesFlyer2009.pdf
    # to   pepysdiary.com/static/files/news/2009/03/23/ParallelLivesFlyer2009.pdf
    text = re.sub(r'pepysdiary\.com\/about\/archive\/files\/(.*?\.(?:mp3|pdf|doc|docx|zip|html))',
                    r'pepysdiary.com/static/files/news/\1',
                    text)
    return text


def get_year(date_obj):
    """
    Return the year from the date like '1660', '1661', etc.
    Because strftime can't cope with very old dates.
    `date` is a date object.
    """
    return date_obj.isoformat().split('T')[0].split('-')[0]


def get_month(date_obj):
    """
    Return month from the date like '01', '02', '12', etc.
    Because strftime can't cope with very old dates.
    """
    return date_obj.isoformat().split('T')[0].split('-')[1]


def get_month_b(date_obj):
    """
    Return month from the date like 'Jan', 'Feb', 'Dec', etc.
    Because strftime can't cope with very old dates.
    """
    months = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
                '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
                '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec', }
    return months[get_month(date_obj)]


def get_day(date_obj):
    """
    Return day from the date like '01', '02', '31', etc.
    Because strftime can't cope with very old dates.
    """
    return date_obj.isoformat().split('T')[0].split('-')[2]


def get_day_e(date_obj):
    """
    Return day from the date like '1', '2', '31', etc.
    Because strftime can't cope with very old dates.
    """
    d = get_day(date_obj)
    if d[:1] == '0':
        return d[1:]
    else:
        return d

