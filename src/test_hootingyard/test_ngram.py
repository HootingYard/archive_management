from hootingyard.analysis.ngram import ngrams, score_ngrams, NgramWithScore, get_ngrams


def test_ngram1():
    result = list(ngrams(n=1, inp=range(3)))
    assert result == [[0], [1], [2]]


def test_ngram2():
    result = list(ngrams(n=2, inp=range(4)))
    assert result == [[0, 1], [1, 2], [2, 3]]


def test_ngram3():
    result = list(ngrams(n=3, inp=range(5)))
    assert result == [[0, 1, 2], [1, 2, 3], [2, 3, 4]]


def test_ngram4():
    result = list(ngrams(n=3, inp=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]))
    assert result == [[1, 1, 1]]


def test_ngram_alpha():
    result = list(ngrams(n=3, inp="abc"))
    assert result == [
        ["a", "b", "c"],
    ]


def test_g_ngrams_with_words():
    source_text = "the time before time is a land we have forgotten".split(" ")

    scoring_function = lambda x: len(x)
    filter_function = lambda x: True

    result = get_ngrams(
        ngram_length=3,
        max_ngrams=4,
        wf_scoring_function=scoring_function,
        filter_function=filter_function,
        word_iterator=iter(source_text),
    )

    assert result == [
        "we have forgotten",
        "time before time",
        "the time before",
        "before time is",
    ]


def test_score_ngrams():
    ngrams = [["a", "b"], ["a", "c"]]
    scoring_function = {"a": 1, "b": 2, "c": 5}.get

    result = list(
        score_ngrams(ngrams_iterator=ngrams, scoring_function=scoring_function)
    )

    assert result == [
        NgramWithScore(ngram=["a", "b"], score=3),
        NgramWithScore(ngram=["a", "c"], score=6),
    ]
