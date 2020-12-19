import datetime
import re


def extract_date_from_string(s: str) -> datetime.date:
    for m in re.findall("([0-9]{4})-([0-9]{2})-([0-9]{2})", s):
        return datetime.date(*[int(x) for x in m])
