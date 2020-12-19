#!/usr/bin/env python3
""" This tests that XHTML files match a DTD (typically keyml.dtd). 

Optionally, relative links can be checked to see if they are broken,
and relatively linked images can be checked for validity.

Example: python3 test_xhtml.py -i -d keyml.dtd bigbook/Text/[0-9]*.xhtml
"""
from sys import stderr, exit
from pathlib import Path
from argparse import ArgumentParser
from urllib.request import url2pathname
from typing import List

from PIL import Image
from lxml.etree import XMLParser, DTD, DocumentInvalid, DTDParseError, XMLSyntaxError, parse
from lxml.etree import _Element  # this is okay to do, it is just used for the type interface


__all__ = []  # not a module


XMLNS = {'xhtml': 'http://www.w3.org/1999/xhtml'}  # XML namespace table


class Settings:
    dtd: Path
    verbose: bool
    images: bool
    links: bool
    files: List[Path]


settings = Settings()


def main():
    # note: it's okay to use Path as an argument type
    parser = ArgumentParser(description=__doc__)
    # noinspection PyTypeChecker
    parser.add_argument('-d', '--dtd', metavar='DTD', type=Path, help='the DTD file to test against', required=True)
    parser.add_argument('-i', '--images', action='store_true', help='also test image links')
    parser.add_argument('-l', '--links', action='store_true', help='also test relative href links')
    parser.add_argument('-v', '--verbose', action='store_true', help='print file names as they are tested')
    # noinspection PyTypeChecker
    parser.add_argument('files', type=Path, metavar='XHTML', nargs='*', help='XHTML files to test')
    args = parser.parse_args(namespace=settings)

    success = run(args.files, args.dtd, args.images, args.links)
    if not success:
        if args.verbose:
            print(f"FAILURE")
        exit(1) 
    elif args.verbose:
        print(f"SUCCESS")


def run(xhtml_files: List[Path], dtd_file: Path, images: bool, links: bool) -> bool:
    success = False
    try:
        dtd = DTD(file=str(dtd_file))
    except DTDParseError as e:
        print(str(e.error_log), file=stderr)
    else:
        success = True
        for file in xhtml_files:
            if not test(file, dtd, images, links):
                success = False        
    return success


def test(xhtml_file: Path, dtd: DTD, images: bool, links: bool) -> bool:
    if settings.verbose:
        print(xhtml_file)
    success = False
    try:
        document = parse(source=str(xhtml_file), parser=XMLParser(resolve_entities=False)).getroot()
        dtd.assertValid(document)
    except IOError as e:
        print(f"{xhtml_file}: {e.strerror}", file=stderr)
    except XMLSyntaxError as e:
        print(str(e.error_log), file=stderr)
    except DocumentInvalid as e:
        print(str(e.error_log), file=stderr)
    else:
        success = True
        if images:
            success = success and test_images(xhtml_file, document)
        if links:
            success = success and test_links(xhtml_file, document)
    return success


def test_images(xhtml_file: Path, xhtml: _Element) -> bool:
    success = True
    imgs: _Element = xhtml.xpath('//xhtml:img', namespaces=XMLNS)
    for img in imgs:
        img: _Element
        src = str(img.attrib['src'])
        if ':' not in src:
            img_path = xhtml_file.parent / Path(url2pathname(src))
            if settings.verbose:
                print('\t', img_path)
            try:
                im = Image.open(img_path)
                im.verify()
            except IOError:
                print(f"{xhtml_file}: broken image {img_path}", file=stderr)
                success = False
    return success


def test_links(xhtml_file: Path, xhtml: _Element) -> bool:
    success = True
    imgs: _Element = xhtml.xpath('//xhtml:a', namespaces=XMLNS)
    for img in imgs:
        img: _Element
        href = str(img.attrib['href'])
        if ':' not in href:
            path = xhtml_file.parent / Path(url2pathname(href))
            if settings.verbose:
                print('\t', path)
            if not path.exists():
                print(f"{xhtml_file}: broken relative link {path}", file=stderr)
                success = False
    return success


if __name__ == '__main__':
    main()
