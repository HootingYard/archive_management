import logging

log = logging.getLogger(__name__)
from hootingyard.utils.generators import get_audio_path_and_transcript


def main():
    for item in get_audio_path_and_transcript():
        if item.transcript:
            print(item)
            for para in item.transcript:
                print(para)



if __name__ == "__main__":
    main()
