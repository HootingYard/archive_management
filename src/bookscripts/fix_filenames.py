import logging
import os

log = logging.getLogger(__name__)

from hootingyard.config.directories import get_archive_root
from hootingyard.utils.generators import WEEKDAYS, extract_date, get_show_archives


def main(warn_wednesday=False):
    archive_root: str = get_archive_root()

    filenames = set()

    for year, path in get_show_archives(archive_root):
        dirname = os.path.dirname(path)
        filename = os.path.basename(path)
        tx_date = extract_date(filename, year)

        if warn_wednesday:
            if year > 2004:
                if tx_date.weekday() != 2:
                    print(
                        f"{filename} is a {WEEKDAYS[tx_date.weekday()]} not a Wednesday!"
                    )

        corrected_filename = f"hooting_yard_{tx_date.isoformat()}.mp3"

        if filename != corrected_filename:
            log.info(f"Would rename {path} to {corrected_path}")

        assert (
            corrected_filename not in filenames
        ), f"{corrected_filename} already exists, was originally {filename}"
        filenames.add(corrected_filename)

        corrected_path = os.path.join(dirname, corrected_filename)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
