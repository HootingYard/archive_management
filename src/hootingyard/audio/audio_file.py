import os
from dataclasses import dataclass

import eyed3
import eyed3.mp3

from hootingyard.config.files import get_audio_file_path_by_id

class AudioFileError(RuntimeError):pass

@dataclass
class AudioFile:
    path: str

    def valid(self):
        return os.path.exists(self.path)

    def get_metadata(self)->eyed3.mp3.Mp3AudioFile:
        return eyed3.load(self.path)


def get_audio_file_by_id(id: str) -> AudioFile:
    audio_path_file:str = get_audio_file_path_by_id(id)
    if not os.path.exists(audio_path_file):
        raise AudioFileError("The file does not exist.")
    return AudioFile(path=audio_path_file)
