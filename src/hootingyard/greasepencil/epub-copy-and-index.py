# epub-copy-and-index.py -- copies files to epub directory, makes EBUB table of contents
# -*- coding: utf-8 -*-

import codecs
import mimetypes
import os
import shutil
import sys
import time
from os.path import join
from typing import Set

from lxml import html
from lxml.html import HtmlElement

import grease
import jinja2
from grease import BookInfo

DATA = sys.argv[1]  # book text and images
CODE = sys.argv[2]  # scripts and template files
EPUB = sys.argv[3]  # epub output
RESIZE_IMAGES = len(sys.argv) >= 5 and sys.argv[4] == 'RESIZE'


def copy_image(src, dst):  # type: (str, str) -> None
    if RESIZE_IMAGES:
        raise NotImplementedError()
    else:
        shutil.copyfile(src=src, dst=dst)


bookinfo = grease.get_bookinfo(join(DATA, 'bookinfo.json'))  # type: BookInfo

bookinfo['date'] = time.strftime("%Y-%m-%d")

# Read the book data directory's table of contents,
# i.e. all files linked to by Text/toc.xhtml, in order,
# and copy only the referenced files to the EPUB Text directory.
# For each XHTML file, copy the images it references to the EPUB Images directory.

bookinfo['pages'] = []  # gather information to use when expanding template files
bookinfo['images'] = []

imagefiles = set()  # type: Set[str]
pageid = 0
imageid = 0

path = join(DATA, 'Text', 'toc.xhtml')
toc = html.parse(path)

for n, a in enumerate(toc.xpath("//a")):
    filename = a.get('href')
    print filename
    shutil.copyfile(join(DATA, 'Text', filename),
                    join(EPUB, 'OEBPS', 'Text', filename))

    bookinfo['pages'].append({'title': grease.text_only(a),
                              'href': 'Text/' + filename,
                              'filename': filename,
                              'id': 'page%03i' % pageid,
                              'order': str(n)})
    pageid += 1

    page = html.parse(join(DATA, 'Text', filename))  # type: HtmlElement

    for img in page.xpath("//img"):
        imgfilename = os.path.basename(img.get('src'))
        print '    ', imgfilename

        if imgfilename not in imagefiles:
            copy_image(src=join(DATA, 'Images', imgfilename),
                       dst=join(EPUB, 'OEBPS', 'Images', imgfilename))

            bookinfo['images'].append({'mimetype': mimetypes.guess_type(imgfilename)[0],
                                       'href': 'Images/' + imgfilename,
                                       'id': 'image%03i' % imageid})
            imagefiles.add(imgfilename)
        imageid += 1

# Write EPUB OEBPS contents files and boilerplate frontmatter.

loader = jinja2.FileSystemLoader(join(CODE, 'templates', 'epub'))
env = jinja2.Environment(loader=loader, autoescape=True)


def expand(pagename, subdir=''):
    # Use the book data's version of the page, if it has one, otherwise expand a template.
    # (For example, there might be a copyright page with additional info about story publication dates.)
    pagepath = join(DATA, 'Text', pagename)
    if os.path.exists(pagepath):
        shutil.copyfile(pagepath, join(EPUB, 'OEBPS', subdir, pagename))
    else:
        template = env.get_template(pagename)
        with codecs.open(join(EPUB, 'OEBPS', subdir, pagename), "w", "utf-8") as f:
            f.write(template.render(bookinfo))


expand('toc.ncx')
expand('content.opf')
expand('copyright.xhtml', 'Text')
expand('title.xhtml', 'Text')
expand('toc.xhtml', 'Text')

# end
