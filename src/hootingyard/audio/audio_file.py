import os
from collections.abc import Iterator
from dataclasses import dataclass

import eyed3
import eyed3.mp3

from hootingyard.config.files import (
    get_audio_file_name_iterator,
    get_audio_file_path_by_id,
)


class AudioFileError(RuntimeError):
    pass


@dataclass
class AudioFile:
    path: str

    def valid(self):
        return os.path.exists(self.path)

    def get_metadata(self) -> eyed3.mp3.Mp3AudioFile:
        return eyed3.load(self.path)

    def get_id(self) -> str:
        fn = os.path.basename(self.path)
        the_id, _ = fn.rsplit(".", maxsplit=1)
        return the_id


def get_audio_file_by_id(id: str) -> AudioFile:
    audio_path_file: str = get_audio_file_path_by_id(id)
    if not os.path.exists(audio_path_file):
        raise AudioFileError("The file does not exist.")
    return AudioFile(path=audio_path_file)


def get_audio_file_iterator() -> Iterator[AudioFile]:
    for p in get_audio_file_name_iterator():
        yield AudioFile(path=p)
