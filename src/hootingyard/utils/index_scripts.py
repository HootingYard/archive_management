import dataclasses
import logging
import math
import os
from collections import defaultdict
from typing import DefaultDict, List

import yaml

from hootingyard.analysis.ngram import get_ngrams
from hootingyard.config.directories import get_stories_dirctory, get_index_directory
from hootingyard.index.story_info import StoryInfo
from hootingyard.index.script_word_frequency import word_frequency
from hootingyard.script.generators import get_scripts

log = logging.getLogger(__name__)


def main(max_ngrams_per_story=30, ngram_length=3):
    stories_dirctory: str = get_stories_dirctory()
    story_index:DefaultDict[int,List[str]] = defaultdict(list)
    wf_scoring_function = word_frequency()

    for script in get_scripts():
        story = script.get_story()
        story.validate()
        log.info(f"Writing {story.id}: {story.title}")
        story_filename = f"{story.id}.yaml"
        story_path = os.path.join(stories_dirctory, story_filename)


        word_count:int = story.get_word_count()
        ngram_count = min(max(3,math.floor(word_count/12)),max_ngrams_per_story)

        ngrams = get_ngrams(ngram_length=ngram_length, max_ngrams=ngram_count, wf_scoring_function=wf_scoring_function, word_iterator=story.lowercase_word_iterator())

        story_info = StoryInfo(
            story=story,
            ngrams=ngrams,
            word_count=story.get_word_count()
        )

        with open(story_path, "w") as story_file:
            story_dict = dataclasses.asdict(story_info)
            yaml.dump(story_dict, story_file)

        for ngram in ngrams:
            ngram_hash = hash(tuple(ngram))
            story_index[ngram_hash].append(story.id)

    story_index_path = os.path.join(get_index_directory(), "hashed_ngrams_to_story_id.yaml")
    with open(story_index_path, "w") as index_file:
        yaml.dump(story_index, index_file)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
