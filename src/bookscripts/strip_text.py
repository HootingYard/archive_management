#!/usr/bin/env python3.7
""" Turns "Big Book of Key" XHTML posts into strings of text in JSON files. 

These JSON files can be used by tools that match posts with speech-to-text transcripts.

The JSON format is 
    { "title": "the post's title",
        "date":  "the date of the post in YYYY-MM-DD format",
        "url":   "Hooting Yard Blog permalink URL",
        "file":  "the XHTML file name",
        "text":  "post text in a single line with, optionally with no punctuation" }
"""

import sys
import re
import json
import lxml.html
from pathlib import Path
import lxml.html
from lxml.html import HtmlElement
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import Dict

__all__ = []


def main():
    # noinspection PyTypeChecker
    parser = ArgumentParser(
        description=__doc__, formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument("source", type=Path, help="a directory containing XHTML files")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output directory for JSON files",
        required=True,
    )
    parser.add_argument(
        "-d", "--overwrite", action="store_true", help="overwrite old output files"
    )
    parser.add_argument(
        "-x", "--nopunctuation", action="store_true", help="remove punctuation"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="print processed path names"
    )
    args = parser.parse_args()
    if args.source.exists():
        run(args.source, args.output, args.overwrite, args.nopunctuation, args.verbose)
    else:
        parser.print_help()
        sys.exit(1)


def run(
    xhtml_dir: Path,
    json_dir: Path,
    overwrite_json_files: bool,
    no_punctuation: bool,
    verbose: bool,
) -> None:
    for xhtml_path in xhtml_dir.glob(POST_GLOB):

        json_path = json_dir / (xhtml_path.stem + ".json")
        if not overwrite_json_files and json_path.exists():
            continue

        if verbose:
            print(xhtml_path)

        html: HtmlElement = lxml.html.parse(str(xhtml_path)).getroot()
        data: Dict[str, str] = {}

        date = element_text(html, '//p[@class="postwebpage"]/a')
        if not date:
            continue  # probably not a post

        data["date"] = date[1:-1]
        data["title"] = element_text(html, "//h1").strip()
        data["url"] = html.xpath('//p[@class="postwebpage"]/a')[0].attrib["href"]
        data["file"] = xhtml_path.name
        data["text"] = process_text(html, no_punctuation)

        with open(json_path, mode="w") as file:
            json.dump(data, file)


POST_GLOB = "[0-9][0-9][0-9][0-9][0-9]_*.xhtml"


def element_text(element: HtmlElement, xpath: str) -> str:
    elements = element.xpath(xpath)
    if not elements:
        return ""
    else:
        return elements[0].text_content()


def process_text(html: HtmlElement, no_punctuation: bool) -> str:
    text = element_text(html, "//body").strip()
    text = re.sub(r"\s+", " ", text)
    if no_punctuation:
        text = re.sub(r"[^ \w']", "", text)
    return text


if __name__ == "__main__":
    main()
