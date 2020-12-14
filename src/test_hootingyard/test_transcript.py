import datetime

from hootingyard.transcript.transcript import (
    Transcript,
    get_transcript_by_date,
    TranscriptParagraph,
)


def test_get_transcript_by_date():
    t: Transcript = get_transcript_by_date(datetime.date(2007, 2, 7))
    assert isinstance(t, Transcript), f"Expected a Transcript, got {t}"


def test_iterate_over_transcript_paragraphs():
    t: Transcript = get_transcript_by_date(datetime.date(2014, 3, 14))
    first_paragraph: TranscriptParagraph = next(t.paragraphs())
    assert isinstance(first_paragraph, TranscriptParagraph)
    assert first_paragraph.speaker == "Frank Key"
