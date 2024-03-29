import logging
import math
import os
import time
from dataclasses import dataclass
from typing import List, Optional, Mapping, Any, Iterator, DefaultDict, Set

import yaml

from hootingyard.audio.audio_file import AudioFile, get_audio_file_by_id
from hootingyard.config.directories import get_refined_show_index_directory
from hootingyard.config.files import (
    get_transcript_to_script_match_files,
    get_refined_show_contents_file,
)
from hootingyard.index.story_info import StoryInfo, get_story_info_by_id
from hootingyard.utils.date_utils import extract_date_from_string

log = logging.getLogger(__name__)


def simplify_segment_result(time_code, votes, previous_segment: Optional[str]):
    total_votes = sum(votes.values())
    sorted_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)
    all_choices = set(votes.keys())

    if previous_segment and previous_segment in all_choices:
        # If the previous segment is defined and is one of our choices,
        # then this segment is probably a continuation
        return None
    if sorted_votes[0][1] > (total_votes * 0.5):
        # If choice has a clear majority, then just choose it
        best_vote = sorted_votes[0][0]
    elif sum(v[1] for v in sorted_votes[:2]) > (total_votes * 0.6):
        # If the top 2 votes are more than 60% then take the latest
        # Then pick the latest of the two stories
        best_vote = max(sorted_votes[:2], key=lambda v: extract_date_from_string(v[0]))[
            0
        ]
    else:
        # No clear winner
        return None

    return {"time_code": time_code, "story": best_vote}


def pick_matches(matches):
    previous_segment_result: Optional[str] = None
    for segment in matches:
        segment_result = simplify_segment_result(
            **segment, previous_segment=previous_segment_result
        )
        if segment_result:
            yield segment_result
            previous_segment_result = segment_result["story"]


def refine_show(id: str, matches):
    return {"id": id, "stories": list(pick_matches(matches))}


def main():
    for file_path in get_transcript_to_script_match_files():
        log.info(f"Loading {file_path}.")
        with open(file_path) as matches_file:
            matches = yaml.safe_load(matches_file)
        refined = refine_show(**matches)
        id = matches["id"]
        log.info(f"Refining {id}")
        output_path = get_refined_show_contents_file(id)
        with open(output_path, "w") as output_file:
            yaml.safe_dump(refined, output_file)


@dataclass
class StoryInShow:
    time_code: int
    story: str
    next_story: Optional["StoryInShow"]

    def get_time_code_mmss(self) -> str:
        if self.time_code > 3600:
            return time.strftime("%H:%M:%S", time.gmtime(self.time_code))
        else:
            return time.strftime("%M:%S", time.gmtime(self.time_code))

    def get_story_info(self) -> StoryInfo:
        return get_story_info_by_id(self.story)


@dataclass
class RefinedShow:
    id: str
    stories: List[StoryInShow]

    @classmethod
    def from_dict(cls, id: str, stories: List[Mapping[str, Any]]):
        stories_in_show = []

        next_story: Optional[StoryInShow] = None

        for s in reversed(stories):
            the_story = StoryInShow(next_story=next_story, **s)
            stories_in_show.append(the_story)
            next_story = the_story

        return cls(id=id, stories=list(reversed(stories_in_show)))

    def get_audio_file(self) -> AudioFile:
        return get_audio_file_by_id(self.id)

    def get_stories_in_order_of_length(self) -> List[StoryInfo]:
        return sorted(
            [s.get_story_info() for s in self.stories],
            key=lambda s: s.word_count,
            reverse=True,
        )

    def get_most_significant_story(self) -> Optional[StoryInfo]:
        sorted_stories = self.get_stories_in_order_of_length()

        if not sorted_stories:
            return None

        total_word_count = sum(s.word_count for s in sorted_stories)
        if sorted_stories[0].word_count / total_word_count > 0.5:
            return sorted_stories[0]
        else:
            return self.stories[0].get_story_info()

    def tx_date(self):
        return extract_date_from_string(self.id)

    def title(self):
        most_significant_story = self.get_most_significant_story()
        if most_significant_story:
            return f"{most_significant_story.story.title}"
        else:
            return f"Hooting Yard {self.tx_date().isoformat()}"

    def get_archive_org_url(self) -> str:
        return f"https://archive.org/details/hy0_{self.id}"

    def album(self) -> str:
        return f"Hooting Yard {self.tx_date().year}"

    def get_duration(self) -> int:
        return int(math.floor(self.get_audio_file().get_metadata().info.time_secs))

    def get_title_and_text(self) -> str:
        story_titles_and_text: List[str] = [
            s.get_story_info().get_title_and_text() for s in self.stories
        ]
        return "\n\n".join(story_titles_and_text)

    def get_toc(self):
        toc_lines: List[str] = [
            f"{s.get_story_info().story.title} - {s.get_time_code_mmss()}"
            for s in self.stories
        ]
        return "\n".join(toc_lines)


def get_refined_index_by_id(index_id: str) -> RefinedShow:
    """
    @Glyn, this is probably the function you need to call to get a single RefinedShow object.
    """
    with open(get_refined_show_contents_file(index_id)) as index_file:
        return RefinedShow.from_dict(**yaml.safe_load(index_file))


def get_all_refined_shows() -> Iterator[RefinedShow]:
    for filename in sorted(os.listdir(get_refined_show_index_directory())):
        id, _ = filename.rsplit(".", maxsplit=1)
        yield get_refined_index_by_id(id)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
