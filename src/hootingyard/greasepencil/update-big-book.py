# update-big-book -- tidies 'Prose' posts from the Hooting Yard website
# -*- coding: utf-8 -*-

# The idea here is to remove presentational markup and cruft put in by wordprocessors,
# and to add useful information for LaTeX, like em-dashes and print indentation rules.

# This script downloads the images used in blog posts when necessary.
import codecs
import json
import os
import urllib, urlparse, glob, sys, re
from os.path import join
from cStringIO import StringIO

from copy import deepcopy
from typing import Dict, Text

from grease import remove_elements_attributes, iscentred, isempty, insert_all, keep_only_these_attributes, \
    enclosed_xhtml_markup, text_only, identifierize, fix_unicode, PostInfo, BookInfo, remove_elements, get_bookinfo

import jinja2
from lxml.html import clean, fromstring, HtmlElement
from lxml.etree import strip_tags, strip_elements
from PIL import Image

ARCHIVE = sys.argv[1]  # Directory of Wordpress blog archive pages
DATA    = sys.argv[2]  # The Big Book's GreasePencil data directory
CODE    = sys.argv[3]  # The GreasePencil code and template directory

WordpressFiles = sorted(glob.glob(join(ARCHIVE, 'prose-*.html')))

loader = jinja2.FileSystemLoader(join(CODE, 'templates', 'xhtml'))
templates = jinja2.Environment(loader=loader, autoescape=True)


Asterisks = re.compile(r'^\s*(\*\s*)+$', re.DOTALL)  #Text that is nothing but asterisks.


def addclass(element, value):  # type: (HtmlElement, str) -> None
    cls = element.get('class')
    if cls is not None:
        cls += ' ' + value
    else:
        cls = value
    element.set('class', cls)


   
def text_surgery(s):  # type: (Text) -> Text
    ''' Replace punctuation that looks bad in print form. '''
    s = s.replace(u' - ', u'—')       # Replace dashes that look horrible in print
    s = s.replace(u' – ', u'—')
    s = s.replace(u' :', FrankColon)  # If it's worth doing, it's worth doing right :-|
    s = NonApostrophe.sub(ur"'\1", s) # Replace single-quotes inside words with true apostrophes
    s = DateDash.sub(ur"\1–\2", s)   # en dashes inside date ranges
    return s

FrankColon = unichr(0xA0) + u':' # non-breaking space, colon
NonApostrophe = re.compile(ur'’([A-Za-z])')
DateDash = re.compile(ur'([0-9])-([0-9])')


def remove_empty_paragraphs(post):  # type: (HtmlElement) -> None
    for p in post.xpath(".//p"):
        if isempty(p):
            p.getparent().remove(p)


def enclose_illustrations(post):  # type: (HtmlElement) -> None

    # A paragraph containing at least one image is a row of images for an illustration:
    for p in post.xpath(".//p[.//img[1]]"):
        images = fromstring('<p class="imagerow"></p>\n') # type: HtmlElement
        for img in p.xpath(".//img"):
            img = deepcopy(img)
            img.tail = None
            images.insert(len(images), img)

        # The non-image tags in the same paragraph make up the caption:
        caption = deepcopy(p)
        remove_elements_attributes(caption)
        remove_elements(caption, './/a[img]')
        remove_elements(caption, './/img')
        caption.set('class', 'caption')

        # If the image paragraph is followed by a centred paragraph that does not contain an image,
        # then that is also intended as a caption:
        nextp = p.getnext()
        if nextp is not None and not post.xpath(".//img[1]"):
            if nextp.tag == 'p' and iscentred(nextp):
                insert_all(caption, nextp)
                nextp.getparent().remove(nextp)

        # Replace the image paragraph with a division enclosing the above:
        div = fromstring('<div class="illustration"></div>\n') # type: HtmlElement
        div.insert(0, images)
        if not isempty(caption): div.insert(1, caption)
        div.text = '\n'
        div.tail = '\n'
        p.getparent().replace(p, div)


def clean_text (element):  # type: (HtmlElement) -> None

    for e in element.iterdescendants():
        if e.text: e.text = text_surgery(e.text)
        if e.tail: e.tail = text_surgery(e.tail)

    # Remove MS Word freakishness:
    strip_tags(element, 'st1')
    strip_elements(element, 'o')
    for p in element.xpath(".//p"):
        if p.attrib.get('class', '') == 'MsoNormal':
            del p.attrib['class']
    for div in element.xpath(".//div[@id='_mcePaste']"):
        div.getparent().remove(div)

    # Replace tags with their bare, abstract versions:
    for i in element.xpath(".//i"): i.tag = 'em'
    for i in element.xpath(".//b"): i.tag = 'strong'
    for a in element.xpath(".//a"): keep_only_these_attributes (a, {'href'})
    for x in element.xpath(".//li|.//ul|.//del"): remove_elements_attributes(x)


