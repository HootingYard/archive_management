import datetime

from hootingyard.transcript.transcript import (
    Transcript,
    TranscriptParagraph,
    get_transcript_by_date,
    get_transcript_by_filename,
)


def test_get_transcript_by_date():
    t: Transcript = get_transcript_by_date(datetime.date(2007, 2, 7))
    assert isinstance(t, Transcript), f"Expected a Transcript, got {t}"


def test_get_transcript_by_filename():
    t: Transcript = get_transcript_by_filename(filename="hooting_yard_2016-06-16.txt")
    assert isinstance(t, Transcript), f"Expected a Transcript, got {t}"


def test_iterate_over_transcript_paragraphs():
    t: Transcript = get_transcript_by_date(datetime.date(2014, 3, 14))
    first_paragraph: TranscriptParagraph = next(t.paragraphs())
    assert isinstance(first_paragraph, TranscriptParagraph)
    assert first_paragraph.speaker == "Frank Key"


def test_get_words_for_paragraphs_for_transcript():
    t: Transcript = get_transcript_by_filename(filename="hooting_yard_2016-06-16.txt")
    first_paragraph = next(t.paragraphs())
    assert first_paragraph.time_code == datetime.timedelta(seconds=13)


def test_second_paragraph():
    t: Transcript = get_transcript_by_filename(filename="hooting_yard_2016-06-16.txt")
    paragraphs = t.paragraphs()
    _ = next(paragraphs)
    second_paragraph = next(paragraphs)
    assert second_paragraph.time_code == datetime.timedelta(seconds=43)


def test_get_last_paragraph_for_transcript():
    t: Transcript = get_transcript_by_filename(filename="hooting_yard_2016-06-16.txt")
    last_paragraph = list(t.paragraphs())[-1]
    assert last_paragraph.text.startswith(
        "Finally this week"
    ), f"Wrong text: {last_paragraph.text}"
    assert last_paragraph.time_code == datetime.timedelta(seconds=27 * 60 + 9)


def test_get_id_for_transcript():
    t: Transcript = get_transcript_by_filename(filename="hooting_yard_2016-06-16.txt")
    assert t.get_id() == "hooting_yard_2016-06-16"
