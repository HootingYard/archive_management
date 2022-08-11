import datetime

from hootingyard.utils.date_utils import extract_date_from_string


def test_extract_date_from_string0():
    assert extract_date_from_string("hooting_yard_2015-03-19.txt") == datetime.date(
        2015, 3, 19
    )


def test_extract_date_from_string1():
    assert extract_date_from_string("2007-03-16-sappensopp-days") == datetime.date(
        2007, 3, 16
    )


def test_extract_date_from_string2():
    # 'hooting_yard_2007-05-02'
    assert extract_date_from_string("hooting_yard_2007-05-02") == datetime.date(
        2007, 5, 2
    )
