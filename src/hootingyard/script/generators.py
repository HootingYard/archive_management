import logging
import os
from collections.abc import Iterator

from hootingyard.config.directories import (
    get_big_book_scripts_dirctory,
)
from hootingyard.index.story import Story
from hootingyard.script.script import (
    Script,
    get_script_from_file_path,
)

log = logging.getLogger(__name__)


def get_scripts() -> Iterator[Script]:
    non_scripts = ["title.xhtml", "toc.xhtml"]

    root: str = get_big_book_scripts_dirctory()

    for filename in sorted(os.listdir(root)):
        if filename not in non_scripts:
            yield from get_script_from_file_path(filename, root)
    #
    # external_scripts_root = get_external_scripts_directory()


def get_stories_from_scripts() -> Iterator[Story]:
    for script in get_scripts():
        story = script.get_story()
        story.validate()
        yield story


if __name__ == "__main__":
    for s in get_scripts():
        print(f"{s} {s.get_id()} {s.get_title()}")
