import logging

from hootingyard.api.stories import get_all_show_information

log = logging.getLogger(__name__)


def main():
    for show in get_all_show_information():
        if len(show.stories) == 0:
            print(show.id)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
