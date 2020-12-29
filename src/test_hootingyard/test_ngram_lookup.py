from hootingyard.index.ngram_to_script_index import ngram_to_script_index


def test_ngram_lookup0():
    lookup_function = ngram_to_script_index()
    assert lookup_function("a b c") == set()


def test_ngram_lookup1():
    lookup_function = ngram_to_script_index()
    assert lookup_function("nincompoop wannabe historians") == {
        "2012-06-21-on-the-world-famous-food-splattered-jesuit",
        "2017-08-26-the-world-famous-food-splattered-jesuit",
    }
