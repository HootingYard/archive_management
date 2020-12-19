from hootingyard.index.match_transcripts_to_scripts import match_single_transcript
from hootingyard.index.ngram_to_script_index import ngram_to_script_index
from hootingyard.index.story_info import get_story_info_by_id
from hootingyard.transcript.transcript import get_transcript_by_filename


def test_matching():
    t = get_transcript_by_filename("hooting_yard_2008-04-24.txt")
    ngram_lookup_function = ngram_to_script_index()
    match_result = match_single_transcript(ngram_lookup_function, t)

def test_that_l_trigrams_from_the_script_are_in_the_index():
    story_info = get_story_info_by_id("2008-04-24-disquieting-ploppy-noises-from-behind-the-panel")
    ngram_lookup_function = ngram_to_script_index()
    for ngram in story_info.ngrams:
        result = ngram_lookup_function(tuple(ngram))
        assert story_info.story.id in result



