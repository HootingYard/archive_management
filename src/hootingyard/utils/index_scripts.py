import dataclasses
import logging
import os

import yaml

from hootingyard.config.directories import get_stories_dirctory
from hootingyard.script.generators import get_scripts

log = logging.getLogger(__name__)


def main():
    stories_dirctory: str = get_stories_dirctory()
    for script in get_scripts():
        story = script.get_story()
        story.validate()
        log.info(f"Writing {story.id}: {story.title}")
        story_filename = f"{story.id}.yaml"
        story_path = os.path.join(stories_dirctory, story_filename)
        with open(story_path, "w") as story_file:
            story_dict = dataclasses.asdict(story)
            yaml.dump(story_dict, story_file)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
