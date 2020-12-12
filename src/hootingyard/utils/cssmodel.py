""" Displays how elements are nested within XML documents.
The output is a series of Xpath selectors that can to select every path thought the document.
ID, style and class attributes are included because they add meaning to the structure
of the document. (The contents of style attributes are ignored but default.)
"""

from lxml.html import parse, HtmlElement
from typing import Dict, List
from argparse import ArgumentParser
from pathlib import Path

__all__ = []


class Settings:
    verbose: bool
    styles: bool
    files: List[Path]


settings = Settings()


def main():
    global settings
    def path(s: str): return Path(s)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-s', '--styles', action='store_true', help="don't ignore the content of style tags")
    parser.add_argument('-v', '--verbose', action='store_true', help='print file names as they are tested')
    parser.add_argument('files', type=path, metavar='HTML', nargs='+', help='HTML files to test')
    settings = parser.parse_args(namespace=Settings)
    run(settings.files)


def run(html: List[Path]) -> None:
    dump(examine_all(html))


Tree = Dict[str, 'Tree']


def dump(all_tags: Tree):
    lines: List[str] = []
    def walk(tree: Tree, previous: str) -> None:
        for (tag, sub) in tree.items():
            lines.append(previous + tag)
            walk(sub, previous + tag + ' / ')
    walk(all_tags, '')
    lines.sort()
    for line in lines:
        print(line)


def examine_all (file: List[Path]) -> Tree:
    tags = {}
    for filepath in file:
        if settings.verbose: 
            print(filepath)
        examine (filepath, tags)
    return tags


def examine (file: Path, tags: Tree) -> None:
    root: HtmlElement = parse(str(file)).getroot()
    walk_element(root, tags)


def walk_element (element: HtmlElement, tags: Tree) -> None:
    for child in element.iterchildren("*"):
        tag = child.tag
        if child.attrib.has_key('class'):
            tag += "[@class='%s']" % child.attrib['class']
        if child.attrib.has_key('style'):
            if settings.styles:
                tag += f"[@style='%s']" % child.attrib['style']
            else:
                tag += "[@style]"
        if child.attrib.has_key('id'):
            tag += "[@id]"
        walk_element(child, tags.setdefault(tag, {}))

        
if __name__ == "__main__":
    main()