import logging

from hootingyard.api.stories import get_story_to_show_index
from hootingyard.index.all_stories_iterator import all_stories_iterator

log = logging.getLogger(__name__)


def main():
    stories_never_narrated = []
    index = get_story_to_show_index()
    for story in all_stories_iterator():
        try:
            index[story.id]
        except KeyError:
            stories_never_narrated.append(story.id)

    # pprint.pprint(stories_never_narrated)

    print("\n".join(sorted(stories_never_narrated)))


if __name__ == "__main__":
    main()
