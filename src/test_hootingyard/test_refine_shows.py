import yaml


def test_refine0():
    show_id = 'hooting_yard_2007-02-07'
    matches =  = {'hooting_yard_2007-02-07': {260: {'2007-02-06-good-king-wenceslas-impersonation-incident': 28,
                                              '2007-02-06-pick-some-words-n-save-resonance': 3},
                                        936: {'2007-02-05-the-socks-of-pepintude': 30}}}

    expected = [
            {"time_code": 260,
             "story_id": "2007-02-06-good-king-wenceslas-impersonation-incident"
             },
            {"time_code": 936,
             "story_id": "2007-02-05-the-socks-of-pepintude"
             },
        ]

    assert expected == extract_show_details_from_matches(show_id=hooting_yard_2007-02-07, matches=)
