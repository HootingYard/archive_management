import collections
import re
import logging
from typing import Mapping, Callable

import yaml

from hootingyard.config.files import transcript_word_frequency_yaml_file_path
from hootingyard.transcript.transcript import get_transcripts

log = logging.getLogger(__name__)


def _word_iterator():
    for t in get_transcripts():
        for p in t.paragraphs():
            for island in re.split("[\s]+", p.text):
                yield from re.findall("([a-zA-Z\-']+)", island)


def word_iterator():
    return (w.lower() for w in _word_iterator())


def main():
    word_counter = collections.Counter(word_iterator())
    with open(transcript_word_frequency_yaml_file_path(), "w") as transcript_file:
        yaml.dump({w: c for (w, c) in word_counter.most_common()}, transcript_file)


def transcript_word_frequency() -> Callable[[str], int]:
    with open(transcript_word_frequency_yaml_file_path()) as yaml_file:
        wf: Mapping[str, int] = yaml.load(yaml_file, Loader=yaml.SafeLoader)

    def get_word_frequency(word: str) -> int:
        return int(wf.get(word, 0))

    return get_word_frequency


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
