import collections
import datetime
import logging
import re
from collections import defaultdict
from typing import DefaultDict, List, TypeVar, Iterator, Mapping

import yaml

from hootingyard.analysis.ngram import ngrams, trigrams
from hootingyard.config.files import transcript_to_script_matches, get_transcript_to_script_match_file
from hootingyard.index.ngram_to_script_index import ngram_to_script_index
from hootingyard.transcript.transcript import get_transcripts

log = logging.getLogger(__name__)

def extract_date_from_string(s:str)->datetime.date:
    for m in re.findall("([0-9]{4})-([0-9]{2})-([0-9]{2})", s):
        return datetime.date(*[int(x) for x in m])

T = TypeVar("T")

def count_and_dictify(found_matches:Iterator[T])->Mapping[T,int]:
    return dict(collections.Counter(found_matches).most_common(5))


def main():
    log.info("Loading index")
    ngram_lookup_function = ngram_to_script_index()
    log.info("Beginning matching process.")
    for t in get_transcripts():
        result = {
            "id":t.get_id(),
            "matches":[]
        }
        log.info(f"Matching: {t}")
        transcript_date = extract_date_from_string(t.get_id())
        for p in t.paragraphs():
            found_matches = []
            for ngram in trigrams(p.word_iterator()):
                hashable_ngram = tuple(ngram)
                matches = ngram_lookup_function(hashable_ngram)
                for found_script_id in matches:
                    script_date = extract_date_from_string(found_script_id)
                    if script_date < transcript_date:
                        found_matches.append(found_script_id)

            if found_matches:
                result["matches"].append({"time_code":p.time_code.seconds, "votes":count_and_dictify(found_matches)})

        output_file_path = get_transcript_to_script_match_file(t.get_id())
        log.warning("Opening output file.")
        with open(output_file_path, "w") as transcript_to_script_matches_file:
            yaml.dump(dict(result), transcript_to_script_matches_file)
        log.info("Done.")


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
