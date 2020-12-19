#!/usr/bin/env python3
""" Create a new Table of Contents file (toc.xhtml) for The Big Book of Key. """

from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from lxml.html import parse, fromstring, tostring
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


def run(text_dir: Path, dummy_run: bool = False, verbose: bool = False) -> None:
    toc = text_dir / 'toc.xhtml'
    files = sorted(text_dir.glob('[12]*.xhtml'))
    ordered_list = fromstring('<ol class="contents">\n</ol>\n')
    for file in files:
        if verbose:
            print(file.name)
        html = parse(str(file))
        elements = html.xpath('.//h1')
        if len(elements) == 0:
            elements = html.xpath('.//title')
        link = deepcopy(elements[0])
        link.tag = 'a'
        link.attrib.clear()
        link.attrib['href'] = file.name
        list_element = fromstring('<li></li>\n')
        list_element.insert(0, link)
        ordered_list.append(list_element)
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
