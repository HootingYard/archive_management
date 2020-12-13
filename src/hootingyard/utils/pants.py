#!/usr/bin/env python3
""" This does its best to provide XHTML files with “smart quotes” and other tyographical finaries."""

from typing import List
from pathlib import Path
from argparse import ArgumentParser
import re

from smartypants import smartypants, convert_entities


__all__ = []


class Settings:
    verbose: bool
    update: bool
    force: bool
    dump: bool
    files: List[Path]


settings = Settings()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--dump', action='store_true', help='write the output to stdout')
    parser.add_argument('-u', '--update', action='store_true', help='overwrite the files with their processed versions')
    parser.add_argument('-f', '--force', action='store_true', help='overwrite the files without question!')
    parser.add_argument('-v', '--verbose', action='store_true', help='print file names as they are processed')
    parser.add_argument('files', type=Path, metavar='XHTML', nargs='+', help='XHTML files to process')
    args = parser.parse_args(namespace=settings)

    run(args.files, args.dump, args.update)


def run(files: List[Path], dump: bool, update: bool) -> None:
    for file in files:
        if settings.verbose: print(file)
        text = file.read_text()
        if re.search(r'[“–”‘—’]', text) and not settings.force:
            print(f"There are already smart quotes in {file}")
        else:
            text = process(text)
            if dump:
                print(text)
            if update:
                file.write_text(text)



def process(text: str) -> str:
    return text_surgery(convert_entities(smartypants(text), 0))


def text_surgery(s: str) -> str:
    """ Replace punctuation that looks bad in print form. """
    s = s.replace(' - ', '—')       # Replace dashes that look horrible in print
    s = s.replace(' – ', '—')
    s = s.replace(' :', FrankColon)  # If it's worth doing, it's worth doing right :-|
    s = NonApostrophe.sub(r"'\1", s) # Replace single-quotes inside words with true apostrophes
    s = DateDash.sub(r"\1–\2", s)   # en dashes inside date ranges
    return s


FrankColon = chr(0xA0) + ':' # non-breaking space, colon
NonApostrophe = re.compile(r'’([A-Za-z])')
DateDash = re.compile(r'([0-9])-([0-9])')


if __name__ == '__main__':
    main()
