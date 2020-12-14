import logging
import os
import datetime
from dataclasses import dataclass
from typing import Iterator, Tuple, Optional

import dateparser

from hootingyard.transcript.transcript import Transcript

log = logging.getLogger(__name__)

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

from hootingyard.config.directories import get_archive_root, get_transcript_directory


def get_archive_files(
    archive_root, filter_fn=lambda x: x.endswith(".mp3")
) -> Iterator[str]:
    for root, _, files in os.walk(archive_root):
        for f in files:
            if filter_fn(f):
                yield os.path.join(root, f)


def get_show_archives(archive_root) -> Iterator[Tuple[int, str]]:
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
        yyyy, mm, dd = [
            int(x) for x in [date_string[:4], date_string[4:6], date_string[6:]]
        ]
        assert yyyy == year
        return datetime.date(yyyy, mm, dd)

    raise ValueError(f"Cannot parse: {date_string}")


def extract_date_string(filename):
    filename = filename.replace(".mp3", "")
    filename = filename.replace("_", " ")
    filename = filename.replace("-", " ")

    for s in ["hooting", "yard", "on", "the", "air"]:
        if filename.lower().startswith(s):
            filename = filename[len(s) :]
            filename = filename.lstrip()

    for s in ["fixed"]:
        if filename.lower().endswith(s):
            filename = filename[: -1 * len(s)]
            filename = filename.lstrip()

    return filename


def extract_date(filename: str, year: int) -> datetime.date:
    date_string = extract_date_string(filename)
    extracted_date = guess_date(year, date_string)
    assert (
        extracted_date.year == year
    ), f"{WEEKDAYS[extracted_date.weekday()]} {extracted_date} is not in year {year}"
    return extracted_date


@dataclass
class AudioAndTranscript(object):
    audio_file_path: str
    transcript: Optional[Transcript]


def get_audio_path_and_transcript(
    archive_root=None, transcript_directory=None
) -> Iterator[AudioAndTranscript]:
    transcript_directory = transcript_directory or get_transcript_directory()
    for year, file_path in get_show_archives(archive_root or get_archive_root()):
        file_name = os.path.basename(file_path)

        file_name_without_extension, _ = file_name.rsplit(".", maxsplit=1)
        expected_transcript_filename = f"{file_name_without_extension}.txt"
        expected_transcript_file_path = os.path.join(
            transcript_directory, expected_transcript_filename
        )

        if os.path.exists(expected_transcript_file_path):
            yield AudioAndTranscript(
                file_path, Transcript(file_path=expected_transcript_file_path)
            )
        else:
            yield AudioAndTranscript(file_path, None)
