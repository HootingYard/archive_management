import logging
from dataclasses import dataclass
from typing import List

import yaml

from hootingyard.config.files import transcript_to_script_matches

log = logging.getLogger(__name__)

@dataclass
class ShowStory:
    id: str
    time_code: int

@dataclass
class RefinedShow():
    id: str
    contents: List[ShowStory]

def refine(show_id:str):


def main():
    with open(transcript_to_script_matches()) as matches_file:
        matches = yaml.safe_load(matches_file)


    for show, show_content in matches.items():
        print(show, show_content)

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
