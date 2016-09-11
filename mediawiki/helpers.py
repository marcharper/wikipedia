# -*- coding: utf-8 -*-
from collections import namedtuple
from html.entities import name2codepoint
import re
from urllib.parse import unquote

import mediawiki


# ParsedLink = namedtuple("ParsedLink",
#                         ["target", "display", "language", "namespace",
#                          "interwiki"])


class LinkNormalizationError(Exception):
    pass

## Extraction

def findall(s, sub):
    """Finds beginning indicies of all non-overlapping instances of sub in string s."""
    indicies = []
    jump = len(sub)
    s = s.replace('\n',' ')
    i = s.find(sub)
    # find returns -1 if the substring is not found
    while (i + 1):
        indicies.append(i)
        i = s.find(sub, i + jump)
    return indicies


def extract_templates(text):
    """Wikipedia pages contain templates of the form {{*}} that can be nested
    and contain a lot of valuable metadata. This function extracts the templates
    from a given input string."""
    # Extract the template variables of the form {{{_}}} because they make the rest of the process much more difficult
    # text = template_variable_regex.sub('<var>\g<name><\var>', text)
    start_token = '{{'
    end_token = '}}'
    start_indicies = findall(text, start_token)
    if not start_indicies:
        return []
    end_indicies = findall(text, end_token)
    if not end_indicies:
        return []

    ## Zip up the tokens and token locations. Merge and sort.
    token_indicies = [(x, start_token) for x in start_indicies]
    token_indicies.extend([(x, end_token) for x in end_indicies])
    token_indicies.sort()

    depth = 0
    new_start = True

    templates = []

    for (index, token) in token_indicies:
        if token == start_token:
            depth += 1
            if new_start:
                start = index
                new_start = False
        if token == end_token:
            # Ignore mismatched end tokens.
            if new_start:
                continue
            else:
                depth -= 1
        if not depth:
            templates.append(text[start: index] + end_token)
            new_start = True
    return templates


## Parsing Normalization

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def denormalize_title(title):
    return title.replace('_', ' ')

def normalize_title(title):
    """Normalizes title by removing outer whitespace and replacing interior
    whitespace by '_' and capitalizing the first character. See
    http://en.wikipedia.org/wiki/Wikipedia:Naming_conventions
    for more information."""

    if not title:
        return ''
    title = '_'.join(title.split())
    try:
        title = unquote(unescape(title))
    except UnicodeDecodeError:
        print(title)
        return ''

    # Wikipedia defines its own escape codes.
    replacement_codes = dict([('&ndash;', '–'), ('&mdash;', '—')])
    for k, v in replacement_codes.items():
        title = title.replace(k, v)
    if len(title) > 0:
        return title[0].capitalize() + title[1:]
    elif len(title) == 1:
        return title[0].capitalize()
    else:
        return ''

def parse_title(title):
    if not ':' in title:
        return ('', title)
    title_split = title.split(':')
    if title_split[0].lower() not in mediawiki.mediawiki_namespaces:
        return ('', title)
    return (title_split[0], ':'.join(title_split[1:]))

