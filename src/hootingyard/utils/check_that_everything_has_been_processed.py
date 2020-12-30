from hootingyard.audio.audio_file import get_audio_file_iterator
from hootingyard.index.refine_index import get_refined_index_by_id


def has_refined_index(id: str) -> bool:
    try:
        get_refined_index_by_id(id)
    except FileNotFoundError:
        return False
    return True


def main():
    for af in get_audio_file_iterator():
        if not has_refined_index(af.get_id()):
            print(af.get_id())


if __name__ == "__main__":
    main()
