import os
from typing import Iterator, Tuple

from hootingyard.config.directories import get_archive_root

def get_archive_files(archive_root, filter_fn=lambda x:x.endswith(".mp3"))->Iterator[str]:
    for root, _, files in os.walk(archive_root):
        for f in files:
            if filter_fn(f):
                yield os.path.join(root, f)

def get_show_archives(archive_root)->Iterator[Tuple[int,str]]:
    for year in range(2004, 2020):
        year_root = os.path.join(archive_root, str(year))
        for path in get_archive_files(year_root):
            yield year, path



def main():
    archive_root:str = get_archive_root()
    for year, path in get_show_archives(archive_root):
        print(year,path)





if __name__ == "__main__":
    main()
