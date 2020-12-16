import collections
import re
import logging


import yaml

from hootingyard.config.files import transcript_word_frequency_yaml_file_path
from hootingyard.transcript.transcript import get_transcripts

log = logging.getLogger(__name__)

def _word_iterator():
    for t in get_transcripts():
        try:
            for p in t.paragraphs():
                for island in re.split("[\s]+", p.text):
                    yield from re.findall("([a-zA-Z\-\']+)", island)
        except ValueError:
            log.exception(f"Cannot extract from {t}")
            raise

def word_iterator():
    return (w.lower() for w in _word_iterator())

def main():
    word_counter = collections.Counter(word_iterator())
    with open(transcript_word_frequency_yaml_file_path(), "w") as transcript_file:
        yaml.dumps({w:c for (w,c) in word_counter.most_common()})





if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
