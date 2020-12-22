import itertools
import logging
import pprint

import internetarchive
from internetarchive import upload, get_item, Item

from hootingyard.api.stories import get_all_show_information
from internetarchive.exceptions import ItemLocateError
from hootingyard.index.refine_index import RefinedShow

log = logging.getLogger(__name__)

IA_PRFX:str = "hy0"

def upload_single_show_to_internetarchive(show_info:RefinedShow):
    show_title = show_info.title()
    upload_id = f"{IA_PRFX}_{show_info.id}"
    log.info(f"Attempting to upload {show_info.id}, Title: {show_title}")

    show_text = show_info.get_title_and_text()
    show_toc = show_info.get_toc()

    md = {'collection': 'opensource_audio',
          'description': show_toc,
          'mediatype': 'audio',
          'title': show_title,
          'creator': "Frank Key",
          'date': show_info.tx_date().isoformat(),
          'notes': show_text,
          }


    log.info(f"Metadata: {pprint.pformat(md)}")

    try:
        item:Item = get_item(upload_id)
        log.info(f"Found an item: {item}")
        item.modify_metadata(metadata=md)
    except internetarchive.exceptions.ItemLocateError:
        r = upload(identifier=upload_id, files=[show_info.get_audio_file().path], metadata=md, verbose=True)
        assert r[0].status_code == 200
        log.info(f"Completed upload {show_info.id}")


def main():
    for show_info in itertools.islice(get_all_show_information(),0,50):
        upload_single_show_to_internetarchive(show_info)

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    main()
