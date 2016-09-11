import os

import mediawiki.parsing
from mediawiki.helpers import *


def load_page_title_id_dictionary():
    connection = sqlite3.connect(database_filename)
    cursor = connection.cursor()
    cursor.execute("select title, id from en_wikipedia_page")
    return dict(cursor.fetchall())


def load_category_title_id_dictionary():
    connection = sqlite3.connect(database_filename)
    cursor = connection.cursor()
    cursor.execute("select name, page_ptr_id from en_wikipedia_category")
    return dict(cursor.fetchall())


def load_redirect_dictionary():
    connection = sqlite3.connect(database_filename)
    cursor = connection.cursor()
    cursor.execute("select page_ptr_id, target_id from en_wikipedia_redirect")
    return dict(cursor.fetchall())


def load_target_resolution_dictionary():
    title_id = load_page_title_id_dictionary()
    redirect_dict = load_redirect_dictionary()
    for title in title_id.keys():
        try:
            title_id[title] = redirect_dict[title_id[title]]
        except:
            continue
    return title_id


def third_pass_commit(link_queue, category_queue, category_link_queue):
    connection = sqlite3.connect(database_filename)
    cursor = connection.cursor()
    # Store to database
    cursor.executemany("insert into en_wikipedia_categorylink(source_id, target_id) values (?,?)", category_link_queue)
    cursor.executemany("insert into en_wikipedia_article_categories(article_id, category_id) values (?,?)", category_queue)
    #cursor.executemany("insert into en_wikipedia_articlelink(source_id, target_id, label) values (?,?,?)", link_queue)
    cursor.executemany("insert into en_wikipedia_articlelink(source_id, target_id) values (?,?)", link_queue)
    connection.commit()


def mediawiki_parser_third_pass(xml_filename):
    """Third pass:
    identify subcateries, store category links
    extract and resolve links
    extract categories for pages"""

    # Load id_title dictionary into memory for faster reverse indexing
    target_dict = load_target_resolution_dictionary()
    category_id_dict = load_category_title_id_dictionary()
    count = 0

    link_queue = set()
    category_link_queue = set()
    category_queue = set()

    parsed_pages = mediawiki.parsing.MediaWikiPages(xml_filename)
    for page in parsed_pages:
        if page.is_redirect():
            continue
        count += 1
        namespace, title = parse_title(page['title'])
        if namespace == 'Category':
            # Category links on a category page are subcategories.
            try:
                category_id = category_id_dict[title]
            except:
                continue
            links = page['links']
            for link in links:
                parsed_link = parse_link(link)
                # If there is a category link on the page, the page is a subcategory of that category
                try:
                    if parsed_link['target'].startswith('Category'):
                        super_id = category_id_dict[ parse_title(parsed_link['target'])[1].strip()]
                        category_link_queue.add( (category_id, super_id ))
                except:
                    pass
            continue
        elif namespace:
            continue
        # Presummably we've got an ordinary page now.
        links = page['links']
        for link in links:
            parsed_link = parse_link(link)
            #if parsed_link['namespace'] == 'Category':
            if 'target' not in parsed_link:
                continue
            if parsed_link['target'].startswith('Category'):
                try:
                    category_id = category_id_dict[ parse_title(parsed_link['target'])[1].strip()]
                    category_queue.add((page['id'], category_id) )
                except:
                    pass
                continue
            elif parsed_link['namespace']:
                continue
            else:
                try:
                    target_id = target_dict[ denormalize_title(normalize_title(parsed_link['target']))]
                    #link_queue.append( (page['id'], target_id, parsed_link['display']) )
                    link_queue.add( (page['id'], target_id) )
                except:
                    pass

        if not (count % 10000):
            print(count)
            third_pass_commit(link_queue, category_queue, category_link_queue)
            link_queue = set()
            category_link_queue = set()
            category_queue = set()
    third_pass_commit(link_queue, category_queue, category_link_queue)

def second_pass_commit(redirect_queue, article_queue):
    connection = sqlite3.connect(database_filename)
    cursor = connection.cursor()
    # Store to database
    cursor.executemany("insert into en_wikipedia_redirect(page_ptr_id, target_id) values (?,?)", redirect_queue)
    cursor.executemany("insert into en_wikipedia_article(page_ptr_id) values (?)", article_queue)
    connection.commit()

def mediawiki_parser_second_pass(xml_filename):
    """Second pass:
    identify and resolve redirects """
    # Load id_title dictionary into memory for faster reverse indexing
    title_id = load_page_title_id_dictionary()
    count = 0
    redirect_queue = []
    article_queue = []

    parsed_pages = mediawiki.parsing.MediaWikiPages(xml_filename)
    for page in parsed_pages:
        if page.is_redirect():
            # Determine the redirect target id
            # need to parse the link
            parsed_link = parse_link(page['redirect target'])
            if parsed_link['namespace']:
                if parsed_link['namespace'] not in ['Category', 'Wikipedia']:
                    continue
            try:
                target_name = parsed_link['target']
                target = denormalize_title(normalize_title(target_name))
                target_id = title_id[target]
                #print target, target_id
                if not target_id:
                    target_id = 0
                # Add to database queue
                redirect_queue.append( (page['id'], target_id)  )
            except:
                # log failures? they are less than 0.1 %
                #print page['text'], parsed_link
                continue
        namespace, title = parse_title(page['title'])
        if namespace:
            continue
        else:
            # Its an article.
            article_queue.append((page['id'],))
        count += 1
        if not (count % 100000):
            print(count)
            second_pass_commit(redirect_queue, article_queue)
            redirect_queue = []
            article_queue = []
    second_pass_commit(redirect_queue, article_queue)

def first_pass_commit(pages_db_queue):

    connection = sqlite3.connect(database_filename)
    cursor = connection.cursor()
    # Store to database
    cursor.executemany("insert into en_wikipedia_page(id, title, last_modified) values (?,?,?)", pages_db_queue)
    categories = [(a,b.split(':')[1]) for (a,b,c) in pages_db_queue if b.startswith('Category:')]
    if categories:
        cursor.executemany("insert into en_wikipedia_category(page_ptr_id, name, main_article_id) values (?,?,null)", categories)
    connection.commit()

def mediawiki_parser_first_pass(xml_filename):
    """ First pass:
    extract page id, title, identify category pages from title"""

    count = 0
    pages_db_queue = []

    parsed_pages = mediawiki.parsing.MediaWikiPages(xml_filename)
    for page in parsed_pages:
        print(page['title'])
        pages_db_queue.append((page['id'], page['title'], page['timestamp']))
        count += 1

        if not (count % 100000):
            print(count)
            # first_pass_commit(pages_db_queue)
            pages_db_queue = []
    # first_pass_commit(pages_db_queue)


def parse(wiki_xml_filename):
    # database_filename = '/home/marc/code/wikipedia/derived/en_wikipedia.sqlite'
    # create_database()
    mediawiki_parser_first_pass(wiki_xml_filename)
    # mediawiki_parser_second_pass(wiki_xml_filename)
    # mediawiki_parser_third_pass(wiki_xml_filename)
    # create_indices()

if __name__ == "__main__":
    wiki_xml_filename = "/ssd/enwiki-20160601-pages-articles.xml"
    parse(wiki_xml_filename)
