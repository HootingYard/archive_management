import itertools
from collections.abc import Iterator

from hootingyard.external_scripts.external_scripts import get_external_stories
from hootingyard.index.story import Story
from hootingyard.script.generators import get_stories_from_scripts


def all_stories_iterator() -> Iterator[Story]:
    """
    Get all the story objects from the keyml repo AND the eternal sources.
    :return:
    """
    return itertools.chain(get_stories_from_scripts(), get_external_stories())
