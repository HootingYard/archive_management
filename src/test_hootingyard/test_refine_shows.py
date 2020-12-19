import yaml

from hootingyard.audio.audio_file import AudioFile
from hootingyard.index.refine_index import refine_show, get_refined_index_by_id, StoryInShow
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
    af:AudioFile = rs.get_audio_file()
    assert isinstance(af, AudioFile)

    metadata = af.get_metadata()

    assert af.valid()


def test_get_longest_story():
    rs = get_refined_index_by_id("hooting_yard_2007-05-02")
    longest_story:StoryInfo = rs.get_stories_in_order_of_length()[0]
    assert longest_story.story.id == "2013-12-17-tenth-anniversary-iv"

def test_get_most_significant_story():
    rs = get_refined_index_by_id("hooting_yard_2007-05-02")
    assert rs.get_most_significant_story().story.id=="2006-09-02-rose-garden"

