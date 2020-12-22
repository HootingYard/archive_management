import os
from dataclasses import dataclass
from typing import List, Iterator, Any, Mapping

import yaml

from hootingyard.config.directories import get_stories_dirctory
from hootingyard.index.story import Story


@dataclass
class StoryInfo:
    story: Story
    ngrams: List[List[str]]
    word_count: int

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "StoryInfo":
        return cls(
            story=Story(**d["story"]), ngrams=d["ngrams"], word_count=d["word_count"]
        )

    def get_title_and_text(self)->str:
        return f"{self.story.title.upper()}\n\n{self.story.text}"


def load_story_info_from_path(file_path: str) -> StoryInfo:
    with open(file_path) as story_file:
        return StoryInfo.from_dict(yaml.load(story_file, Loader=yaml.SafeLoader))


def get_story_info_by_id(story_id: str) -> StoryInfo:
    story_filename = f"{story_id}.yaml"
    story_path = os.path.join(get_stories_dirctory(), story_filename)
    return load_story_info_from_path(story_path)


def get_story_infos() -> Iterator[StoryInfo]:
    stories_dirctory: str = get_stories_dirctory()
    for file_name in os.listdir(stories_dirctory):
        file_path = os.path.join(stories_dirctory, file_name)
        yield load_story_info_from_path(file_path)
