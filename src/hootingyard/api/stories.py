"""
Hooting Yard Indexes API.
"""
import functools
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterator, DefaultDict, Mapping, Set

from hootingyard.index.refine_index import (
    RefinedShow,
    get_refined_index_by_id,
    get_all_refined_shows,
)
from hootingyard.index.story import Story
from hootingyard.index.story_info import StoryInfo, get_story_info_by_id


from typing import Set, Mapping, Optional


@dataclass(eq=True, frozen=True)
class Narration:
    show_id: str
    time_code: int
    story_id: str

    def get_show(self) -> RefinedShow:
        return get_show_information(self.show_id)

    def get_story(self) -> Story:
        return get_story_info_by_id(story_id=self.story_id).story


def get_narrations_for_story(story_id: str) -> Iterator[Narration]:
    """
    Given a story ID return an iterator of all the narrations of that story.
    """
    index = get_story_to_show_index()

    for show_id in sorted(index.get(story_id, [])):
        show_information = get_show_information(show_id=show_id)
        for story_in_show in show_information.stories:
            if story_in_show.story == story_id:
                yield Narration(
                    show_id=show_information.id,
                    time_code=story_in_show.time_code,
                    story_id=story_in_show.get_story_info().story.id,
                )


def get_story_information(story_id: str) -> StoryInfo:
    """
    Gets information about a single story.

    >>> story_info = get_story_information("2004-01-01-by-aerostat-to-hooting-yard")
    >>> story_info.story.title
    'By Aerostat to Hooting Yard'
    >>> story_info.story.date
    datetime.date(2004, 1, 1)
    """
    return get_story_info_by_id(story_id)


def get_show_information(show_id) -> RefinedShow:
    """
    Gets information about a single show.

    >>> show = get_show_information("hooting_yard_2007-01-31")
    >>> show.id
    'hooting_yard_2007-01-31'
    >>> show.tx_date()
    datetime.date(2007, 1, 31)
    >>> [s.get_story_info().story.title for s in show.stories]
    ['The New Goat', 'It Was Dusk', 'Tenth Anniversary (III)', 'Babbling About Doris']
    >>> [s.get_story_info().story.id for s in show.stories]
    ['2005-07-08-the-new-goat', '2005-07-28-it-was-dusk', '2013-12-16-tenth-anniversary-iii', '2017-11-30-babbling-about-doris']
    """
    return get_refined_index_by_id(show_id)


def get_all_show_information() -> Iterator[RefinedShow]:
    """
    Returns an iterator, that gives all of the show information objects.
    """
    yield from get_all_refined_shows()


@functools.lru_cache()
def get_story_to_show_index() -> Mapping[str, Set[str]]:
    """
    Return a dict which maps story IDs to a set of show IDs. This function
    can be used to tell you which shows a story appeared in.
    """
    cache: DefaultDict[str, Set[str]] = defaultdict(set)
    for show in get_all_refined_shows():
        for story in show.stories:
            cache[story.story].add(show.id)

    return dict(cache)
