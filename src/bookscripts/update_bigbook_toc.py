#!/usr/bin/env python3
""" Create a new Table of Contents file (toc.xhtml) for The Big Book of Key. """
import re
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from lxml.html import parse, fromstring, tostring, HtmlElement
from copy import deepcopy


class Settings:
    dummy_run: bool
    verbose: bool
    bigbook: Path


settings = Settings()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--dummy-run', action='store_true', help="don't write 'toc.xhtml'")
    parser.add_argument('-v', '--verbose', action='store_true', help='print file names as they are processed')
    parser.add_argument('bigbook', type=Path, help='path to bigbook directory')
    parser.parse_args(namespace=settings)

    text_dir = settings.bigbook / 'Text'
    if not text_dir.is_dir():
        parser.print_usage()
        exit(1)
    else:
        run(text_dir, settings.dummy_run, settings.verbose)


def extract_iso_date(text: str) -> datetime.date:
    match = re.search(r'\d\d\d\d-\d\d-\d\d', text)
    if match:
        return datetime.strptime(match.group(), '%Y-%m-%d')
    else:
        raise ValueError(f'No YYYY-MM-DD date found: {text}')


def get_contents(toc: Path) -> List[HtmlElement]:
        date = extract_iso_date(p.text_content)


def get_title_link(page: Path) -> HtmlElement:
    html = parse(str(page)).getroot()
    elements = html.xpath('.//h1')
    if len(elements) == 0 or elements[0].text_content().strip() == 'Quote of the Day':
        elements = html.xpath('.//title')
    link = deepcopy(elements[0])
    link.tag = 'a'
    link.attrib.clear()
    link.attrib['href'] = page.name
    return link


def merge_in_sorted(item_list: List[HtmlElement], sorted_list: List[HtmlElement]) -> List[HtmlElement]:
    if not item_list:
        return sorted_list
    elif not sorted_list:
        return item_list
    else:
        new_list = []
        if item_list[0].text < sorted_list[0]:
            new_list = [sorted_list[0], item_list[0]]
            del sorted_list[0]
            del item_list[0]
        for item in item_list:
            while sorted_list and sorted_list[0] > :
                new_list.append(sorted_list[0])
                del sorted_list[0]
            new_list.append(item)
        return new_list

def run(text_dir: Path, dummy_run: bool = False, verbose: bool = False) -> None:
    toc = text_dir / 'toc.xhtml'
    if toc.exists():
        html = parse(str(toc)).getroot()
        contents_div = html.xpath('.//div[@contents]')[0]
        old_contents = list(html.xpath('.//div[@contents]/p'))
    else:
        old_contents = []
    new_contents = []
    for file in text_dir.glob('[12][90][0-9][0-9]*.xhtml'):  # files stating with dates
        link = get_title_link(file)
        date = extract_iso_date(file.name)
        item = P(f"{date} — ", link)
        item.tail = '\n'
        new_contents.append(item)
        if verbose:
            print(file.name, "'" + link.text_content() + "'")
    new_contents.sort()
    contents = []

    for item in old_contents:

    list_xhtml = tostring(ordered_list, pretty_print=True, method='xml', encoding='unicode')
    xhtml = Template.format(LIST=list_xhtml, DATE=datetime.now().isoformat())
    if not dummy_run:
        toc.write_text(xhtml)
    if verbose:
        print('Done.')


Template = r'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta name="generator" content="Scrawled in GreasePencil" />
        <title>Contents</title>
        <meta name="author" content="Frank Key" />
        <meta name="description" content="Indiscriminately collected prose works by Frank Key." />
        <meta name="language" content="en-GB" />
        <meta name="generator" content="Scrawled in GreasePencil" />
        <meta name="date" content="{DATE}" />
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <link href="../Styles/style.css" rel="stylesheet" type="text/css" />
    </head>
    <body class="toc">
        <h1>Contents</h1>
        {LIST}
    </body>
</html>'''

if __name__ == '__main__':
    main()
