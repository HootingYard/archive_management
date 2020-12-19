import logging

from hootingyard.index import script_word_frequency, transcript_word_frequency, match_transcripts_to_scripts, \
    refine_index
from hootingyard.utils import generate_script_index

log = logging.getLogger(__name__)

def main():
    log.info("Calculating script word frquency.")
    script_word_frequency.main()
    log.info("Calculating transcript word frquency.")
    transcript_word_frequency.main()
    log.info("Building an index of scripts.")
    generate_script_index.main()
    log.info("Matching transcripts to scripts.")
    match_transcripts_to_scripts.main()
    log.info("Refining the index.")
    refine_index.main()

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
