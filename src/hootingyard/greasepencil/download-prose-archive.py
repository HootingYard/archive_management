# download-prose-archive.py -- download a sequence of Wordpress post archive pages

import urllib, sys, os

PAGES  = sys.argv[1] + '/page/%i'          # URLS of Wordpress archive pages
CACHE  = sys.argv[2] + '/prose-%03i.html'  # local file paths to copy those to
RELOAD = True

for page_num in range(1,50000):
    if RELOAD or not os.path.exists(CACHE % page_num):
        urllib.urlretrieve(PAGES % page_num, CACHE % page_num)
    with open(CACHE % page_num) as f:
        print CACHE % page_num
        text = f.read()
        if '<div class="nav-previous"></div>' in text: #link to previous page absent
            break
    #print 'page', page_num
    
print 'done'
