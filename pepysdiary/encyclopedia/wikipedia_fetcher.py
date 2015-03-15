#! -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import bleach
import requests


class WikipediaFetcher(object):

    def fetch(self, page_name):
        result = self.get_html(page_name)
        if result['success']:
            result['content'] = self.filter_html(result['content'])
        return result

    def get_html(self, page_name):
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

    def filter_html(self, html):
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

        allowed_attributes = {
            '*':        ['class', 'id'],
            'a':        ['href', 'title'],
            'abbr':     ['title'],
            'acronym':  ['title'],
            'img':      ['alt', 'src'],
            'td':       ['colspan', 'rowspan'],
            'th':       ['colspan', 'rowspan', 'scope'],
        }

        html = bleach.clean(html, tags=allowed_tags,
                                    attributes=allowed_attributes, strip=True)
        return html

