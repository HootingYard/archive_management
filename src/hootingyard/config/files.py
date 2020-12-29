import os
from pathlib import Path
from typing import Iterator

from hootingyard.config.directories import (
    get_external_data_directory,
    get_statistics_directory,
    get_index_directory,
    get_show_index_directory,
    get_refined_show_index_directory,
    get_matches_directory,
    get_archive_root, get_external_scripts_directory,
)
from hootingyard.utils.date_utils import extract_date_from_string


def get_corncob_lowercase_path() -> str:
    return os.path.join(get_external_data_directory(), "corncob_lowercase.txt")


def word_frequency_csv_file_path() -> str:
    return os.path.join(get_statistics_directory(), "word_frequency.csv")


def script_word_frequency_yaml_file_path() -> str:
    return os.path.join(get_statistics_directory(), "script_word_frequency.yaml")


def transcript_word_frequency_yaml_file_path() -> str:
    return os.path.join(get_statistics_directory(), "transcript_word_frequency.yaml")


def ngram_to_story_index_file() -> str:
    return os.path.join(get_index_directory(), "hashed_ngrams_to_story_id.pickle")


def transcript_to_script_matches() -> str:
    return os.path.join(get_index_directory(), "transcript_to_script_matches.yaml")


def get_transcript_to_script_match_file(show_id: str) -> str:
    return os.path.join(get_matches_directory(), f"{show_id}.yaml")


def get_refined_show_contents_file(show_id: str) -> str:
    return os.path.join(get_refined_show_index_directory(), f"{show_id}.yaml")


def get_audio_file_path_by_id(show_id) -> str:
    date = extract_date_from_string(show_id)
    filename = f"{show_id}.mp3"
    return os.path.join(get_archive_root(), str(date.year), filename)

def get_audio_file_name_iterator()->Iterator[str]:
    for file_path in Path(get_archive_root()).glob("**/*.mp3"):
        yield str(file_path)


def get_external_scripts_iterator()->Iterator[str]:
    for file_path in Path(get_external_scripts_directory()).glob("*.txt"):
        yield str(file_path)

def get_transcript_to_script_match_files() -> Iterator[str]:
    index_directory = get_matches_directory()
    for file_name in os.listdir(index_directory):
        yield os.path.join(index_directory, file_name)
