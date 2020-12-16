import heapq
import os
import re
from dataclasses import dataclass
import datetime
from typing import Iterator

import yaml

from hootingyard.analysis.ngram import ngrams, score_ngrams
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
            yield from re.findall("([a-zA-Z\-]+)", w)

    def lowercase_word_iterator(self)->Iterator[str]:
        return (w.lower() for w in self.word_iterator())

    def get_ngrams(self, ngram_length, max_ngrams, wf_scoring_function):
        trigrams = ngrams(n=ngram_length, inp=self.lowercase_word_iterator())
        scored_ngrams = score_ngrams(ngrams_iterator=trigrams, scoring_function=wf_scoring_function)
        best_ngrams = heapq.nsmallest(max_ngrams, scored_ngrams, key=lambda x:x.score)
        return [h.ngram for h in best_ngrams]

    def get_word_count(self)->int:
        return sum(1 for _ in self.word_iterator())


def get_story_by_id(story_id:str)->Story:
    story_filename = f"{story_id}.yaml"
    story_path = os.path.join(get_stories_dirctory(), story_filename)
    return load_story_from_path(story_path)


def get_stories() -> Iterator[Story]:
    stories_dirctory:str = get_stories_dirctory()
    for file_name in os.listdir(stories_dirctory):
        file_path = os.path.join(stories_dirctory, file_name)
        yield load_story_from_path(file_path)


def load_story_from_path(file_path:str)->Story:
    with open(file_path) as story_file:
        return Story(**yaml.load(story_file, Loader=yaml.SafeLoader))


if __name__ == "__main__":
    for s in get_stories():
        print(s)
