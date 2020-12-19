import os

from hootingyard.config.directories import get_external_data_directory, get_statistics_directory, get_index_directory


def get_corncob_lowercase_path()->str:
    return os.path.join(get_external_data_directory(), "corncob_lowercase.txt")

def word_frequency_csv_file_path()->str:
    return os.path.join(get_statistics_directory(), "word_frequency.csv")

def script_word_frequency_yaml_file_path()->str:
    return os.path.join(get_statistics_directory(), "script_word_frequency.yaml")

def transcript_word_frequency_yaml_file_path()->str:
    return os.path.join(get_statistics_directory(), "transcript_word_frequency.yaml")

def ngram_to_story_index_file()->str:
    return os.path.join(get_index_directory(), "hashed_ngrams_to_story_id.pickle")

def transcript_to_script_matches()->str:
    return os.path.join(get_index_directory(), "transcript_to_script_matches.yaml")

def get_transcript_to_script_match_file(show_id:str)->str:
    return os.path.join(get_index_directory(), "matches", f"{show_id}.yaml")
