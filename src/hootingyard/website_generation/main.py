import logging

from pathlib import Path
from hootingyard.api.stories import get_narrations_for_story
from hootingyard.config.directories import get_keyml_root  # , get_website_directory

log = logging.getLogger(__name__)

#Website = Path(get_website_directory())
Website = Path('~/Documents/hootingyard').expanduser()
BigBook = Path(get_keyml_root()) / 'books' / 'bigbook'

BigBookText = BigBook / 'Text'
WebsiteText = Website / 'Text'


def process_stories():
    for file in BigBookText.glob('[12]*.xhtml'):
        narrations = list(get_narrations_for_story(file.stem))
        if narrations:
            print(file)
            for n in narrations:
                print('\t', n.get_show().title(), n.time_code)


def main():
    process_stories()


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
