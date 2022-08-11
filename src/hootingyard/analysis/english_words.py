from collections.abc import MutableSet
from typing import Callable

from hootingyard.config.files import get_corncob_lowercase_path


def english_words() -> Callable[[str], bool]:

    with open(get_corncob_lowercase_path()) as words_file:
        all_words: MutableSet[str] = {w.strip() for w in words_file}

    def word_filter_function(word: str):
        return word in all_words

    return word_filter_function
