from collections import deque
from typing import TypeVar, Iterator, List

T = TypeVar("T")

def ngrams(n:int,inp:Iterator[T])->Iterator[List[T]]:
    d = deque(maxlen=n)
    for i in inp:
        d.append(i)
        if len(d) == n:
            yield list(d)
