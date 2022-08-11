import dataclasses
import functools
import logging
import os

import yaml

log = logging.getLogger(__name__)


@dataclasses.dataclass
class Config:
    project_directory: str  # This should be the path to hooting_yard_projects dropbox
    keyml_directory: str  # This should be where the keyml GitHub project is checked out
    analysis_directory: str  # This should be were the analysis project files are checked out.
    openai_api_key: str  # This should be the OpenAI API key


@functools.lru_cache
def get_config(config_file_path="~/.config/hootingyard/config.yaml"):
    expanded_config_file_path: str = os.path.expanduser(config_file_path)
    with open(expanded_config_file_path) as config_file:
        try:
            return Config(**yaml.load(config_file, Loader=yaml.SafeLoader))
        except TypeError:
            log.exception(
                f"Missing attribute in config file: {expanded_config_file_path}"
            )
            raise
