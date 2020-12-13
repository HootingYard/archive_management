import os

from hootingyard.config.config import get_config


def get_archive_root():
    return os.path.join(get_config().project_directory, "archive")


def get_keymal_root():
    return get_config().keyml_directory


def get_transcript_directory():
    return os.path.join(get_keymal_root(), "transcripts")


def get_big_book_scripts_dirctory():
    return os.path.join(get_keymal_root(), "books/bigbook/Text")


def get_stories_dirctory():
    return os.path.join(get_keymal_root(), "stories")
