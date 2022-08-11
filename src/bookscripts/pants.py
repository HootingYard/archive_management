#!/usr/bin/env python3
""" This does its best to provide XHTML files with “smart quotes” and other typographical finaries.
    It does this by running 'smartypants' on it, and correcting the apostrophes it stuffs up."""

import re
from argparse import ArgumentParser
from pathlib import Path

from smartypants import convert_entities, smartypants


class Settings:
    verbose: bool
    update: bool
    force: bool
    dump: bool
    files: list[Path]


settings = Settings()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "-d", "--dump", action="store_true", help="write the output to stdout"
    )
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="overwrite the files with their processed versions",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite the files without question!",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print file names as they are processed",
    )
    parser.add_argument(
        "files", type=Path, metavar="XHTML", nargs="+", help="XHTML files to process"
    )
    args = parser.parse_args(namespace=settings)

    run(args.files, args.dump, args.update)


def run(files: list[Path], dump: bool, update: bool) -> None:
    for file in files:
        if settings.verbose:
            print(file)
        text = file.read_text()
        if re.search(r"[“”‘’]", text) and not settings.force:
            print(f"There are already smart quotes in {file}")
        else:
            text = process(text)
            if dump:
                print(text)
            if update:
                file.write_text(text)


def process(text: str) -> str:
    s = convert_entities(smartypants(text), 0)
    # Smartypants replaces proper mid-word apostrophes with single quotes:
    s = re.sub(r"\b[‘’]\b", "'", s)  # put them back
    return s


if __name__ == "__main__":
    main()
