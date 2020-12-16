from collections import deque
from dataclasses import dataclass
from typing import TypeVar, Iterator, List, Callable

T = TypeVar("T")

@dataclass
class NgramWithScore:
    ngram: List[str]
    score: int

def ngrams(n:int,inp:Iterator[T])->Iterator[List[T]]:
    d = deque(maxlen=n)
    for i in inp:
        d.append(i)
        if len(d) == n:
            yield list(d)


def score_ngram(ngram:List[str], scoring_function:Callable[[str],int])->NgramWithScore:
    return NgramWithScore(ngram=ngram, score=sum(scoring_function(w) for w in ngram))

def score_ngrams(ngrams_iterator:Iterator[List[str]], scoring_function:Callable[[str],int])->Iterator[NgramWithScore]:
    for ngram in ngrams_iterator:
        yield score_ngram(ngram=ngram, scoring_function=scoring_function)
