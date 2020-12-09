import datetime

from hootingyard.transcript.transcript import extract_speaker_and_timecode


def test_extract_speaker_and_timecode0():
    input_string = "Frank Key  09:13"
    expected_speaker = "Frank Key"
    expected_timecode = datetime.timedelta(minutes=9, seconds=13)

    speaker, timecode = extract_speaker_and_timecode(input_string)


    assert speaker == expected_speaker
    assert timecode == expected_timecode
