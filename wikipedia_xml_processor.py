# -*- coding: utf-8 -*-
import codecs
import csv
#import gc
import shelve
import cPickle as pickle
import os

from mediawiki.parsing import MediaWikiPages, MediaWikiPage
from mediawiki.helpers import parse_link, parse_title, normalize_title, denormalize_title
from mediawiki.csv_unicode import UnicodeReader, UnicodeWriter

from pagerank import pagerank
from operator import itemgetter, attrgetter

#{'id': {'type':'int', 'list':False}, 'title': {'type':'str', 'list':False}, 'in_links': {'type':'int', 'list':True}, 'out_links': {'type':'int', 'list':True}, 'category_title': {'type':'str', 'list':False}, 'articles': {'type':'int', 'list':True}, 'categories': {'type':'int', 'list':True}}



#def pickle_dictionaries():
    #import cPickle as pickle
    #d = load_title_dict()
    #output = open('id_title.pickle', 'wb')
    #pickle.dump(d, output)

#def load_pickle_dict():
    #import cPickle as pickle
    #infile = open('id_title.pickle')
    #d = pickle.load(infile)

#def shelve_dictionaries():
    #import shelve
    #d = shelve.open('id_title.shelve')
    #c = shelve.open('id_category.shelve')
    #reader = UnicodeReader(codecs.open('id_title.csv', encoding='utf-8'))
    #for row in reader:
    #try:
        #source_id, title = row
        #namespace, title = parse_title(title)
        #if namespace == "Category":
        #c[title.encode('utf-8')] = int(source_id)
        #else:    #reader = csv.reader(codecs.open('id_title.csv', encoding='utf-8'))
    #shelve_csv_dictionary(reader, 'id_title.shelve', values_as_lists=False)

        #d[title.encode('utf-8')] = int(source_id)
    #except ValueError:
        #pass
    #print source_id
    #d.close()
    #c.close()

def load_out_links_dict():
    out_links_reader = csv.reader(codecs.open('links.csv', encoding='utf-8'))
    d = []
    for row in out_links_reader:
        d[int(row[0])] = map(int, row[2:])
    return d

def load_title_dict():
    reader = UnicodeReader(codecs.open('id_title.csv', encoding='utf-8'))
    rows = list(reader)
    d = dict()
    for row in rows:
        try:
            source_id, title = row
        except ValueError:
            #print source_id, title
            pass
        d[title] = int(source_id)
    return d

def load_redirect_dict():
    reader = UnicodeReader(codecs.open('redirects.csv', encoding='utf-8'))
    rows = list(reader)
    d = dict()
    for row in rows:
        try:
            source_id, target_id = row
        except ValueError:
            pass
        d[int(source_id)] = int(target_id)
    return d

def load_target_counts():
    reader = csv.reader(codecs.open('out_counts.csv', encoding='ascii'))
    d = dict()
    for source, targets in reader:
        d[int(source)] = int(targets)
    return d

def load_in_links():
    reader = csv.reader(codecs.open('in_links.csv', encoding='ascii'))
    d = dict()
    for row in reader:
        d[int(row[0])] = map(int, row[1:])
    return d

def index_links():
    titles = load_title_dict()
    redirects = load_redirect_dict()
    links_reader = UnicodeReader(codecs.open('raw_out_links.csv', encoding='utf-8'))
    out_links_writer = csv.writer(codecs.open('out_links.csv', mode='w', encoding='ascii'))
    id_categories_writer = csv.writer(codecs.open('id_categories.csv', mode='w', encoding='utf-8'))
    categories_writer = csv.writer(codecs.open('article_categories.csv', mode='w', encoding='ascii'))
    category_links_writer = csv.writer(codecs.open('category_links.csv', mode='w', encoding='ascii'))

    for row in links_reader:
        try:
            source_id, source_title, links = row[0], row[1], row[2:]
        except ValueError:
            continue
        # Is this a category page?
        page_namespace, title = parse_title(source_title)
        if page_namespace == "Category":
            page_is_category = True
            source_title = title
            id_categories_writer.writerow([source_id, source_title])
        else:
            page_is_category = False
        new_row = [source_id]
        categories = [source_id]
        for link in links:
            is_category = False
            # Is it an actual page link?
            try:
            parsed_link = parse_link(link)
            target_title = parsed_link['target']
            except KeyError:
            continue
            #Is is a category link?
            if parsed_link['target'].startswith('Category:'):
            _, title = parse_title(parsed_link['target'])
            is_category = True
            target_title = denormalize_title(normalize_title(target_title))
            if '#' in target_title:
            split = target_title.split('#')[:-1]
            target_title = '#'.join(split)
            # Does it link to a real page or a page of interest?
            try:
            target_id = titles[target_title]
            except KeyError:
            continue
            # Resolve redirects.
            if target_id in redirects:
            target_id = redirects[target_id]
            if is_category:
            categories.append(target_id)
            else:
            new_row.append(target_id)
        if page_is_category:
            category_links_writer.writerow(categories)
        else:
            out_links_writer.writerow(new_row)
            categories_writer.writerow(categories)

def index_redirects():
    titles = load_title_dict()
    reader = UnicodeReader(codecs.open('id_redirect.csv', encoding='utf-8'))
    writer = csv.writer(codecs.open('redirects.csv', mode='w', encoding='ascii'))
    for row in reader:
        try:
            source_id, title = row
        except ValueError:
            continue
        try:
            # Redirect might land on an anchor, reroute to page.
            target_title = denormalize_title(normalize_title(title))
            if '#' in target_title:
            split = target_title.split('#')[:-1]
            target_title = '#'.join(split)
            target_id = titles[target_title]
            writer.writerow([int(source_id), target_id])
        except KeyError:
            print source_id, title, target_title
	
