from search import *

doc0 = "aaabaad"
query0 = "a b d"
expected_match_result = MatchResult(
    spans=[Span(start=0, end=1), Span(start=3, end=4), Span(start=6, end=7)]
)


def test_match():
    res = TextMatcher.match(query0, doc0)
    assert res == expected_match_result


def test_search():
    text_matcher = TextMatcher([doc0, "abc"])
    line_nos, lines, match_results = text_matcher.filter(query0)
    assert match_results == [expected_match_result]
    assert line_nos == [0]
    assert lines == [doc0]
