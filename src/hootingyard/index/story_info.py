from dataclasses import dataclass
from typing import List

from hootingyard.index.story import Story


@dataclass
class StoryInfo:
    story: Story
    ngrams: List[List[str]]
    word_count: int
