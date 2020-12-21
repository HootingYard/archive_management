import datetime
import math

import yaml

from hootingyard.audio.audio_file import AudioFile
from hootingyard.index.refine_index import (
    refine_show,
    get_refined_index_by_id,
    StoryInShow,
)
from hootingyard.index.story_info import StoryInfo
from test_hootingyard.refinement_test_data import get_refinement_test_data


def do_yaml_test(test_number: int):
    assert refine_show(
        **get_refinement_test_data(test_number, "input")
    ) == get_refinement_test_data(test_number, "expected")


def test_refine1():
    do_yaml_test(1)


def test_refine2():
    do_yaml_test(2)


def test_refine3():
    do_yaml_test(3)


def test_refine4():
    do_yaml_test(4)


def test_refine5():
    do_yaml_test(5)


def test_refine6():
    do_yaml_test(6)


def test_get_refined_show():
    rs = get_refined_index_by_id("hooting_yard_2007-03-14")
    for si in rs.stories:
        sinfo = si.get_story_info()
        assert isinstance(sinfo, StoryInfo)
    af: AudioFile = rs.get_audio_file()
    assert isinstance(af, AudioFile)

    metadata = af.get_metadata()

    assert af.valid()


def test_get_longest_story():
    rs = get_refined_index_by_id("hooting_yard_2007-05-02")
    longest_story: StoryInfo = rs.get_stories_in_order_of_length()[0]
    assert longest_story.story.id == "2013-12-17-tenth-anniversary-iv"


def test_get_most_significant_story():
    rs = get_refined_index_by_id("hooting_yard_2007-05-02")
    assert rs.get_most_significant_story().story.id == "2006-09-02-rose-garden"


def test_get_tx_date():
    rs = get_refined_index_by_id("hooting_yard_2007-05-02")
    assert rs.tx_date() == datetime.date(2007, 5, 2)


def test_get_show_title():
    rs = get_refined_index_by_id("hooting_yard_2007-05-02")
    assert rs.title() == "Hooting Yard on the Air: Rose Garden"

def test_get_chapter_start_end0():
    rs = get_refined_index_by_id("hooting_yard_2007-05-02")
    first_story = rs.stories[0]
    assert first_story.time_code == 0
    assert first_story.next_story.time_code == 371

def test_get_chapter_start_end1():
    rs = get_refined_index_by_id("hooting_yard_2007-05-09")
    last_story = rs.stories[-1]
    assert last_story.story == "2006-06-28-the-wind-was-howling-like-a-thousand"
    assert last_story.time_code == 1700
    assert last_story.next_story is None

def test_get_show_length():
    rs = get_refined_index_by_id("hooting_yard_2007-05-09")
    assert rs.get_duration() == 1803
