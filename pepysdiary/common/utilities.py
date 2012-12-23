import re


def fix_old_links(text):
    """
    Fix any old-style internal links in a piece of text, changing to new
    style.
    """
    # From pepysdiary.com/p/42.php
    # to   pepysdiary.com/encyclopedia/42/
    text = re.sub(r'pepysdiary.com\/p\/(\d+)\.php',
                    r'pepysdiary.com/encyclopedia/\1/',
                    text)
    # From pepysdiary.com/indepth/archive/2012/12/23/slug.php
    # to   pepysdiary.com/indepth/2012/12/23/slug/
    text = re.sub(r'pepysdiary.com\/indepth\/archive\/(.*?)\.php',
                    r'pepysdiary.com/indepth/\1/',
                    text)
    # From pepysdiary.com/archive/1666/12/23/
    # or   pepysdiary.com/archive/1666/12/23/index.php
    # to   pepysdiary.com/diary/1666/12/23/
    text = re.sub(r'pepysdiary.com\/archive\/(\d\d\d\d\/\d\d\/\d\d)\/(index\.php)?',
                    r'pepysdiary.com/diary/\1/',
                    text)
    # From pepysdiary.com/letters/1666/12/23/pepys-to-evelyn.pyp
    # to   pepysdiary.com/etters/1666/12/23/pepys-to-evelyn/
    text = re.sub(r'pepysdiary.com\/letters\/(\d\d\d\d\/\d\d\/\d\d\/[\w-]+)\.php',
            r'pepysdiary.com/letters/\1/',
            text)
    return text
