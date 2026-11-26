# AC#3: `python -m wordfreq` reads stdin, prints sorted TSV with a trailing
# newline, and exits 2 on a missing file. main returns 0 or 2.
#
# Target: wordfreq/cli.py::main (invoked through `python -m wordfreq`).
# Import root: wordfreq

import subprocess
import sys

import pytest


def _run_wordfreq(args=None, stdin_text=""):
    """Run `python -m wordfreq` as a real subprocess and capture its output."""
    cmd = [sys.executable, "-m", "wordfreq"] + list(args or [])
    return subprocess.run(
        cmd,
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.fixture
def stdin_sample():
    return "the cat the dog the cat\n"


def test_wordfreq_stdin_exit_code_zero(stdin_sample):
    result = _run_wordfreq(stdin_text=stdin_sample)
    assert result.returncode == 0


def test_wordfreq_stdin_output_ends_with_trailing_newline(stdin_sample):
    result = _run_wordfreq(stdin_text=stdin_sample)
    assert result.stdout.endswith("\n")


def test_wordfreq_stdin_output_lines_are_tab_separated(stdin_sample):
    result = _run_wordfreq(stdin_text=stdin_sample)
    lines = [line for line in result.stdout.split("\n") if line]
    assert lines and all("\t" in line for line in lines)


def test_wordfreq_stdin_output_most_frequent_word_first(stdin_sample):
    result = _run_wordfreq(stdin_text=stdin_sample)
    first_line = result.stdout.split("\n")[0]
    assert first_line.split("\t")[0] == "the"


def test_wordfreq_missing_file_exit_code_two(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    result = _run_wordfreq(args=[str(missing)])
    assert result.returncode == 2
