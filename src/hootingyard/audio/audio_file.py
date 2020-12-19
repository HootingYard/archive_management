import os
from dataclasses import dataclass

import mutagen

from hootingyard.config.files import get_audio_file_path_by_id
from hootingyard.utils.date_utils import extract_date_from_string


@dataclass
class AudioFile:
    path: str

    def valid(self):
        return os.path.exists(self.path)

    def get_metadata(self):
        return mutagen.File(self.path)


def get_audio_file_by_id(id:str)->AudioFile:
    return AudioFile(path=get_audio_file_path_by_id(id))

