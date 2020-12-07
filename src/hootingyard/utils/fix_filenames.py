import dateparser.search
import os
import datetime
from typing import Iterator, Tuple
import logging

log = logging.getLogger(__name__)

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

from hootingyard.config.directories import get_archive_root

def get_archive_files(archive_root, filter_fn=lambda x:x.endswith(".mp3"))->Iterator[str]:
    for root, _, files in os.walk(archive_root):
        for f in files:
            if filter_fn(f):
                yield os.path.join(root, f)

def get_show_archives(archive_root)->Iterator[Tuple[int,str]]:
    for year in range(2004, 2020):
        year_root = os.path.join(archive_root, str(year))
        for path in get_archive_files(year_root):
            yield year, path


def guess_date(year, date_string):
    d = dateparser.parse(date_string)
    if d:
        return d.date()

    four_digit_year = str(year)
    two_digit_year = four_digit_year[-2:]

    if four_digit_year not in date_string:
        if date_string.endswith(f" {two_digit_year}"):
            date_string = date_string[:-2] + four_digit_year

    d = dateparser.parse(date_string)
    if d:
        return d.date()

    if len(date_string) == 8:
        yyyy,mm,dd = [int(x) for x in [date_string[:4], date_string[4:6], date_string[6:]]]
        assert yyyy == year
        return datetime.date(yyyy,mm,dd)

    raise ValueError(f"Cannot parse: {date_string}")

def extract_date_string(filename):
    filename = filename.replace(".mp3", "")
    filename = filename.replace("_", " ")
    filename = filename.replace("-", " ")

    for s in ["hooting", "yard", "on", "the", "air"]:
        if filename.lower().startswith(s):
            filename = filename[len(s):]
            filename = filename.lstrip()

    for s in ["fixed"]:
        if filename.lower().endswith(s):
            filename = filename[:-1*len(s)]
            filename = filename.lstrip()

    return filename

def extract_date(filename:str, year:int)->datetime.date:
    date_string = extract_date_string(filename)
    extracted_date = guess_date(year,date_string)
    assert extracted_date.year == year, f"{WEEKDAYS[extracted_date.weekday()]} {extracted_date} is not in year {year}"
    return extracted_date

def main():
    archive_root:str = get_archive_root()

    filenames = set()

    for year, path in get_show_archives(archive_root):
        dirname = os.path.dirname(path)
        filename = os.path.basename(path)
        tx_date = extract_date(filename, year)

        if year > 2004:
            if tx_date.weekday() != 2:
                print(f"{filename} is a {WEEKDAYS[tx_date.weekday()]} not a Wednesday!")

        corrected_filename = f"hooting_yard_{tx_date.isoformat()}.mp3"

        assert corrected_filename not in filenames, f"{corrected_filename} already exists, was originally {filename}"
        filenames.add(corrected_filename)

        corrected_path = os.path.join(dirname, corrected_filename)

        # os.rename(path, corrected_path)






if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
