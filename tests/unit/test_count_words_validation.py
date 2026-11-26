# Acceptance criterion (AC#1): count_words raises ValueError with exact messages:
#   ValueError('min_len must be >= 1') when min_len < 1
#   ValueError('top must be >= 0') when top < 0

import pytest

from wordfreq.cli import count_words


SAMPLE_TEXT = "the quick brown fox jumps over the lazy dog"


@pytest.mark.parametrize(
    "min_len",
    [0, -1, -5],
    ids=["min_len_zero", "min_len_minus_one", "min_len_minus_five"],
)
def test_count_words_min_len_below_one_raises_value_error(min_len):
    with pytest.raises(ValueError) as exc_info:
        count_words(SAMPLE_TEXT, min_len=min_len, top=10)
    assert str(exc_info.value) == "min_len must be >= 1"


@pytest.mark.parametrize(
    "top",
    [-1, -10],
    ids=["top_minus_one", "top_minus_ten"],
)
def test_count_words_top_below_zero_raises_value_error(top):
    with pytest.raises(ValueError) as exc_info:
        count_words(SAMPLE_TEXT, min_len=1, top=top)
    assert str(exc_info.value) == "top must be >= 0"


def test_count_words_min_len_below_one_raises_with_exact_type():
    with pytest.raises(ValueError) as exc_info:
        count_words(SAMPLE_TEXT, min_len=0, top=10)
    assert type(exc_info.value) is ValueError


def test_count_words_top_below_zero_raises_with_exact_type():
    with pytest.raises(ValueError) as exc_info:
        count_words(SAMPLE_TEXT, min_len=1, top=-1)
    assert type(exc_info.value) is ValueError
