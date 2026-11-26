# Criterion (AC#3): main returns 2 with non-empty stderr on invalid arguments
# (bad --top / --min-len, unknown flag) or missing files.

from wordfreq.cli import main
import pytest


@pytest.mark.parametrize(
    "argv",
    [
        ["--top", "abc"],
        ["--top=-1"],
        ["--min-len", "abc"],
        ["--min-len=0"],
        ["--bogus"],
    ],
    ids=[
        "top-non-integer",
        "top-negative",
        "min-len-non-integer",
        "min-len-zero",
        "unknown-flag",
    ],
)
def test_main_invalid_argument_returns_two(argv):
    result = main(argv)

    assert result == 2


@pytest.mark.parametrize(
    "argv",
    [
        ["--top", "abc"],
        ["--top=-1"],
        ["--min-len", "abc"],
        ["--min-len=0"],
        ["--bogus"],
    ],
    ids=[
        "top-non-integer",
        "top-negative",
        "min-len-non-integer",
        "min-len-zero",
        "unknown-flag",
    ],
)
def test_main_invalid_argument_writes_stderr(argv, capsys):
    try:
        main(argv)
    except SystemExit:
        pass

    captured = capsys.readouterr()

    assert captured.err != ""


def test_main_missing_file_returns_two(tmp_path):
    missing = tmp_path / "does_not_exist.txt"

    result = main([str(missing)])

    assert result == 2


def test_main_missing_file_writes_stderr(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"

    try:
        main([str(missing)])
    except SystemExit:
        pass

    captured = capsys.readouterr()

    assert captured.err != ""
