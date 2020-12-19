from hootingyard.index.match_transcripts_to_scripts import match_single_transcript
from hootingyard.index.ngram_to_script_index import ngram_to_script_index
from hootingyard.transcript.transcript import get_transcript_by_filename


def test_matching():
    t = get_transcript_by_filename("hooting_yard_2008-04-24.txt")
    ngram_lookup_function = ngram_to_script_index()
    match_result = match_single_transcript(ngram_lookup_function, t)

    print(match_result)
