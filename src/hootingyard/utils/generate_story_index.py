import dataclasses
import logging
import math
import os
from collections import defaultdict
from typing import DefaultDict, List

import yaml

from hootingyard.analysis.ngram import get_ngrams
from hootingyard.config.directories import get_stories_dirctory, get_index_directory
from hootingyard.index.all_stories_iterator import all_stories_iterator
from hootingyard.index.ngram_to_script_index import save_ngram_to_script_index
from hootingyard.index.story_info import StoryInfo
from hootingyard.index.script_word_frequency import script_word_frequency
from hootingyard.index.transcript_word_frequency import transcript_word_frequency

log = logging.getLogger(__name__)


def main(min_ngrams_per_story=5, max_ngrams_per_story=400, ngram_length=3):
    stories_dirctory: str = get_stories_dirctory()
    story_index: DefaultDict[int, List[str]] = defaultdict(list)

    script_word_frequency_function = script_word_frequency()
    transcript_word_frequency_function = transcript_word_frequency()

    def ngram_filter_function(ngram: List[str]) -> bool:
        return all(transcript_word_frequency_function(w) for w in ngram)

    for story in all_stories_iterator():
        log.info(f"Writing {story.id}: {story.title}")
        story_filename = f"{story.id}.yaml"
        story_path = os.path.join(stories_dirctory, story_filename)

        word_count: int = story.get_word_count()
        ngram_count = min(
            max(min_ngrams_per_story, math.floor(word_count / 8)), max_ngrams_per_story
        )

        ngrams: List[str] = get_ngrams(
            ngram_length=ngram_length,
            max_ngrams=ngram_count,
            wf_scoring_function=script_word_frequency_function,
            filter_function=ngram_filter_function,
            word_iterator=story.lowercase_word_iterator(),
        )

        story_info = StoryInfo(
            story=story, ngrams=ngrams, word_count=story.get_word_count()
        )

        with open(story_path, "w") as story_file:
            story_dict = dataclasses.asdict(story_info)
            yaml.dump(story_dict, story_file)

        for ngram in ngrams:
            story_index[ngram].append(story.id)

    save_ngram_to_script_index(dict(story_index))


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
