import heapq
import os
import re
from dataclasses import dataclass
import datetime
from typing import Iterator

import yaml

from hootingyard.config.directories import get_stories_dirctory


class InvalidStory(RuntimeError):
    pass



@dataclass
class Story:
    id: str
    title: str
    date: datetime.date
    text: str

    def validate(self):
        try:
            assert isinstance(self.id, str)
            assert len(self.id) > 0
            assert isinstance(self.title, str)
            assert len(self.title) > 0
            assert self.date > datetime.date(1995, 1, 1)
        except AssertionError:
            raise InvalidStory

    def _word_iterator(self)->Iterator[str]:
        yield from re.split("[\s]+", self.title)
        yield from re.split("[\s]+", self.text)

    def word_iterator(self)->Iterator[str]:
        for w in self._word_iterator():
            yield from re.findall("([a-zA-Z\-\']+)", w)

    def lowercase_word_iterator(self)->Iterator[str]:
        return (w.lower() for w in self.word_iterator())



    def get_word_count(self)->int:
        return sum(1 for _ in self.word_iterator())








if __name__ == "__main__":
    for s in get_stories():
        print(s)
