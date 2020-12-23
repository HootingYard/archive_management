import logging

from eyed3.core import Date
from eyed3.id3 import ID3_DEFAULT_VERSION

from hootingyard.api.stories import get_all_show_information
from hootingyard.audio.audio_file import AudioFile
from hootingyard.index.refine_index import RefinedShow

log = logging.getLogger(__name__)


def fix_id3_for_show(show_info: RefinedShow):
    log.info(f"Fixing ID3 tags for {show_info.id}")

    tx_date = show_info.tx_date()
    id3_date = Date(year=tx_date.year, month=tx_date.month, day=tx_date.day)

    audio: AudioFile = show_info.get_audio_file()
    metadata = audio.get_metadata()

    metadata.tag.title = show_info.title()
    metadata.tag.album = show_info.album()

    metadata.tag.album_artist = "Frank Key"
    metadata.tag.artist = "Frank Key"
    metadata.tag.recording_date = id3_date
    metadata.tag.encoding_date = id3_date
    metadata.tag.genre = "Humour"

    for story in show_info.stories:
        story_info = story.get_story_info()
        start_time = story.time_code
        story_title = story_info.story.title
        end_time = (
            story.next_story.time_code if story.next_story else show_info.get_duration()
        )
        metadata.tag.chapters.set(story_title.encode("utf-8"), (start_time, end_time))

    metadata.tag.save(version=ID3_DEFAULT_VERSION)

    log.info(f"Finished: {show_info.id}")


def main():
    for show_info in get_all_show_information():
        fix_id3_for_show(show_info)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
