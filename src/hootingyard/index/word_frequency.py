import csv
import logging
import os
from collections import Counter
from typing import Callable
from typing import Iterator, Mapping

import yaml

from hootingyard.config.directories import get_statistics_directory
from hootingyard.index.story import get_stories

def get_word_frequency_yaml_path():
    return os.path.join(get_statistics_directory(), "word_frequency.yaml")

def words_iterator()->Iterator[str]:
    for story in get_stories():
        yield from story.word_iterator()

def main():
    statistics_dirctory = get_statistics_directory()
    word_counter = Counter(w.lower() for w in words_iterator())
    os.makedirs(statistics_dirctory, exist_ok=True)
    output_file_path = os.path.join(statistics_dirctory, "word_frequency.csv")
    with open(output_file_path, "w") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=["rank", "count", "word"])
        writer.writeheader()
        for i, (word, count) in enumerate(word_counter.most_common()):
            writer.writerow({"rank":i, "count":count, "word":word})

    with open(get_word_frequency_yaml_path(), "w") as yaml_file:
        yaml.dump({w:c for (w,c) in word_counter.most_common()}, yaml_file)


def word_frequency()->Callable[[str],int]:
    with open(get_word_frequency_yaml_path()) as yaml_file:
        wf:Mapping[str,int] = yaml.load(yaml_file, Loader=yaml.SafeLoader)
    def get_word_frequency(word:str)->int:
        return int(wf[word])

    return get_word_frequency


if __name__ == "__main__":
    logging.basicConfig()
    main()
