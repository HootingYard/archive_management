""" A library of various text and XHTML functions. """
# -*- coding: utf-8 -*-

import codecs
import json
import os
import re
import time
import uuid
from copy import deepcopy
from typing import AnyStr, Text, Set, TypedDict, List

from lxml import etree
from lxml.html import HtmlElement
import asciify
import ftfy


def fix_bad_unicode(text):  # type: (Text) -> Text
    return ftfy.fix_text(text, uncurl_quotes=False)


# These records are used when processing book data
# There are in dictionary form to allow them to be used directly in Jinja2 templates

PostInfo = TypedDict('PostInfo', {
    'id': str,  # Wordpress id
    'postnum': int,  # Wordpress post number
    'filename': str,  # filename of the BigBook XHTML file for this post
    'href': str,  # URL of the post on hootingyard.org
    'date': str,
    'heading': Text,
    'title': Text,
    'body': Text,  # the XHTML of the post body, set before expanding the post.xhtml template
})

PageInfo = TypedDict('PageInfo', {
    'title': Text,
    'href': str,
    'filename': str,
    'id': str,
    'order': str})

ImageInfo = TypedDict('ImageInfo', {
    'mimetype': str,
    'href': str,
    'id': str,
})

BookInfo = TypedDict('BookInfo', {
    'title': Text,
    'description': Text,
    'author': Text,
    'pronoun': Text,
    'filingorder': Text,  # order for filing, e.g. "Key, Frank"
    'publisher': Text,
    'language': str,
    'isodate': str,
    'year': str,
    'date': str,
    'website': str,
    'email': str,
    'UUID': str,  # ISBN number, or any other unique identifier
    'index': List[PostInfo],  # used when expanding the the toc.xhtml template
    'texfiles': List[str],  # used when preparing LaTeX files
    'pages': List[PageInfo],
    'images': List[ImageInfo],
})


def get_bookinfo(path):  # type: (str) -> BookInfo
    """ Book metadata. Stored as a dictionary, because than works well with Jinja2 """
    b = json.load(codecs.open(path, 'r', 'utf-8'))
    b.setdefault('title', 'Untitled Work')
    b.setdefault('description', 'The writings of Frank Key.')
    b.setdefault('author', 'Frank Key')
    b.setdefault('pronoun', 'he')
    b.setdefault('filingorder', b['author'])  # order for filing, e.g. author's name, surname first
    b.setdefault('publisher', b['author'])
    b.setdefault('language', 'en-GB')
    b.setdefault('isodate', time.strftime("%Y-%m-%dT%H:%M:%S"))
    b.setdefault('year', time.strftime("%Y"))
    b.setdefault('date', time.strftime("%e %B %Y"))
    b.setdefault('website', "http://www.hootingyard.org")
    b.setdefault('email', "hooting.yard@gmail.com")
    b.setdefault('UUID', uuid.uuid4())  # ISBN number, or any other unique identifier
    return b


def identifierize(s):  # type: (AnyStr) -> AnyStr
    """Turn unicode into a nice string for a filename: no accents, no punctuation, underscores for spaces."""
    s = asciify.asciify(s)
    s = s.replace("&", 'n')
    s = s.replace("'", '')
    s = re.sub('[^a-zA-Z0-9]', ' ', s)
    s = s.lower()
    return '_'.join(s.split())


def filenamepart(path):  # type: (AnyStr) -> AnyStr
    """Name part of filename, i.e. namepart('xxx/yyy.eee') == 'yyy'"""
    return os.path.splitext(os.path.basename(path))[0]


def remove_elements_attributes(element):  # type: (HtmlElement) -> None
    for a in element.attrib:
        del element.attrib[a]


def keep_only_these_attributes(element, attributes):  # type: (HtmlElement, Set[str]) -> None
    for a in element.attrib:
        if a not in attributes:
            del element.attrib[a]


def escape(text):  # type: (Text) -> Text
    return text.replace('&', '&amp;').replace('>', '&gt;').replace('<', '&lt;').replace('"', '&quot;')


def text_only(element):  # type: (HtmlElement) -> Text
    """returns just the text in an element, without any tags"""
    s = element.text or u''
    for e in element:
        s += text_only(e) + (e.tail or '')
    return s


NonEmpty = re.compile(r'\S', re.DOTALL)


def isempty(element):  # type: (HtmlElement) -> bool
    """True if the element contains only whitespace text, or no text"""
    if NonEmpty.search(element.text or ''):
        return False
    for e in element:
        if e.tag == 'img':
            return False
        if e.tail is not None and NonEmpty.search(e.tail):
            return False
        if not isempty(e):
            return False
    return True


def iscentred(element):  # type: (HtmlElement) -> bool
    return 'center' in element.attrib.get('style', '') or \
           'center' in element.attrib.get('class', '')


def add(a, b):  # type: (AnyStr, AnyStr) -> AnyStr
    """Concatenate strings that might be represented by None."""
    if a is None:
        return b
    if b is None:
        return a
    return a + b


def insert_all(a, b):  # type: (HtmlElement, HtmlElement) -> None
    """insert all the text and tags inside b into the end of a"""
    if len(a) == 0:
        a.text = add(a.text, b.text)
    else:
        a[-1].tail = add(a[-1].tail, b.text)
    for e in b:
        a.insert(len(a), deepcopy(e))


def remove_elements(element, xpath):  # type: (HtmlElement, str) -> None
    """remove all elements that match an xpath, without removing their tails."""
    for e in element.xpath(xpath):
        parent = e.getparent()
        prev = e.getprevious()
        if prev is not None:
            prev.tail = add(prev.tail, e.tail)
        else:
            parent.text = add(parent.text, e.tail)
        parent.remove(e)


def enclosed_xhtml_markup(element):  # type: (HtmlElement) -> Text
    """Returns all the contents of element in the form of a text string containing HTML tags"""
    s = escape(element.text or u'')
    for e in element:
        s += etree.tounicode(e)
    return s


def fix_unicode(element):  # type: (HtmlElement) -> None
    """Fix 'mojibake' Unicode damage"""
    if element.text:
        element.text = fix_bad_unicode(unicode(element.text))
    if element.tail:
        element.tail = fix_bad_unicode(unicode(element.tail))
    for e in element:
        fix_unicode(e)
