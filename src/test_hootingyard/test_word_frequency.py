from hootingyard.index.script_word_frequency import word_frequency


def test_load_word_frequency():
    wf:int = word_frequency()("marvelously")
    assert wf==1
