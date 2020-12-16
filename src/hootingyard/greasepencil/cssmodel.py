""" cssmodel.py -- display how elements are nested within XML documents
                   by showing all possible Xpath selectors"""

import sys
from lxml import html
from lxml.html import HtmlElement
from typing import Dict, List

hide_style = False

Tree = Dict[str, 'Tree']


def walk(root, tags):  # type: (HtmlElement, Tree) -> None
    for child in root.iterchildren("*"):
        tag = child.tag
        if child.attrib.has_key('class'):
            tag += "[@class='%s']" % child.attrib['class']
        if child.attrib.has_key('style'):
            tag += "[@style='']" if hide_style else "[@style='%s']" % child.attrib['style']
        if child.attrib.has_key('id'):
            tag += "[@id='']"
        walk(child, tags.setdefault(tag, {}))


def examine(filepath, tags):  # type: (str, Tree) -> None
    doc = html.parse(filepath).getroot()  # type: HtmlElement
    walk(doc, tags)


def examine_all(filepaths):  # type: (List[str]) -> Tree
    tags = {}
    for filepath in filepaths:
        # print filepath
        examine(filepath, tags)
    return tags


def dump(tags, previous=''):  # type: (Tree, str) -> None
    for (tag, sub) in tags.items():
        print previous + tag
        dump(sub, previous + tag + ' / ')


dump(examine_all(sys.argv[1:]))