def adjust_styles (post):  # type: (HtmlElement) -> None
    # XXX I'm removing ALL style tags here. The ones used up to Aug 2012
    # have been cruft added by word processors, but that might change.

    for p in post.xpath(".//p"):
        c = iscentred(p)
        if p.get('style'): del p.attrib['style']
        if p.get('align'): del p.attrib['align']
        if c: addclass(p, 'center')

    for span in post.xpath(".//span[@style='text-decoration: line-through;']"):
        remove_elements_attributes(span)
        span.tag = 'del'
       
    for span in post.xpath(".//span[@style='font-size: small;']"):
        remove_elements_attributes(span)
        span.tag = 'small'
       
    strip_tags(post, 'span')   # XXX totally ignore remaining spans


def adjust_text_break_asterisks (post):  # type: (HtmlElement) -> None
    for p in post.xpath(".//p"):
        if len(p) == 0 and Asterisks.match(p.text or ''):
            p.text = ''
            p.set('class', 'textbreak')
            n = p.getnext()
            if n is not None and n.tag == 'p':
                addclass(n, 'noindent')
   

def adjust_indents (post):  # type: (HtmlElement) -> None
    # Text with whitespace above it should not not be given paragraph indents.

    # Paragraphs containing breaks are /usually/ verse, and have whitespace about and below:
    for p in post.xpath(".//p[br]"):
        p.set('class', 'linebreaks')

    # Headings, blockquotes and illustrations all have whitespace under them.
    for element in post.xpath(".//h1|.//h2|.//blockquote|.//div[@class='illustration']|.//p[class='linebreaks']"):
        n = element.getnext()
        if n is not None and n.tag == 'p':
            addclass(n, 'noindent')
       
    # The first paragraph of a blockquote has whitespace above it
    for p in post.xpath(".//blockquote/p[1]"):
        addclass(p, 'noindent')


def clean_image_attributes (img):  # type: (HtmlElement) -> None
    keep_only_these_attributes(img, {'src', 'alt', 'class'})
    # Wordpress images have extra attributes and classes we don't want.
    # See keyml.dtd for the accepted img classes.
    if img.attrib.has_key('class'):
        classes = set(img.attrib.get('class', '').split())
        classes &= {'size-full', 'size-medium', 'size-large', 'small', 'fullwidth'}
        if classes != set():
            img.attrib['class'] = ' '.join(classes)
        else:
            del img.attrib['class']
    # All images must have alt attributes
    if img.attrib.get('alt', '') == '':
        img.attrib['alt'] = '(Illustration.)'

        
def collect_images (post_url, post):  # type: (str, HtmlElement) -> None

    for img in post.xpath(".//img"):

        url = urlparse.urljoin(post_url, urllib.quote(img.get("src").encode('utf-8'))) #XXX
        print 'Image:', url

        # Wordpress stores images in year/month subdirectories, but EPUB does not,
        # so we make the year and date part of the image's filename instead:
        match = re.search(r'wp-content/uploads/(\d\d\d\d)/(\d\d)/(.*)$', url)
        if match:
            filename = '-'.join(match.groups())  #i.e. yyyy-mm-filename.jpg
        else:
            filename = os.path.basename(urlparse.urlsplit(url).path)

        # Download the image.
        # GIFs are resaved as PNGs, because LaTeX cannot deal with those.
        namepart, ext = os.path.splitext(filename)
        if ext.lower() == '.gif':
            filename_png = namepart + '.png'
            save_as_png(filename_png, url)
        else:
            path = join(DATA, 'Images', filename)
            if not os.path.exists(path):
                urllib.urlretrieve(url, path)

        img.attrib['src'] = '../Images/' + filename
        clean_image_attributes(img)

        # On the website images have links, but we don't want that in the ebook:
        parent = img.getparent()
        if parent.tag == 'a':
            parent.getparent().replace(parent, img)


def save_as_png(filename_png, url):  # type: (str, str) -> None
    path = join(DATA, 'Images', filename_png)
    if not os.path.exists(path):
        try:
            data = StringIO(urllib.urlopen(url).read())
            image = Image.open(data)
            image.save(path)
        except IOError:
            print '*** COULD NOT SAVE %r AS %r' % (url, path)


BlogURL = re.compile(r'http://.*hootingyard\.org/archives/([0-9]+)')


def classify_and_redirect_links (post, postindex):  # type: (HtmlElement, Dict[str, PostInfo]) -> None
    ''' Makes links to other prose posts local '''
    # XXX This may result in broken links when extracting an anthology,
    # so the links will need to be re-checked by the script that does that.
    for a in post.xpath(".//a"): # type: HtmlElement
        href = a.get('href') or ''
        m = BlogURL.match(href)
        if m:
            postid = 'post-' + m.group(1)  # type: str
            if postindex.has_key(postid):
                a.set('class', 'internal')
                a.set('title', postindex[postid]['title'])
        elif 'hootingyard.org' in href:
            a.set('class', 'hootingyard')
        else:
            a.set('class', 'external')
                   
           
