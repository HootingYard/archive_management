import heapq
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

def trigrams(inp:Iterator[T])->Iterator[List[T]]:
    return ngrams(3, inp)

def score_ngram(ngram:List[str], scoring_function:Callable[[str],int])->NgramWithScore:
    return NgramWithScore(ngram=ngram, score=sum(scoring_function(w) for w in ngram))

def score_ngrams(ngrams_iterator:Iterator[List[str]], scoring_function:Callable[[str],int])->Iterator[NgramWithScore]:
    for ngram in ngrams_iterator:
        yield score_ngram(ngram=ngram, scoring_function=scoring_function)


def get_ngrams(ngram_length, max_ngrams, wf_scoring_function, filter_function, word_iterator):
    trigrams = [n for n in ngrams(n=ngram_length, inp=word_iterator) if filter_function(n)]
    scored_ngrams = score_ngrams(ngrams_iterator=trigrams, scoring_function=wf_scoring_function)
    best_ngrams = heapq.nsmallest(max_ngrams, scored_ngrams, key=lambda x:x.score)
    return [h.ngram for h in best_ngrams]
