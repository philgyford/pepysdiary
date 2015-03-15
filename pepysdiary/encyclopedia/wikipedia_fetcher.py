#! -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import bleach
import requests


class WikipediaFetcher(object):

    def fetch(self, page_name):
        """
        Passed a Wikipedia page's URL fragment, like
        'Edward_Montagu,_1st_Earl_of_Sandwich', this will fetch the page's
        main contents, tidy the HTML, strip out any elements we don't want
        and return the final HTML string.
        """
        result = self._get_html(page_name)

        if result['success']:
            result['content'] = self._tidy_html(result['content'])

        return result

    def _get_html(self, page_name):
        """
        Passed the name of a Wikipedia page (eg, 'Samuel_Pepys'), it fetches
        the HTML content (not the entire HTML page) and returns it.

        Returns either the HTML text or None, if there was an error.
        """
        error_message = ''
        
        url = 'https://en.wikipedia.org/wiki/%s' % page_name

        try:
            response = requests.get(url, params={'action':'render'}, timeout=5)
        except requests.exceptions.ConnectionError as e:
            error_message = "Can't connect to domain."
        except requests.exceptions.Timeout as e:
            error_message = "Connection timed out."
        except requests.exceptions.TooManyRedirects as e:
            error_message = "Too many redirects."

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # 4xx or 5xx errors:
            error_message = "HTTP Error: %s" % response.status_code
        except NameError:
            if error_message == '':
                error_message = "Something unusual went wrong."

        if error_message:
            return {'success': False, 'content': error_message} 
        else:
            return {'success': True, 'content': response.text}

    def _tidy_html(self, html):
        """
        Passed the raw Wikipedia HTML, this returns valid HTML, with all
        disallowed elements stripped out.
        """
        html = self._bleach_html(html)
        html = self._strip_html(html)
        return html

    def _bleach_html(self, html):
        """
        Ensures we have valid HTML; no unclosed or mis-nested tags.
        Removes any tags and attributes we don't want to let through.
        Doesn't remove the contents of any disallowed tags.
        """

        # Pretty much most elements, but no forms or audio/video.
        allowed_tags = [
            'a', 'abbr', 'acronym', 'address', 'area', 'article',
            'b', 'blockquote', 'br',
            'caption', 'cite', 'code', 'col', 'colgroup',
            'dd', 'del', 'dfn', 'div', 'dl', 'dt',
            'em',
            'figcaption', 'figure', 'footer',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hgroup', 'hr',
            'i', 'img', 'ins',
            'kbd',
            'li',
            'map',
            'nav',
            'ol',
            'p', 'pre',
            'q',
            's', 'samp', 'section', 'small', 'span', 'strong', 'sub', 'sup',
            'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'time', 'tr',
            'ul',
            'var',
        ]

        # These attributes will be removed from any of the allowed tags.
        allowed_attributes = {
            '*':        ['class', 'id'],
            'a':        ['href', 'title'],
            'abbr':     ['title'],
            'acronym':  ['title'],
            'img':      ['alt', 'src', 'srcset'],
            # Ugh. Don't know why this page doesn't use .tright like others
            # http://127.0.0.1:8000/encyclopedia/5040/
            'table':    ['align'],
            'td':       ['colspan', 'rowspan'],
            'th':       ['colspan', 'rowspan', 'scope'],
        }

        return bleach.clean(html, tags=allowed_tags,
                                    attributes=allowed_attributes, strip=True)

    def _strip_html(self, html):
        """
        Takes out any tags, and their contents, that we don't want at all.
        And adds custom classes to existing tags (so we can apply CSS styles
        without having to multiply our CSS).
        """

        # CSS selectors. Strip these and their contents.
        selectors = [
            'div.hatnote',
            'div.navbar.mini', # Will also match div.mini.navbar
            # Bottom of https://en.wikipedia.org/wiki/Charles_II_of_England :
            'div.topicon',
            'a.mw-headline-anchor',
        ]

        # Strip any element that has one of these classes.
        classes = [
            # "This article may be expanded with text translated from..."
            # https://en.wikipedia.org/wiki/Afonso_VI_of_Portugal
            'ambox-notice',
            'magnify',
            # eg audio on https://en.wikipedia.org/wiki/Bagpipes
            'mediaContainer',
            'navbox',
            'noprint',
        ]

        # Any element has a class matching a key, it will have the classes
        # in the value added.
        add_classes = {
            # Give these tables standard Bootstrap styles.
            'infobox':   ['table', 'table-bordered'],
            'ambox':     ['table', 'table-bordered'],
            'wikitable': ['table', 'table-bordered'],
        } 

        soup = BeautifulSoup(html)

        for selector in selectors:
            [tag.decompose() for tag in soup.select(selector)]

        for clss in classes:
            [tag.decompose() for tag in soup.find_all(attrs={'class':clss})]

        for clss, new_classes in add_classes.iteritems():
            for tag in soup.find_all(attrs={'class':clss}):
                tag['class'] = tag.get('class', []) + new_classes

        # Depending on the HTML parser BeautifulSoup used, soup may have
        # surrounding <html><body></body></html> or just <body></body> tags.
        if soup.body:
            soup = soup.body
        elif soup.html:
            soup = soup.html.body

        # Put the content back into a string.
        html = ''.join(str(tag) for tag in soup.contents)

        return html

