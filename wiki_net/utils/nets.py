from itertools import product

import networkx as nx


def link_network(pages, fname):
    net = nx.DiGraph()
    for page in pages:
        net.add_node(page.title)
    n = len(pages)**2
    for i, (page1, page2) in enumerate(product(pages, repeat=2)):
        if i % 1000 == 0:
            print('Processed: %d/%d' % (i, n))
        if page1 == page2 or not hasattr(page2, 'links'):
            continue
        if page1.title in page2.links:
            net.add_edge(page1.title, page2.title)
    nx.write_gexf(net, '%s.gexf' % fname)
