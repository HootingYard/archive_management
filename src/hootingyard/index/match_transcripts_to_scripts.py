import collections
import logging
from collections.abc import Iterator, Mapping
from typing import TypeVar

import yaml

from hootingyard.analysis.ngram import trigrams
from hootingyard.config.files import (
    get_transcript_to_script_match_file,
)
from hootingyard.index.ngram_to_script_index import ngram_to_script_index
from hootingyard.transcript.transcript import get_transcripts

log = logging.getLogger(__name__)


T = TypeVar("T")


def count_and_dictify(found_matches: Iterator[T]) -> Mapping[T, int]:
    return dict(collections.Counter(found_matches).most_common(5))


def main():
    log.info("Loading index")
    ngram_lookup_function = ngram_to_script_index()
    log.info("Beginning matching process.")
    for t in get_transcripts():
        match_result = match_single_transcript(ngram_lookup_function, t)
        output_file_path = get_transcript_to_script_match_file(t.get_id())
        log.warning("Opening output file.")
        with open(output_file_path, "w") as transcript_to_script_matches_file:
            yaml.dump(dict(match_result), transcript_to_script_matches_file)
        log.info(f"Finished matching for {t.get_id()}")


def match_single_transcript(ngram_lookup_function, t):
    result = {"id": t.get_id(), "matches": []}
    log.info(f"Matching: {t}")
    for p in t.paragraphs():
        found_matches = []
        for ngram in trigrams(p.word_iterator()):
            hashable_ngram = " ".join(ngram)
            matches = ngram_lookup_function(hashable_ngram)
            for found_script_id in matches:
                found_matches.append(found_script_id)

        if found_matches:
            result["matches"].append(
                {
                    "time_code": p.time_code.seconds,
                    "votes": count_and_dictify(found_matches),
                }
            )
    return result


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
