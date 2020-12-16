import dataclasses
import heapq
import logging
import os

import yaml

from hootingyard.analysis.ngram import ngrams, score_ngrams
from hootingyard.config.directories import get_stories_dirctory
from hootingyard.index.story_info import StoryInfo
from hootingyard.index.word_frequency import word_frequency
from hootingyard.script.generators import get_scripts

log = logging.getLogger(__name__)


def main(max_ngrams_per_story=15, ngram_length=3):
    stories_dirctory: str = get_stories_dirctory()
    wf_scoring_function = word_frequency()

    for script in get_scripts():
        story = script.get_story()
        story.validate()
        log.info(f"Writing {story.id}: {story.title}")
        story_filename = f"{story.id}.yaml"
        story_path = os.path.join(stories_dirctory, story_filename)

        ngrams = story.get_ngrams(ngram_length=3, max_ngrams=max_ngrams_per_story, wf_scoring_function=wf_scoring_function)

        story_info = StoryInfo(
            story=story,
            ngrams=ngrams,
            word_count=story.get_word_count()
        )

        with open(story_path, "w") as story_file:
            story_dict = dataclasses.asdict(story_info)
            yaml.dump(story_dict, story_file)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
