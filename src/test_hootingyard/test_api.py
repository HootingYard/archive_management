import datetime
import functools
from typing import List

from hootingyard.api.stories import (
    get_story_information,
    get_show_information,
    get_all_show_information,
    get_story_to_show_index,
    Narration,
    get_narrations_for_story,
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
    assert index["2006-12-13-paupers-drool"] == {
        "hooting_yard_2007-12-06",
        "hooting_yard_2006-12-13",
    }


def test_find_when_a_story_is_narrated():
    expected = [
        Narration(
            show_id="hooting_yard_2014-05-29",
            time_code=215,
            story_id="2004-05-17-life-and-loves-of-the-immersion-man",
        ),
        Narration(
            show_id="hooting_yard_2005-11-02",
            time_code=255,
            story_id="2004-05-17-life-and-loves-of-the-immersion-man",
        ),
        Narration(
            show_id="hooting_yard_2005-05-11",
            time_code=237,
            story_id="2004-05-17-life-and-loves-of-the-immersion-man",
        ),
    ]
    narrations: List[Narration] = list(
        get_narrations_for_story(
            story_id="2004-05-17-life-and-loves-of-the-immersion-man"
        )
    )
    assert set(narrations) == set(expected)


def test_that_you_can_get_story_objects_from_narrations():
    narrations = get_narrations_for_story(
        story_id="2004-05-17-life-and-loves-of-the-immersion-man"
    )
    first_narration = next(narrations)
    assert "with the hammers" in first_narration.get_story().text


def test_that_you_can_get_show_objects_from_narratives():
    narrations = get_narrations_for_story(
        story_id="2004-05-17-life-and-loves-of-the-immersion-man"
    )
    first_narration = next(narrations)
    assert first_narration.get_show().tx_date() == datetime.date(2014, 5, 29)
