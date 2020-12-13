import os
import logging
from typing import Iterator

from hootingyard.config.directories import get_big_book_scripts_dirctory
from hootingyard.script.script import (
    Script,
    get_id_from_filename,
    NotAScript,
    get_script_from_file_path,
)

log = logging.getLogger(__name__)


def get_scripts() -> Iterator[Script]:
    root: str = get_big_book_scripts_dirctory()

    for filename in os.listdir(root):
        yield from get_script_from_file_path(filename, root)


if __name__ == "__main__":
    for s in get_scripts():
        print(f"{s} {s.get_id()} {s.get_title()} {s.get_text()}")
