import logging
from dataclasses import dataclass
from typing import List, Optional

import yaml

from hootingyard.config.files import transcript_to_script_matches
from hootingyard.utils.date_utils import extract_date_from_string

log = logging.getLogger(__name__)

def simplify_segment_result(time_code, votes, previous_segment:Optional[str]):
    total_votes = sum(votes.values())
    sorted_votes = sorted(votes.items(), key=lambda x:x[1], reverse=True)
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
        best_vote = max(sorted_votes[:2], key=lambda v:extract_date_from_string(v[0]))[0]
    else:
        raise RuntimeError("Not sure what to do")
        # best_vote = sorted_votes[0][0]

    return {
        "time_code":time_code,
        "story": best_vote
    }


def pick_matches(matches):
    previous_segment_result:Optional[str] = None
    for segment in matches:
        segment_result = simplify_segment_result(**segment, previous_segment=previous_segment_result)
        if segment_result:
            yield segment_result
            previous_segment_result = segment_result["story"]

def refine_show(id:str, matches):
    return {
        "id": id,
        "stories": list(pick_matches(matches))
    }

def main():
    with open(transcript_to_script_matches()) as matches_file:
        matches = yaml.safe_load(matches_file)


    for show, show_content in matches.items():
        print(show, show_content)

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
