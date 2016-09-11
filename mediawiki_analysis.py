
import os
import re
import sqlite3

import mediawiki
import mediawiki.parsing
import mediawiki.models
from mediawiki.helpers import *

import mediawiki.decorators


## Globals:

database_filename = '/home/marc/code/wikipedia/wiki.sqlite'


if __name__ == "__main__":
    
    def detect_category_cycles():
        database_filename = '/home/marc/code/wikipedia/derived/en_wikipedia.sqlite'
        mwdb = mediawiki.models.MediaWikiDatabase(database_filename)
        all_categories = mwdb.get_all_category_ids()
        for x, in all_categories:
            #print x
            cycle = False
            loop_list = [x]
            super_categories = [y for (y,) in mwdb.categories.super[x]]
            #print super_categories
            #for y, in super_categories:
                #print y
            depth = 0
            while len(super_categories) and depth < 6:
                depth += 1
                for s in super_categories:
                    #print s
                    if s == x and depth > 1:
                    #if s in loop_list:
                        cycle = True
                        print x, mwdb.categories[x], depth
                        break
                    loop_list.append(s)
                new_super_categories = []
                if cycle:
                    break
                for s in super_categories:
                    sups = mwdb.categories.super[s]
                    for t in sups:
                        new_super_categories.append(t[0])
                super_categories = new_super_categories
                #print super_categories


    detect_category_cycles()
    
    #categories = mwdb.get_categories()
    ##import random
    ##subs = []
    ##sups = []
    #roots = []
    #for id, in categories:
        #count = 0
        #sups = mwdb.supercategories[id]
        #new_id = 0

        #while sups:
            #if new_id == sups[0][0]:
                #break
            #new_id = sups[0][0]
            #print new_id, sups
            #count += 1
            #sups = mwdb.supercategories[new_id]
            #print sups
        #roots.append(count)
        #count = 0
    #print "max", max(roots)
    #print "avg", float(sum(roots)) / float(len(roots))

    #cats = mwdb.categories.get_categories(18831)

    #cats = mwdb.titles.starts_with('Cheese')
    #cats = mwdb.categories.get_categories('11749910')

    #for (x,) in cats:
        #print mwdb.categories[x]

    #print 'avg_sub', float(sum(subs)) / float(len(categories))
    #print 'max_sub', max(subs)
    #print 'avg_sup', float(sum(sups)) / float(len(categories))
    #print 'max_sup', max(sups)
    