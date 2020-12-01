import dataclasses
import functools
import os

import yaml


@dataclasses.dataclass
class Config:
    project_directory: str # This should be the path to hooting_yard_projects dropbox

@functools.lru_cache()
def get_config():
    with open(os.path.expanduser("~/.config/hootingyard/config.yaml")) as config_file:
        return Config(**yaml.load(config_file))
