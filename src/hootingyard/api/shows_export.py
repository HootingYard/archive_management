import datetime
import logging
from dataclasses import dataclass, asdict
from typing import List, Optional

import yaml

from hootingyard.api.stories import get_all_show_information
from hootingyard.config.files import get_export_file_path
from hootingyard.index.refine_index import RefinedShow, StoryInShow

log = logging.getLogger(__name__)

@dataclass
class Narration:
    title: str
    story_id: str
    word_count: int
    start_time: int
    end_time: Optional[int]

    @classmethod
    def from_story_in_show(cls, sis:StoryInShow, show_duration:int)->"Narration":
        story_info = sis.get_story_info()

        return cls(
            title= story_info.story.title,
            story_id= story_info.story.id,
            word_count= story_info.word_count,
            start_time=sis.time_code,
            end_time=sis.next_story.time_code if sis.next_story else show_duration
        )

@dataclass
class Show(object):
    title: str
    date: datetime.date
    id: str
    internet_archive_url: str
    duration: int
    narrations: List[Narration]

    @classmethod
    def from_refined_show_info(cls, sh: RefinedShow):
        return cls(
            title=sh.title(),
            date=sh.tx_date(),
            id=sh.id,
            internet_archive_url=sh.get_archive_org_url(),
            duration=sh.get_duration(),
            narrations=[Narration.from_story_in_show(sis, sh.get_duration()) for sis in sh.stories]
        )



@dataclass
class Shows:
    shows:List[Show]


def main():
    shows = Shows(shows=[Show.from_refined_show_info(sh) for sh in get_all_show_information()])


    with open(get_export_file_path(), "w") as shows_export_file:
        yaml.safe_dump(asdict(shows), stream=shows_export_file)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
