import logging
import pickle
from typing import Callable, Set, Tuple

log = logging.getLogger(__name__)

from hootingyard.config.files import ngram_to_story_index_file

def save_ngram_to_script_index(data: dict):
    with open(ngram_to_story_index_file(), "wb") as index_file:
        pickle.dump(data, index_file)


def ngram_to_script_index()->Callable[[Tuple[str]],Set[str]]:
    with open(ngram_to_story_index_file(), "rb") as index_file:
        index = pickle.load(index_file)
        log.warning(f"Loaded {len(index)} keys.")

    def get_index_items(hashed_ngram:Tuple[str])->Set[str]:
        return set(index.get(hashed_ngram, []))

    return get_index_items
