import datetime

from hootingyard.index.match_transcripts_to_scripts import extract_date_from_string


def test_extract_date_from_string0():
    assert extract_date_from_string("hooting_yard_2015-03-19.txt") == datetime.date(2015,3,19)


def test_extract_date_from_string1():
    assert extract_date_from_string("2007-03-16-sappensopp-days") == datetime.date(2007,3,16)
