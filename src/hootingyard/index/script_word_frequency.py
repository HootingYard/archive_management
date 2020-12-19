import csv
import logging
import os
from collections import Counter
from typing import Callable
from typing import Iterator, Mapping

import yaml

from hootingyard.config.directories import get_statistics_directory
from hootingyard.config.files import script_word_frequency_yaml_file_path
from hootingyard.index.story_info import get_story_infos


def words_iterator() -> Iterator[str]:
    for story_info in get_story_infos():
        yield from story_info.story.word_iterator()


def main():
    statistics_dirctory = get_statistics_directory()
    word_counter = Counter(w.lower() for w in words_iterator())
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
