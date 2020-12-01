import os

from hootingyard.config.config import get_config


def get_archive_root():
    return os.path.join(get_config().project_directory, "archive")
