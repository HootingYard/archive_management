import itertools

from hootingyard.index.story import get_story_by_id


def test_get_story_by_id():
    story = get_story_by_id("2007-02-24-the-central-lever")
    assert story.title == "The Central Lever"

def test_get_word_iterator0():
    story = get_story_by_id("2007-02-25-tiny-enid-takes-a-nap")
    items = list(w.lower() for w in itertools.islice(story.word_iterator(),10))
    assert items == "tiny enid takes a nap tiny enid knew how vitally".split(" ")

def test_get_word_iterator1():
    story = get_story_by_id("2007-02-25-tiny-enid-takes-a-nap")
    items = list(w.lower() for w in itertools.islice(story.word_iterator(),10,20))
    assert items == "important it is to take an afternoon nap because she".split(" ")

