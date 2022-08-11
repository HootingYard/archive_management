import dataclasses
import json
import logging
from pathlib import Path
from typing import Set, Iterator

from hootingyard.config.files import get_training_file_path
from hootingyard.index.story import Story
from hootingyard.index.story_info import get_story_infos, StoryInfo

log = logging.getLogger(__name__)



def format_prompt(prompt:str)->str:
    return f"{prompt}\n"

def format_story_text(text:str)->str:
    return f" {text}\n###"

def make_training_data(training_file_path:Path):

    used_prompts = set()

    training_file_path.parent.mkdir(exist_ok=True)
    with training_file_path.open("w") as training_file:
        for si in get_story_infos():
            if si.word_count > 250:
                log.info(f"Skipping {si.story.title}")
                continue

            story:Story = si.story
            title:str = story.title
            text:str = story.text


            if not story.title in used_prompts:
                item = {
                    "prompt":format_prompt(story.title),
                    "completion":format_story_text(story.text)
                }
                log.info(f"Processing story: {story.title} {si.word_count} words")
                json.dump(item, training_file)
                training_file.write("\n")
                used_prompts.add(story.title)


def main():
    make_training_data(training_file_path=get_training_file_path())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()