def normalize_link(link, page_title=None):
    """Normalizes a link by making the following transformations, of which some require the page title.
    (1) Any amount of interior whitespace is converted to '_'.
    (2) Pipe tricks:
        [[a (b)|]] -> [[a (b)|a]]
        [[a, b|]] -> [[a, b|a]]
        [[namespace:b|]] -> [[namespace:b|b]]
        In fact, any text before a colon is ignored.
    (3) Reverse pipe tricks:
        [[|b]] -> [[b (c)|b]] (on pages with titles of the form 'a (c)'
        [[|b]] -> [[b, c|b]] (on pages with titles of the form 'a, c'
        If the reverse pipe trick is used on a page without a comma or parentheses, the pipe is simply removed.
    (4) Anchoring:
        [[#a|b]] -> [[page_name#a|b]]
    See http://en.wikipedia.org/wiki/Help:Pipe_trick for documentation of the pipe trick and also http://en.wikipedia.org/wiki/Help:Magic.
    """

    # Check if input has brackets
    if link.startswith('[[') and link.endswith(']]'):
        link = link[2:-2]
    # If the page leads with an anchor, insert the current page.
    if link.startswith('#'):
        # Check if the page_title was given.
        if page_title is None:
            raise LinkNormalizationError('Page title needed to resolve empty anchor.')
        else:
            link = page_title + link
    # Check if it starts with a colon, as in the case of [[:Category:Continents|]]
    leading_colon = False
    if link.startswith(':'):
        leading_colon = True
        link = link[1:]
    #link = normalize_title(link)
    link = link.strip()
    # Pipe trick
    if link.endswith('|'):
        # Remove the pipe.
        link = link[:-1]
        if '(' in link:
            # Split on the last colon, if present.
            if ':' in link:
                colon_split = link.rsplit(':',1)
                start = colon_split[1].strip()
            else:
                start = link
            # Split on the '('
            start_split = start.rsplit(' (', 1)
            # Glue it back together
            link = "|".join([link, start_split[0]])
        elif ',' in link:
            # Split on the last colon, if present.
            if ':' in link:
                colon_split = link.rsplit(':',1)
                comma = colon_split[1].strip()
            else:
                comma = link
            # Split on the comma
            comma_split = comma.rsplit(',', 1)
            # Glue it back together
            link = "|".join([link, comma_split[0]])
        else:
            if ':' in link:
                colon_split = link.rsplit(':',1)
                link = '|'.join([link, colon_split[1]])
            else:
                # Just remove the pipe, which has already been done
                pass
    # Reverse pipe trick
    if link.startswith('|'):
        # Check if the page_title was given.
        if page_title is None:
            raise LinkNormalizationError('Page title needed to resolve reverse pipe trick.')
        else:
            # Remove the pipe.
            link = link[1:]
        #[[|b]] -> [[b (c)|b]] (on pages with titles of the form 'a (c)'
        #[[|b]] -> [[b, c|b]] (on pages with titles of the form 'a, c'
            if '(' in page_title:
                link = "|".join([" (".join([link, page_title.split("(")[1]]), link] )
                pass
            elif ',' in page_title:
                link = "|".join([", ".join([link, page_title.split(',',1)[1].strip()]), link])
    if leading_colon:
        link = ':' + link
    return '[[%s]]' % link

def parse_link(link, language='en'):
    try:
        link = normalize_link(link)
    except LinkNormalizationError:
        pass
    return_dict = {'namespace': '', 'interwiki': '', 'target': '',
                   'language': language, 'display': ''}
    # Check if input has brackets
    if link.startswith('[[') and link.endswith(']]'):
        link = link[2:-2]
    #Determine display name if '|' present
    if '|' in link:
        link, return_dict['display'] = link.rsplit('|',1)
    #Look for anchor
    if '#' in link:
        link, return_dict['anchor'] = link.rsplit('#',1)
    #Examine namespace
    colon_start = False
    if link.startswith(':'):
        link = link[1:]
        colon_start = True
    if ':' not in link:
        return_dict['target'] = link
    else:
        # Examine the namespace
        link_split = link.split(':', 1)
        if link_split[0] in mediawiki.mediawiki_language_codes:
            # It's a language link
            return_dict['language'], link = link_split
        if ':' in link:
            link_split = link.split(':', 1)
            if link_split[0].lower() in mediawiki.mediawiki_namespaces:
                return_dict['namespace'] = link_split[0]
                if link_split[0].lower() == 'category' and not colon_start:
                    return_dict['namespace'] = ''
                return_dict['target'] = link
            elif link_split[0].lower() in mediawiki.mediawiki_interwiki_prefix:
                return_dict['interwiki'] = link_split[0]
                return_dict['target'] = link
            else:
                return_dict['target'] = link
    if not return_dict['display']:
        return_dict['display'] = link
    return return_dict

def parse_category_link(link):
    """ Parses a category link. Piping has a different meaning for category
    links, which are not ordinary links. In particular, a category link with a
    pipe is of the following form [[Category:category_name|sort_key]]. sort_key
    is used to change the display order on the category page and otherwise does
    not effect the category link, so for categorization purposes, it is
    equivalent to [[Category:category_name]]."""
    if '|' in link:
        link = link.rsplit('|')[0] + ']]'
    return link