def extract_link_graph(page_gen):
    id_title_writer = UnicodeWriter(codecs.open('id_title.csv', mode='w', encoding='utf-8'))
    redirect_writer = UnicodeWriter(codecs.open('id_redirect.csv', mode='w', encoding='utf-8'))
    links_writer = UnicodeWriter(codecs.open('raw_out_links.csv', mode='w', encoding='utf-8'))
    # We don't care about metawiki pages, portal pages, language links, and such, so we will filter by namespace. We do want Category data though.
    namespaces = ['', 'Category']
    for page in page_gen:
        page_id = page['id']
        page_title = page['title']
        page_namespace, _ = parse_title(page_title)
        if page_namespace not in namespaces:
            continue
        id_title_writer.writerow([page_id, page_title])	
        if page.is_redirect():
                parsed_link = parse_link(page['redirect target'])
            try:
                target_title = parsed_link['target']
                target_namespace, _ = parse_title(target_title)
                if target_namespace not in namespaces:
                    continue
                target_title = denormalize_title(normalize_title(target_title))
                redirect_writer.writerow([page_id, target_title])
            except KeyError:
                continue
        else:
            row = [page_id, page_title]
            page_links = page['links']
            for link in page_links:
                parsed_link = parse_link(link)
                try:
                    target_title = denormalize_title(normalize_title(parsed_link['target']))
                    row.append(target_title)
                except KeyError:
                    continue
            links_writer.writerow(row)

def process_xml():
    # Access XML Database with SAX parser.
    wikipedia_xml_filename = '/media/sda2/enwiki/enwiki-20080103-pages-articles.xml'
    page_gen = MediaWikiPages(wikipedia_xml_filename)
    # Extract desired data: titles, ids, links, and categories, including category links.
    extract_link_graph(page_gen)
    index_redirects()
    index_links()

def shelve_csv_dictionary(csv_reader, shelve_filename, values_as_lists=False, value_map=str):
    d = shelve.open(shelve_filename)
    for row in csv_reader:
    try:
        key = str(row[0]) # Shelve keys are strings.
    except IndexError:
        print row
        continue
    try:
        if values_as_lists:
            value = map(int, row[1:])
        else:
            #value = int(row[1])
            value = value_map(row[1])
            d[key] = value
    except ValueError:
    pass
    d.close()

def create_shelves():
    # Create shelves.
    names = ['target_counts', 'category_target_counts', 'article_categories', 'category_articles', 'category_in_links', 'in_links']
    for name in names:
        print("Shelving:", name)
        values_as_lists = not ('counts' in name)
        reader = csv.reader(codecs.open(name + '.csv', encoding='ascii'))
        shelve_csv_dictionary(reader, name + ".shelve", values_as_lists=values_as_lists)

def invert_csv_dict(reader, writer):
    inv = dict()
    for row in reader:
        source = int(row[0])
        targets = map(int, row[1:])
        for target in targets:
            inv.setdefault(target, []).append(source)
        keys = inv.keys()
        keys.sort()
        for key in keys:
            values = inv[key]
            values.sort()
            row = [key]
            row.extend(values)
        writer.writerow(row)

def invert_csv_dicts():
    ## Invert dictionaries
    reader = csv.reader(codecs.open('article_categories.csv', encoding='ascii'))
    writer = csv.writer(codecs.open('category_articles.csv', mode='w', encoding='ascii'))
    invert_csv_dict(reader, writer)
    reader = csv.reader(codecs.open('category_out_links.csv', encoding='ascii'))
    writer = csv.writer(codecs.open('category_in_links.csv', mode='w', encoding='ascii'))
    invert_csv_dict(reader, writer)
    reader = csv.reader(codecs.open('out_links.csv', encoding='ascii'))
    writer = csv.writer(codecs.open('in_links.csv', mode='w', encoding='ascii'))
    invert_csv_dict(reader, writer)

def compute_target_counts():
    reader = csv.reader(codecs.open('out_links.csv', encoding='ascii'))
    writer = csv.writer(codecs.open('out_counts.csv', mode='w', encoding='ascii'))
    for row in reader:
        source = int(row[0])
        target_count = len(row) - 1
        writer.writerow([source, target_count])

def compute_category_target_counts():
    reader = csv.reader(codecs.open('category_out_links.csv', encoding='ascii'))
    writer = csv.writer(codecs.open('category_target_counts.csv', mode='w', encoding='ascii'))
    for row in reader:
        source = int(row[0])
        target_count = len(row) - 1
        writer.writerow([source, target_count])

def main():
    process_xml()
    # Shelve csv dictionaries.
    reader = csv.reader(codecs.open('id_title.csv', encoding='utf-8'))
    shelve_csv_dictionary(reader, 'id_title.shelve', values_as_lists=False)
    reader = csv.reader(codecs.open('id_categories.csv', encoding='utf-8'))
    shelve_csv_dictionary(reader, 'id_categories.shelve', values_as_lists=False)

    invert_csv_dicts()
    compute_target_counts()
    compute_category_target_counts()
    create_shelves()

    #compute_pagerank()
    #all_categories_pageranks()
    pass

if __name__ == "__main__":
    main()
