import os

from hootingyard.config.config import get_config


def get_archive_root():
    return os.path.join(get_config().project_directory, "archive")


def get_keyml_root():
    return get_config().keyml_directory


def get_analysis_directory()->str:
    return get_config().analysis_directory


def get_transcript_directory():
    return os.path.join(get_analysis_directory(), "transcripts")


def get_big_book_scripts_dirctory():
    return os.path.join(get_keyml_root(), "books/bigbook/Text")


def get_stories_dirctory():
    return os.path.join(get_analysis_directory(), "stories")

def get_statistics_directory():
    return os.path.join(get_analysis_directory(), "statistics")
