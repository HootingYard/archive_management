import heapq
from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass
from functools import reduce
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass
class NgramWithScore:
    ngram: list[str]
    score: int


def ngrams(n: int, inp: Iterator[T]) -> Iterator[list[T]]:
    d = deque(maxlen=n)
    found: set[int] = set()
    for i in inp:
        d.append(i)
        if len(d) == n:
            hashed_ngram = hash(tuple(d))
            if hashed_ngram not in found:
                found.add(hashed_ngram)
                yield list(d)


def trigrams(inp: Iterator[T]) -> Iterator[list[T]]:
    return ngrams(3, inp)


def score_ngram(
    ngram: list[str], scoring_function: Callable[[str], int]
) -> NgramWithScore:
    scored_items = [scoring_function(w) for w in ngram]
    score = reduce(lambda x, y: x * y, scored_items)
    return NgramWithScore(ngram=ngram, score=sum(scoring_function(w) for w in ngram))


def score_ngrams(
    ngrams_iterator: Iterator[list[str]], scoring_function: Callable[[str], int]
) -> Iterator[NgramWithScore]:
    for ngram in ngrams_iterator:
        yield score_ngram(ngram=ngram, scoring_function=scoring_function)


def get_ngrams(
    ngram_length, max_ngrams, wf_scoring_function, filter_function, word_iterator
) -> list[str]:
    trigrams = [
        n for n in ngrams(n=ngram_length, inp=word_iterator) if filter_function(n)
    ]
    scored_ngrams = score_ngrams(
        ngrams_iterator=trigrams, scoring_function=wf_scoring_function
    )

    scored_ngrams = list(scored_ngrams)

    best_ngrams = heapq.nlargest(max_ngrams, scored_ngrams, key=lambda x: x.score)
    return [" ".join(h.ngram) for h in best_ngrams]
