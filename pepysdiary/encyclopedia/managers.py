#! -*- coding: utf-8 -*-
import re

from django.db import models
from django.utils import timezone

from pepysdiary.encyclopedia.wikipedia_fetcher import WikipediaFetcher


class TopicManager(models.Manager):

    def pepys_homes_ids(self):
        """The IDs of the Topics about the places Pepys has lived."""
        return [102, 1023, ]

    def fetch_wikipedia_texts(self, topic_ids=[]):
        """
        Passed a list of Topic IDs, this calls the method that fetches and
        munges the Wikipedia HTML for any of those Topics that have
        `wikipedia_fragment`s set.

        topic_ids is either a list of topic IDs (ints), or the string 'all'.
        By default, this method will fetch nothing.

        Returns the number of Topics whose HTML was successfully fetched.
        (Doesn't count Topics with no texts, or where something went wrong
        when fetching the text.)
        """
        updated_count = 0 
        topics = None

        if topic_ids == 'all':
            topics = self.model.objects.exclude(wikipedia_fragment__exact='') 
        else:
            topics = self.model.objects.filter(pk__in=topic_ids).exclude(
                                                wikipedia_fragment__exact='') 

        fetcher = WikipediaFetcher()

        if topics is not None:
            for topic in topics:
                result = fetcher.fetch(topic.wikipedia_fragment)
                if result['success'] == True:
                    topic.wikipedia_html = result['content']
                    topic.wikipedia_last_fetch = timezone.now()
                    topic.save()
                    updated_count += 1

        return updated_count

    def make_order_title(self, text, is_person=False):
        """
        If is_person we change:

        "Fred Bloggs" to "Bloggs, Fred"
        "Sidney Smythe (1st Lord Smythe)" to "Smythe, Sidney (1st Lord Smythe)"
        "Sir Heneage Finch (Solicitor-General)" to "Finch, Sir Heneage (Solicitor-General)"
        "Capt. Henry Terne" to "Terne, Capt. Henry"
        "Capt. Aldridge" to "Aldridge, Capt."
        "Mr Hazard" to "Hazard, Mr"
        "Johann Heinrich Alsted" to "Alsted, Johann Heinrich"
        "Monsieur d'Esquier" to "Esquier, Monsieur d'"
        "Adriaen de Haes" to "Haes, Adriaen de"
        "Jan de Witt (Grand Pensionary of Holland)" to "Witt, Jan de (Grand Pensionary of Holland)"
        "Peter de la Roche" to "Roche, Peter de la"
        "Monsieur du Prat" to "Prat, Monsieur du"
        "Catherine of Braganza (Queen)" to "Braganza, Catherine of (Queen)"
        "Michiel van Gogh (Dutch Ambassador, 1664-5)" to "Gogh, Michiel van (Dutch Ambassador, 1664-5)"
        "Mr Butler (Mons. L'impertinent)" to "Butler, Mr (Mons. L'impertinent)"

        Stay the same:
        "Mary (c, Pepys' chambermaid)"
        "Shelston"
        "Mary I of England"
        "Philip IV (King of Spain, 1621-1665)"
        "Ivan the Terrible"

        If not is_person we change:
        "The Royal Prince" to "Royal Prince, The"
        "The Alchemist (Ben Jonson)" to "Alchemist, The (Ben Jonson)"
        """
        order_title = text

        if is_person:
            # First we take off any bit in parentheses at the end.
            name_match = re.match(r'^(.*?)(?:\s)?(\(.*?\))?$', text)
            parentheses = ''
            if name_match is not None:
                matches = name_match.groups()
                if matches[1] is not None:
                    parentheses = ' %s' % matches[1]
                # The actual name part of the string:
                name = matches[0]

            pattern = """
                # Optionally match a title:
                (Ald\.|Capt\.|Col\.|Don|Dr|Lady|Lieut\.|Lord|Lt-Adm\.|Lt-Col\.|Lt-Gen\.|Maj\.(?:-Gen\.)?(?:\sAld\.)?(?:\sSir)?|Miss|(?:Mrs?)|Ms|Pope|Sir)?
                # Ignore any space after a title:
                (?:\s)?
                # Match a single first name:
                (.*?)
                # Match any other names up until the end:
                (?:\s(.*?))?
                # That's it:
                $
            """
            name_match = re.match(pattern, name, re.VERBOSE)
            if name_match is None:
                # Leave it as it is.
                pass
            else:
                matches = list(name_match.groups())

                # We need to trap anything that's like:
                # "Mary I of England"
                # "Philip IV (King of Spain, 1621-1665)"
                # "Ivan the Terrible"
                king_match = None
                if matches[2] is not None:
                    king_match = re.match(r'^(I|II|III|IV|V|VI|VII|VIII|XI|XIV|the)(?:\s|$)',
                                                                    matches[2])
                if king_match is not None:
                    # Looks like it's a king-type person.
                    # Leave the text as it was.
                    pass
                else:
                    # Save any title, plus a space, or just nothing:
                    title = ''
                    if matches[0] is not None:
                        title = '%s' % (matches[0])

                    if matches[2] is not None:
                        # The "surname" part has something in it.

                        if matches[2][:1] == '(':
                            # eg, (None, 'Mary', "(c, Pepys' chambermaid)", None)
                            # leave it as-is.
                            pass
                        elif matches[1][-1:] == ',':
                            # eg, (None, 'Godefroy,', "Comte d'Estrades")
                            # leave it as-is.
                            pass
                        else:
                            # A little fix first for surnames like "d'Esquier".
                            # We want to move any leading "d'" or "l'" from the
                            # start of the surname to the end of the first names.
                            # So that we'll order by "Esquier".
                            apostrophe_match = re.match(r"^(d'|l'|al-)(.*?)$", matches[2])
                            if apostrophe_match is not None:
                                # Will be something like ("d'", "Esquier"):
                                apostrophe_matches = apostrophe_match.groups()
                                # Will be like "Monsieur d'":
                                matches[1] = '%s %s' % (matches[1], apostrophe_matches[0])
                                # Will be like "Esquier":
                                matches[2] = apostrophe_matches[1]

                            # See what's in the "surname" part.
                            # One word or more?
                            surname_match = re.match(
                                                r'^(.*)(?:\s)(.*?)$', matches[2])
                            if surname_match is None:
                                # "surname" was just one word, simple.
                                # eg, (None, 'Fred', 'Bloggs', None)
                                if title == '':
                                    order_title = '%s, %s%s' % (matches[2],
                                                        matches[1], parentheses)
                                else:
                                    order_title = '%s, %s %s%s' % (matches[2],
                                                title, matches[1], parentheses)
                            else:
                                # "surname" has more than one word.
                                # eg, (None, 'Adriaen', 'de Haes', None)
                                surname_matches = surname_match.groups()
                                # surname_matches might now be like:
                                # ('de la', 'Roche')
                                pre_surname = ''
                                if surname_matches[0]:
                                    pre_surname = ' %s' % surname_matches[0]
                                order_title = '%s, %s%s%s%s' % (surname_matches[1],
                                        title, matches[1], pre_surname, parentheses)
                    elif title != '':
                        # eg, ('Mr', 'Hazard', None)
                        # Need to remove extra space from title, eg 'Mr ':
                        if parentheses == '':
                            order_title = '%s, %s' % (matches[1], title)
                        else:
                            order_title = '%s, %s%s' % (matches[1], title, parentheses)
                    else:
                        pass

        else:
            the_pattern = re.compile(r'^The\s(.*?)(?:\s\((.*?)\))?$')
            the_match = the_pattern.match(text)
            if the_match is not None:
                # Starts with 'The '.
                matches = the_match.groups()
                if matches[1] is None:
                    # eg, ('Royal Prince', None)
                    order_title = '%s, The' % matches[0]
                else:
                    # eg, ('Alchemist', 'Ben Jonson')
                    order_title = '%s, The (%s)' % (matches[0], matches[1])

        return order_title

