#!/usr/bin/env python3
""" This tests that XHTML files match a DTD (typically keyml.dtd). 

Optionally, relative image links can be checked to see if they are broken.

Example: python3 test_xhtml.py -i -d keyml.dtd bigbook/Text/[0-9]*.xhtml
"""

from sys import stderr, exit
from typing import List, Any
from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter
from urllib.request import url2pathname

from PIL import Image
from lxml.etree import XMLParser, DTD, DocumentInvalid, DTDParseError, XMLSyntaxError, parse
from lxml.etree import _Element  # this is okay to do, it is just used for the type interface


__all__ = ['run']


XMLNS = {'xhtml': 'http://www.w3.org/1999/xhtml'}


def main():
    # note: it's okay to use Path as an argument type
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    # noinspection PyTypeChecker
    parser.add_argument('-d', '--dtd', metavar='DTD', type=Path, help='DTD file to test against', required=True)
    parser.add_argument('-i', '--images', action='store_true', help='also test images')
    parser.add_argument('-v', '--verbose', action='store_true', help='also test images')
    # noinspection PyTypeChecker
    parser.add_argument('files', type=Path, metavar='XHTML', nargs='*', help='XHTML files to test')
    args = parser.parse_args()

    success = run(args.files, args.dtd, args.verbose, args.images)
    if not success:
        if args.verbose:
            print(f"FAILURE")
        exit(1) 
    elif args.verbose:
        print(f"SUCCESS")
        


def run(xhtml_files: List[Path], dtd_file: Path, verbose: bool, images: bool) -> bool:
    success = False
    try:
        dtd = DTD(file=str(dtd_file))
    except DTDParseError as e:
        print(str(e.error_log), file=stderr)
    else:
        success = True
        for file in xhtml_files:
            if not test(file, dtd, images, verbose):
                success = False        
    return success


def test(xhtml_file: Path, dtd: DTD, images: bool, verbose: bool) -> bool:
    if verbose:
        print(xhtml_file)
    success = False
    try:
        with open(xhtml_file, mode='rb') as f:
            text = f.read()
        #document = XML(xhtml_file, XMLParser(resolve_entities=False))
        document = parse(source=str(xhtml_file), parser=XMLParser(resolve_entities=False)).getroot()
        dtd.assertValid(document)
    except IOError as e:
        print(f"{xhtml_file}: {e.strerror}", file=stderr)
    except XMLSyntaxError as e:
        print(str(e.error_log), file=stderr)
    except DocumentInvalid as e:
        print(str(e.error_log), file=stderr)
    else:
        if images:
            success = test_images(xhtml_file, document, verbose)
        else:
            success = True
    return success


def test_images(xhtml_file: Path, xhtml: _Element, verbose: bool) -> bool:
    success = True
    imgs: Any = xhtml.xpath('//xhtml:img', namespaces=XMLNS)
    for img in imgs:
        img: _Element
        src = str(img.attrib['src'])
        if not src.startswith('http'):
            img_path = xhtml_file.parent / Path(url2pathname(src))
            if verbose:
                print(img_path)
            try:
                im = Image.open(img_path)
                im.verify()
            except IOError:
                print(f"{xhtml_file}: broken image {img_path}", file=stderr)
                success = False
    return success


if __name__ == '__main__':
    main()
