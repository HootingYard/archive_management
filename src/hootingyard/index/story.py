import datetime
import re
from collections.abc import Iterator
from dataclasses import dataclass


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

    def _word_iterator(self) -> Iterator[str]:
        yield from re.split(r"[\s]+", self.title)
        yield from re.split(r"[\s]+", self.text)

    def word_iterator(self) -> Iterator[str]:
        for w in self._word_iterator():
            yield from re.findall(r"([a-zA-Z\-']+)", w)

    def lowercase_word_iterator(self) -> Iterator[str]:
        return (w.lower() for w in self.word_iterator())

    def get_word_count(self) -> int:
        return sum(1 for _ in self.word_iterator())
