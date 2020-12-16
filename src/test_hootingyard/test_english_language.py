from hootingyard.analysis.english_words import english_words


def test_filter_words():#
    elf = english_words()
    some_words = "who why where or what is the acond of swat"
    filtered_words = [w for w in some_words.split(" ") if elf(w)]
    assert " ".join(filtered_words) == "who why where or what is the of swat"
