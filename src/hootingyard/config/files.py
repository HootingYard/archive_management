import os

from hootingyard.config.directories import get_external_data_directory, get_statistics_directory


def get_corncob_lowercase_path()->str:
    return os.path.join(get_external_data_directory(), "corncob_lowercase.txt")

def word_frequency_csv_file_path()->str:
    return os.path.join(get_statistics_directory(), "word_frequency.csv")

def script_word_frequency_yaml_file_path()->str:
    return os.path.join(get_statistics_directory(), "script_word_frequency.yaml")

def transcript_word_frequency_yaml_file_path()->str:
    return os.path.join(get_statistics_directory(), "transcript_word_frequency.yaml")
