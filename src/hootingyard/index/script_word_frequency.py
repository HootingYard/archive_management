import logging
import os
from collections import Counter
from collections.abc import Iterator, Mapping
from typing import Callable

import yaml

from hootingyard.config.directories import get_statistics_directory
from hootingyard.config.files import script_word_frequency_yaml_file_path
from hootingyard.index.all_stories_iterator import all_stories_iterator


def words_iterator() -> Iterator[str]:
    for story in all_stories_iterator():
        yield from story.word_iterator()


def word_filter(w: str):
    return len(w) > 2


def main():
    statistics_dirctory = get_statistics_directory()
    word_counter = Counter(w.lower() for w in words_iterator() if word_filter(w))
    os.makedirs(statistics_dirctory, exist_ok=True)

    with open(script_word_frequency_yaml_file_path(), "w") as yaml_file:
        yaml.dump({w: c for (w, c) in word_counter.most_common()}, yaml_file)


def script_word_frequency() -> Callable[[str], int]:
    with open(script_word_frequency_yaml_file_path()) as yaml_file:
        wf: Mapping[str, int] = yaml.load(yaml_file, Loader=yaml.SafeLoader)

    def get_word_frequency(word: str) -> int:
        return int(wf.get(word, 0))

    return get_word_frequency


if __name__ == "__main__":
    logging.basicConfig()
    main()