def xhtml_formatting (post):  # type: (HtmlElement) -> None
    # some spacing make it readable
    for p in post.xpath('//div|//p|//h1|//blockquote'): p.tail = '\n\n'


def get_post_info (entry):  # type: (HtmlElement) -> PostInfo
    link    = entry.xpath(".//*[@class='entry-title']/a")[0]
    postid  = entry.get('id')  # "post-nnnnn"
    postnum = int(postid[postid.index('-')+1:])
    date    = entry.xpath(".//div[@class='entry-meta']//time/@datetime")[0][:10]  # "yyyy-mm-dd"
    clean_text(link)
    heading = enclosed_xhtml_markup(link)   #with HTML mark up
    title   = text_surgery(text_only(link)) #without mark up
    info = { 'id'       : str(postid),
             'postnum'  : postnum,
             'filename' : '%05i_%s.xhtml' % (postnum, identifierize(text_only(link))),
             'href'     : link.get('href'),
             'date'     : date,
             'heading'  : heading,
             'title'    : title }
    #print postnum, title
    return info

def process_post (entry, postinfo, postindex):
    # type: (HtmlElement, PostInfo, Dict[str, PostInfo]) -> HtmlElement
    post = entry.xpath(".//div[@class='entry-content'][1]")[0]
    h1 = fromstring(u'<h1 id="%s">%s</h1>\n\n' % (postinfo['id'], postinfo['heading'])) # type: HtmlElement
    post.insert(0, h1)
    remove_elements(post, '//form')
    remove_elements_attributes(post)
    remove_empty_paragraphs(post)
    enclose_illustrations(post)
    collect_images(postinfo['href'], post)
    clean_text(post)
    adjust_styles(post)
    adjust_text_break_asterisks(post)
    adjust_indents(post)
    xhtml_formatting(post)
    classify_and_redirect_links(post, postindex)
    return post


cleaner = clean.Cleaner( scripts = True,
                         javascript = True,
                         comments = True,
                         processing_instructions = True,
                         embedded = True,
                         frames = True,
                         forms = True,
                         remove_unknown_tags = True )

def parse_dubious_html (path):  # type: (str) -> HtmlElement
    with codecs.open(path, "r", "utf-8") as f: text = f.read()
    text = re.sub(r'(?is)<o.*?>.*?</o>|<object.*?>.*?</object>|<iframe.*?>.*?</iframe>', u'', text)
    cleaner.clean_html(text)
    html = fromstring(text) # type: HtmlElement
    fix_unicode(html)
    return html


post_template = templates.get_template('post.xhtml')


def write_post (path, post, postinfo, bookinfo): # type: (str, HtmlElement, PostInfo, BookInfo) -> None
    postinfo['body'] = enclosed_xhtml_markup(post)
    with codecs.open(path, "w", "utf-8") as f:
        data = dict(post = postinfo, book = bookinfo)
        f.write(post_template.render(data))


def write_toc_page (bookinfo):  # type: (BookInfo) -> None
    path = join(DATA, 'Text', 'toc.xhtml')
    with codecs.open(path, "w", "utf-8") as f:
        data = dict(book = bookinfo)
        f.write(templates.get_template('toc.xhtml').render(data))

def replace_internal_links(post, postinfo):  # type: (HtmlElement, PostInfo) -> None
    for a in post.xpath(".//a[@class='internal']"):
        a.attrib['href'] = postinfo['filename']

def main():
    bookinfo = get_bookinfo(join(CODE, 'templates', 'xhtml', 'bigbookinfo.json'))
    postindex_cache = os.path.join(DATA, 'postindex.json')

    bookinfo['index'] = []
    postindex = {}  # type: Dict[str, PostInfo]   # post id to postinfo

    if os.path.exists(postindex_cache):
        with codecs.open(postindex_cache, "r", "utf-8") as f:
            postindex = json.load(f)
            bookinfo['index'] = postindex.values()
            bookinfo['index'].sort(cmp=(lambda a, b: a['postnum'] - b['postnum']))
    else:
        for path in WordpressFiles:
            print '?', path
            page = parse_dubious_html(path)
            for entry in page.xpath("//article"):
                postinfo = get_post_info(entry)
                postindex[postinfo['id']] = postinfo
                bookinfo['index'].append(postinfo)
        with codecs.open(postindex_cache, "w", "utf-8") as f:
            json.dump(postindex, f, ensure_ascii=False, indent=2, sort_keys=True)

    write_toc_page(bookinfo)

    for path in WordpressFiles:
        print '>', path
        page = parse_dubious_html(path)
        for entry in page.xpath("//article"):
            postinfo = postindex[entry.get('id')]
            path = join(DATA, 'Text', postinfo['filename'])
            if not os.path.exists(path):
                print '*', path
                post = process_post(entry, postinfo, postindex)
                replace_internal_links(post, postinfo)
                write_post(path, post, postinfo, bookinfo)
            else:
                print ' ', path

main()

