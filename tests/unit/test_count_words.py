# AC#1: count_words extracts tokens, lowercases, preserves case, filters min_len,
# sorts by (-count, word) and applies top.
#
# Expectations are taken from the criterion only. Signature verified against
# wordfreq/cli.py: count_words(text, *, min_len=1, ignore_case=True, top=None)
# returning a list of (word, count) tuples.

import pytest

from wordfreq.cli import count_words


def _as_pairs(result):
    return [(word, count) for word, count in result]


def test_count_words_extracts_alnum_tokens_only_returns_expected_words():
    text = "Hello, world! It's test-42 ok_go"
    words = {word for word, _ in count_words(text)}
    assert words == {"hello", "world", "it", "s", "test", "42", "ok", "go"}


def test_count_words_default_lowercases_tokens_returns_lowercase_word():
    result = _as_pairs(count_words("Apple APPLE apple"))
    assert result == [("apple", 3)]


def test_count_words_ignore_case_false_preserves_case_returns_distinct_words():
    result = _as_pairs(count_words("Apple APPLE apple", ignore_case=False))
    assert sorted(result) == sorted([("Apple", 1), ("APPLE", 1), ("apple", 1)])


@pytest.mark.parametrize(
    "min_len,expected_words",
    [
        (1, {"a", "bb", "ccc"}),
        (2, {"bb", "ccc"}),
        (3, {"ccc"}),
    ],
    ids=["min_len_1_keeps_all", "min_len_2_drops_single_char", "min_len_3_keeps_only_long"],
)
def test_count_words_min_len_filters_short_tokens_returns_expected_words(min_len, expected_words):
    words = {word for word, _ in count_words("a bb ccc", min_len=min_len)}
    assert words == expected_words


def test_count_words_sorts_by_count_desc_then_word_returns_ordered_pairs():
    result = _as_pairs(count_words("b a c c b b a z"))
    assert result == [("b", 3), ("a", 2), ("c", 2), ("z", 1)]


def test_count_words_ties_sorted_alphabetically_returns_word_order():
    result = _as_pairs(count_words("zeta alpha mike"))
    assert [word for word, _ in result] == ["alpha", "mike", "zeta"]


def test_count_words_top_limits_results_returns_first_n_pairs():
    result = _as_pairs(count_words("b a c c b b a z", top=2))
    assert result == [("b", 3), ("a", 2)]


def test_count_words_top_applied_after_sort_returns_highest_counts():
    result = _as_pairs(count_words("x y y z z z", top=1))
    assert result == [("z", 3)]


def test_count_words_empty_text_returns_empty_list():
    assert count_words("") == []
