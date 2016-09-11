from collections import namedtuple
import sys

from dateutil import parser as date_parser


from mediawiki.access import get_session
from mediawiki.models import setup_database, Category, Page
from mediawiki.parsing import MediaWikiPages


PageTuple = namedtuple("PageTuple", [
    "id", "title", "timestamp"])

CategoryTuple = namedtuple("CategoryTuple", [
    "id", "title", "timestamp"])

def page_tuple_from_page(page):
    pt = PageTuple(
        id = page['id'],
        title = page["title"],
        timestamp = date_parser.parse(page["timestamp"])
    )
    return pt

def first_pass_commit(page_tuples):
    session = get_session()
    session.bulk_insert_mappings(Page, [pt._asdict() for pt in page_tuples])
    cts = [ct for ct in page_tuples if ct.title.startswith('Category:')]
    session.bulk_insert_mappings(Category, [pt._asdict() for pt in page_tuples])

    # session.bulk_insert_mappings(Category, [
    #     {"id": page[0], "title": page[1]} for page in categories])
    # categories = [(a, b.split(':')[1]) for (a, b, c) in pages
    #               if b.startswith('Category:')]
    # session.bulk_insert_mappings(Page,[
    #     {"id": page[0], "title": page[1]} for page in pages])


    session.commit()

def mediawiki_parser_first_pass(xml_filename):
    """ First pass:
    extract page id, title, identify category pages from title"""

    page_tuples = []

    parsed_pages = MediaWikiPages(xml_filename)
    for count, page in enumerate(parsed_pages):
        # print(page['title'])
        page_tuples.append(page_tuple_from_page(page))

        if not (count % 10000):
            print(count)
            first_pass_commit(page_tuples)
            page_tuples = []
    first_pass_commit(page_tuples)


def parse(wiki_xml_filename):
    # database_filename = '/home/marc/code/wikipedia/derived/en_wikipedia.sqlite'
    # create_database()
    mediawiki_parser_first_pass(wiki_xml_filename)
    # mediawiki_parser_second_pass(wiki_xml_filename)
    # mediawiki_parser_third_pass(wiki_xml_filename)
    # create_indices()


def main(echo=False):
    setup_database(echo=echo, drop=True)
    wiki_xml_filename = "/ssd/enwiki-20160601-pages-articles.xml"
    parse(wiki_xml_filename)

if __name__ == "__main__":
    try:
        if sys.argv[1] == "echo":
            echo = True
    except:
        echo = False
    main(echo=echo)
