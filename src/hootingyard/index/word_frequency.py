import logging
from collections import Counter
from typing import Iterator

from hootingyard.index.story import get_stories


def words_iterator()->Iterator[str]:
    for story in get_stories():
        yield from story.word_iterator()

def main():
    word_counter = Counter(w.lower() for w in words_iterator())
    print(word_counter)

if __name__ == "__main__":
    logging.basicConfig()
    main()
