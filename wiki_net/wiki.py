from utils import nets, wiki_loader

cat = 'World_War_I'

if 'pages' not in locals():
    # download data from wikipedia
    id2pages = wiki_loader.pages_from_cat(cat, mxl_items=1, depth=1, save_path='tmp')
    pages = wiki_loader.pages_from_ids(id2pages, dump_path='tmp')

# load data locally once obtained from wikipedia
# pages = wiki_loader.unpickle_pages(path='tmp')

# save a network to Gephi format
nets.link_network(pages, cat)

