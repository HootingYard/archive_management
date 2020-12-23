import os
from dataclasses import dataclass
from typing import Optional

from hootingyard.config.directories import get_transcript_directory
from hootingyard.transcript.transcript import Transcript, get_transcript_by_filename


@dataclass
class DuplicateStatus:
    is_duplicated: bool
    good_file: str
    bad_file: Optional[str]


def get_duplicated_file_name(file_name:str):
    file_name_without_extension, _=file_name.rsplit(".", maxsplit=1)
    return f"{file_name_without_extension} (1).txt"


def main():
    transcript_directory = get_transcript_directory()
    all_files = os.listdir(transcript_directory)

    non_duplicated_files = [f for f in all_files if "(1)" not in f]

    commands = []

    for file_name in non_duplicated_files:
        duplicated_file_name = get_duplicated_file_name(file_name)

        original_file_path = os.path.join(transcript_directory, file_name)
        duplicated_file_path = os.path.join(transcript_directory, duplicated_file_name)

        if os.path.exists(original_file_path) and os.path.exists(duplicated_file_path):


            t0:Transcript = get_transcript_by_filename(file_name)
            t1:Transcript = get_transcript_by_filename(duplicated_file_name)

            speaker0 = next(t0.paragraphs()).speaker
            speaker1 = next(t1.paragraphs()).speaker

            if speaker0 == "Unknown Speaker":
                print(f"Duplicate found: {file_name}->{speaker0}, {duplicated_file_name}->{speaker1}")
                commands.append(f"cp \"{duplicated_file_name}\" {file_name}")

            commands.append(f"git rm \"{duplicated_file_name}\"")


    print("\n".join(commands))



if __name__ == "__main__":
    main()
