# AC#2: format_table formats rows as word\tcount lines separated by \n and returns '' for empty input
import pytest

from wordfreq.cli import format_table


@pytest.mark.parametrize(
    "rows,expected",
    [
        ([("the", 3), ("cat", 1)], "the\t3\ncat\t1"),
        ([("alpha", 10)], "alpha\t10"),
        ([("a", 2), ("b", 2), ("c", 1)], "a\t2\nb\t2\nc\t1"),
    ],
    ids=["two-rows", "single-row", "three-rows"],
)
def test_format_table_rows_joined_with_newline_and_tab_separator(rows, expected):
    assert format_table(rows) == expected


def test_format_table_rows_no_trailing_newline():
    result = format_table([("the", 3), ("cat", 1)])
    assert not result.endswith("\n")


def test_format_table_empty_input_returns_empty_string():
    assert format_table([]) == ""
