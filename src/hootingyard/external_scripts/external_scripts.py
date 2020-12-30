import re
from typing import Iterator

from hootingyard.config.directories import get_external_scripts_directory
from hootingyard.config.files import get_external_scripts_iterator
from hootingyard.index.story import Story
from hootingyard.utils.date_utils import extract_date_from_string

"""
@dataclass
class Story:
    id: str
    title: str
    date: datetime.date
    text: str
"""


def get_external_stories() -> Iterator[Story]:
    for script_file_path in get_external_scripts_iterator():
        with open(script_file_path) as sf:

            title = next(sf).strip()
            date = extract_date_from_string(next(sf))
            text = "\n".join(sf)

            lower_title = re.sub("\s+", "_", title.lower())
            iso_date = date.isoformat()

            story_id = f"external_{lower_title}-{iso_date}"

            yield Story(id=story_id, title=title, date=date, text=text)


if __name__ == "__main__":
    for s in get_external_stories():
        print(s.id)
