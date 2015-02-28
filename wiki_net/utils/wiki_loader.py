#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib2
import os
from os.path import join
import cPickle
import sys
reload(sys)

import numpy as np
import wikipedia

sys.setdefaultencoding('utf-8')
np.random.seed(0)


def get_result(url):
    try:
        connection = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        return ''
    else:
        return connection.read().rstrip()


def category2members(cmpageid, cmtitle, cmtype, cmcont):
    cmcontinue = '&cmcontinue=%s' % cmcont if cmcont else u''
    page = u'cmpageid=%s' % cmpageid if cmpageid else u'cmtitle=%s' % cmtitle
    query = u'http://en.wikipedia.org/w/api.php?action=query&' \
            'list=categorymembers&%s&cmtype=%s&' \
            'cmdir=desc&format=json%s' % (page, cmtype, cmcontinue)
    res = get_result(query)
    jres = json.loads(res)
    return jres


def members_from_cat(cmpageid, cmtitle, cmtype, save_path):
    id2mem = {}
    cmcont = ''
    while cmcont is not None:
        jres = category2members(cmpageid, cmtitle, cmtype, cmcont)
        for page in jres['query']['categorymembers']:
            id2mem[page['pageid']] = page['title'].encode('utf-8')
        if 'query-continue' in jres:
            cmcont = jres['query-continue']['categorymembers']['cmcontinue']
        else:
            cmcont = None
    if save_path:
        f = open(join(save_path, '%d.txt' % cmpageid), 'w')
        f.write(cmtitle)
        f.write('\n')
        f.write('\n'.join(['%d\t%s' % (pageid, title) for pageid, title in id2mem.iteritems()]))
        f.close()
    return id2mem


def pages_from_cat(cat, mxl_items=50, depth=3, save_path=None):
    id2subcat = {}
    level_cats = [(0, 'Category:%s' % cat)]
    for level in xrange(depth):
        np.random.shuffle(level_cats)
        for cmpageid, cmtitle in level_cats[:mxl_items]:
            print('Level: %d - category: %12d %s' % (level, cmpageid, cmtitle.encode('utf-8')))
            id2mem = members_from_cat(cmpageid, cmtitle.replace(' ', '_'), 'subcat', False)
            id2subcat.update(id2mem)
            level_cats.extend(id2mem.items())
    id2pages = {}
    for cmpageid, cmtitle in id2subcat.iteritems():
        cmtitle = cmtitle.decode('utf-8').replace(u'0xe2', '-')
        print('Retrieving pages in category: %s' % cmtitle.encode('utf-8'))
        cmtitle = cmtitle.replace(' ', '_')
        id2pages.update(members_from_cat(cmpageid, cmtitle, 'page', save_path))
    return id2pages


def pages_from_ids(id2pages, dump_path=None):
    pages = []
    n = len(id2pages)
    for i, (pageid, title) in enumerate(id2pages.iteritems()):
        if i % 100 == 0:
            print('Page: %d/%d - %s' % (i, n, title))
        try:
            pages.append(wikipedia.page(title))
        except (wikipedia.PageError, wikipedia.DisambiguationError) as e:
            print 'Disambiguation or page problem: %d - %s' % (pageid, title)
    if dump_path:
        for page in pages:
            path = join(dump_path, '%s.pkl' % page.pageid)
            cPickle.dump(page, open(path, 'w'))
    return pages


def unpickle_pages(path):
    pages = []
    for fname in os.listdir(path):
        if not fname.endswith('.pkl'):
            continue
        f = open(join(path, fname))
        page = cPickle.load(f)
        f.close()
        pages.append(page)
    return pages
