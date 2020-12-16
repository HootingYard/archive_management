# epub-copy-and-index.py -- copies files to epub directory, makes EBUB table of contents files
# -*- coding: utf-8 -*-

import codecs
import re
import urllib
from os.path import join

from lxml import etree
from lxml.html import HtmlElement, parse as html_parse

import grease

DATA = '/home/glyn/hootingyard/books/anthology6'  # sys.argv[1]  # book text and images
CODE = '/home/glyn/hootingyard/code'  # sys.argv[2]  # scripts and template files
# EPUB = sys.argv[3]  # epub output
OUT = '/home/glyn/hootingyard/o'

bookinfo = grease.get_bookinfo(join(DATA, 'bookinfo.json'))

FILE = re.compile(r'0*([0-9]+)_.*\.xhtml')
LINK = re.compile(r'http://hootingyard.org/archives/([0-9]+).*')

toc = etree.parse(codecs.open(join(DATA, 'Text', 'toc.xhtml'), "r", "utf-8"), etree.HTMLParser())

index = {}

for toca in toc.xpath("//a"):
    filename = toca.get('href')
    if filename == 'preface.xhtml':
        continue
    postnum = FILE.match(filename).group(1)
    index[postnum] = (filename, grease.text_only(toca))
    # print index[postnum]

for toca in toc.xpath("//a"):
    print '---', toca.get('href')
    page = etree.parse(codecs.open(join(DATA, 'Text', toca.get('href')), "r", "utf-8"), etree.HTMLParser())
    html = page.xpath('//html[1]')[0]
    for a in html.xpath("//a"):
        href = a.get('href')
        link = LINK.match(href)
        if link:
            postnum = link.group(1)
            if href == 'http://hootingyard.org/archives/8352#comments':
                a.set('class', 'hootingyard')
                a.set('title', 'Nicknames')
                print '*', href
            elif postnum in index:
                filename, title = index[postnum]
                a.set('href', filename)
                a.set('title', str(title))
                a.set('class', 'internal')
                print '>', href
            else:
                a.set('class', 'hootingyard')
                print '*', href
                extpage = html_parse(urllib.urlopen(href)).getroot()  # type: HtmlElement
                exta = extpage.xpath("//h1[@class='entry-title'][1]/a")[0]  # type: HtmlElement
                a.set('title', str(grease.text_only(exta)))
        elif href == 'http://hootingyard.org/archive/oct05.htm#2005-10-11-1':
            a.set('class', 'hootingyard')
            a.set('title', 'The Magic Mountain')
            print '*', href
        elif 'hootingyard.org' in href:
            a.set('class', 'hootingyard')
            print '*', href
        else:
            a.set('class', 'external')
            print ' ', href
    html.text = '\n'
    html[0].text = '\n'
    for e in html.xpath('head/*'):
        e.tail = '\n'
    for e in html.xpath('*'):
        e.tail = '\n'
    s = etree.tounicode(html)
    for m in re.findall(ur'(<strong>(<a.+?</a>)</strong>)', s):
        s = s.replace(m[0], m[1])
    with codecs.open(join(OUT, toca.get('href')), 'w', 'utf-8') as f:
        f.write(
            '<?xml version="1.0" encoding="utf-8" standalone="no"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML '
            '1.1//EN"\n  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n')
        f.write(s)
