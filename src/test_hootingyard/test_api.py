import functools

from hootingyard.api.stories import (
    get_story_information,
    get_show_information,
    get_all_show_information,
    get_story_to_show_index,
)
from hootingyard.index.refine_index import RefinedShow
from hootingyard.index.story_info import StoryInfo


def test_get_story_information0():
    story_info: StoryInfo = get_story_information(
        story_id="2003-12-16-archival-rescue-service"
    )
    assert isinstance(story_info, StoryInfo)


def test_get_show_information():
    show_information = get_show_information(show_id="hooting_yard_2007-02-07")
    assert isinstance(show_information, RefinedShow)


def test_get_all_show_information():
    shows = get_all_show_information()
    assert isinstance(next(shows), RefinedShow)


def test_get_story_to_show_index():
    index = get_story_to_show_index()
    assert index["2007-02-07-chump-and-flapper"] == {"hooting_yard_2007-02-07"}
    assert index["2006-12-13-paupers-drool"] == {'hooting_yard_2007-12-06', 'hooting_yard_2006-12-13'}
