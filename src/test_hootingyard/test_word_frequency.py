from hootingyard.index.script_word_frequency import script_word_frequency


def test_load_word_frequency():
    wf: int = script_word_frequency()("marvelously")
    assert wf == 1
