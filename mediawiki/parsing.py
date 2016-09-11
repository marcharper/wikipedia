from collections import defaultdict
import re

import xml.etree.cElementTree as ETree

from .helpers import extract_templates

class NonexistantPageAttributeError(Exception):
    pass


class MediaWikiPage(object):
    """Wrapper for parsed page data. Access the page information through the
     dictionary interface. Accessible keys are ['title', 'id', 'timestamp', ]
     'text', 'links', 'templates', 'redirect target']. One of more of these may ]
     not exist (text in the case of an image page for instance) in which case
     NonexistantPageAttributeError is raised, but 'title' and 'id' will always
     exist for a validating mediawiki xml dump. Access is lazy since some of
     the extraction operations (such as templates) are expensive."""
    
    redirect_regex = re.compile('\#REDIRECT\s*(\[\[.*?\]\])', re.VERBOSE | re.IGNORECASE)
    links_regex = re.compile('\[\[.*?\]\]')
    nowiki_regex = re.compile('<nowiki>.*?</nowiki>', re.IGNORECASE | re.DOTALL)
    math_regex = re.compile('<math>.*?</math>', re.IGNORECASE | re.DOTALL)
    # template_variable_regex = re.compile('\{\{\{(?P<match>[^\{\}]*?)\}\}\}', re.DOTALL)
    extractibles = ['links', 'templates', 'redirect target']

    def __init__(self, page_data=None, include_nowiki=False):
        self.page_data = page_data
        self.extracted = defaultdict(lambda x: False)
        self.extracts = defaultdict(list)
        if not include_nowiki:
            self.remove_nowiki(page_data)

    def remove_nowiki(self):
        text = self.text
        if not text:
            return
        if (not nowiki_include):
            # Remove anything inside a <nowiki> tag, which is not intended
            # for markup.
            page_data['revision']['text'] = self.nowiki_regex.sub('', self.text)

    @property
    def id(self):
        return self.page_data['id']

    @property
    def title(self):
        return self.page_data['title']

    @property
    def timestamp(self):
        return self.page_data['revision']['timestamp']

    @property
    def text(self):
        ## Add argument to extract <nowiki>
        # https://stackoverflow.com/questions/5715620/python-how-to-pass-more-than-one-argument-to-the-property-getter
        return self.page_data['revision']['text']

    def is_redirect(self):
        target = self.redirect_target()
        if target:
            return True
        return False

    @property
    def redirect_target(self):
        if not self.extracted['redirect target']:
            text = self.text
            m = self.redirect_regex.match(text)
            if m:
                target = m.group(1)
                self.extracts['redirect target'] = target
            else:
                self.extracts['redirect target'] = None
            self.extracted['redirect target'] = True
        return self.extracts['redirect target']


    def _find_links(self):
        self.extracts['links'] = self.links_regex.findall(self['text'])

    @property
    def links(self):
        if not self.extracted['links']:
            self._find_links()
            self.extracted['links'] = True
        return self.extracts['links']

    # @property
    # def categories(self):
    #     # if not self.extracted['links']:
    #     #     self._find_links()
    #     #     self.extracted['links'] = True
    #     # return self.extracts['links']
    #     pass

    def _find_templates(self):
        self.extracts['templates'] = extract_templates(self['text'])

    @property
    def templates(self):
        if not self.extracted['templates']:
            self._find_templates()
            self.extracted['templates'] = True
        return self.extracts['templates']


class MediaWikiPages(object):
    """Page iterator for MediaWiki XML dumps. Locates and returns <page> tag trees as dictionaries."""
    
    def __init__(self, xml_filename):
        # Attempt to open the file.
        try:
            if xml_filename.endswith('.gz'):
                import gzip
                handle = gzip.GzipFile(xml_filename)
            else:
                handle = open(xml_filename, encoding="utf-8")
        except:
            print("Could not open file %s" % xml_filename)
            exit()

        # Prepare an iterator for the xml tree.
        self._xml_tree = iter(ETree.iterparse(
            handle, events=("start", "end")))
        
        # Get the root element so the used portions of the tree can be freed
        # from memory periodically.
        # _, self.root = self._xml_tree.next()
        _, self.root = next(self._xml_tree)
        self.root.clear()

        # Initialize self._event and friends for next()
        self._next_event_element()
        
    def _next_event_element(self):
        try:
            self._event, self._xml_element = next(self._xml_tree)
        except StopIteration:
            raise StopIteration
        # Separate out the namespace if present.
        ## -- Probably a better way to do this.
        if '}' in self._xml_element.tag:
            self._namespace, self._tag_name = tuple(self._xml_element.tag.split('}'))
        else: 
            self._namespace, self._tag_name = "", self._xml_element.tag

    def __iter__(self):
        return self

    def __next__(self):
        references = [{'page': dict()}]
        current_dict = None
        
        # Find the next "<page> tag"
        while not ( (self._event == "start") and (self._tag_name == "page") ):
            self._next_event_element()
        
        # Build the page tree into a dictionary and return.
        while not ( (self._event == "end") and (self._tag_name == "page") ):
            if self._event == 'end':
                # If no children add to the current dictionary.
                if not len(self._xml_element):
                    references.pop()
                    references[-1][self._tag_name] = self._xml_element.text
                else:
                    references[-1][self._tag_name] = current_dict
                    references.pop()
            elif self._event == 'start':
                current_dict = references[-1][self._tag_name] = dict()
                references.append(current_dict)
            self._next_event_element()
        # Cleanup and return
        self.root.clear()
        return MediaWikiPage(references[0]['page'])
