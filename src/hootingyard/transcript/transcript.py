import datetime
import os
import re
from dataclasses import dataclass
from typing import Iterator, Tuple

from hootingyard.config.directories import get_transcript_directory

MULTIPLIERS = [1, 60, 60 * 60]


def convert_string_timecode_to_timedelta(inp: str) -> datetime.timedelta:
    seconds: int = sum(
        [a * b for (a, b) in zip(MULTIPLIERS, [int(a) for a in inp.split(":")[::-1]])]
    )
    return datetime.timedelta(seconds=seconds)


def extract_speaker_and_timecode(inp: str) -> Tuple[str, datetime.timedelta]:
    matches = re.findall("^([A-Za-z ]+)  ([0-9:]+)$", inp)
    for m in matches:
        return (m[0], convert_string_timecode_to_timedelta(m[1]))
    raise ValueError(f"Could not extract info from: `{inp}`")


@dataclass
class TranscriptParagraph:
    speaker: str
    time_code: datetime.timedelta
    text: str

    def word_iterator(self)->Iterator[str]:
        for island in re.split("[\s]+", self.text):
            yield from (w.lower() for w in re.findall("([a-zA-Z\-\']+)", island))


@dataclass
class Transcript:
    file_path: str

    def paragraphs(self) -> Iterator[TranscriptParagraph]:
        def take3(iter):
            l = [next(iter), next(iter)]
            try:
                l.append(next(iter))
            except StopIteration:
                l.append("")
            return l

        with open(file=self.file_path) as transcript_file:

            while True:
                try:
                    first_line, text, _ = take3(transcript_file)
                except StopIteration:
                    break
                speaker, time_code = extract_speaker_and_timecode(first_line)
                yield TranscriptParagraph(
                    speaker=speaker, time_code=time_code, text=text
                )

    def get_id(self)->str:
        the_id, ext = os.path.basename(self.file_path).rsplit(".", maxsplit=2)
        return the_id


def get_transcript_path_by_date(transcript_date: datetime.date) -> str:
    transcript_dir: str = get_transcript_directory()
    transcript_filename = f"hooting_yard_{transcript_date.isoformat()}.txt"
    return os.path.join(transcript_dir, transcript_filename)


def get_transcript_by_date(transcript_date: datetime.date) -> Transcript:
    return Transcript(get_transcript_path_by_date(transcript_date))

def get_transcript_by_filename(filename:str) -> Transcript:
    transcript_dir: str = get_transcript_directory()
    return Transcript(os.path.join(transcript_dir, filename))

def get_transcripts()->Iterator[Transcript]:
    transcripts_dir:str = get_transcript_directory()
    for file_name in os.listdir(transcripts_dir):
        file_path = os.path.join(transcripts_dir, file_name)
        yield Transcript(file_path)
