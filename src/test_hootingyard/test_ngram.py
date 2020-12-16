from hootingyard.analysis.ngram import ngrams, score_ngrams, NgramWithScore


def test_ngram1():
    result = list(ngrams(n=1,inp=range(3)))
    assert result == [[0],[1],[2]]

def test_ngram2():
    result = list(ngrams(n=2,inp=range(4)))
    assert result == [[0,1],[1,2],[2,3]]

def test_ngram3():
    result = list(ngrams(n=3,inp=range(5)))
    assert result == [[0,1,2],[1,2,3],[2,3,4]]

def test_ngram_alpha():
    result = list(ngrams(n=3,inp="abc"))
    assert result == [["a","b","c"],]

def test_score_ngrams():
    ngrams = [["a", "b"], ["a","c"]]
    scoring_function = {
        "a":1,
        "b":2,
        "c":5
    }.get

    result = list(score_ngrams(ngrams_iterator=ngrams, scoring_function=scoring_function))

    assert result==[
        NgramWithScore(ngram=["a", "b"], score=3),
        NgramWithScore(ngram=["a", "c"], score=6),

    ]

