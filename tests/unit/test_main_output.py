# Criterion (AC#3): main reads stdin, honors flags, terminates output with final newline, returns 0.
# Spec: `main` and `python -m wordfreq` read from `sys.stdin` by default when no `path` argument
# is given (or when `path` is "-"), honor --case-sensitive, --top, --min-len, and --json,
# terminate non-empty TSV output and --json output with a final "\n" (writing nothing for
# empty TSV output), and return 0 on success.

import io
import json
import sys

import pytest

from wordfreq.cli import main


@pytest.fixture
def stdin_text(monkeypatch):
    def _set(text):
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))

    return _set


def test_main_default_reads_stdin_returns_zero(stdin_text, capsys):
    stdin_text("apple banana apple\n")
    rc = main([])
    assert rc == 0


def test_main_default_reads_stdin_outputs_counts(stdin_text, capsys):
    stdin_text("apple banana apple\n")
    main([])
    assert capsys.readouterr().out == "apple\t2\nbanana\t1\n"


def test_main_dash_path_reads_stdin(stdin_text, capsys):
    stdin_text("apple banana apple\n")
    rc = main(["-"])
    assert (rc, capsys.readouterr().out) == (0, "apple\t2\nbanana\t1\n")


def test_main_tsv_output_ends_with_single_newline(stdin_text, capsys):
    stdin_text("apple banana\n")
    main([])
    out = capsys.readouterr().out
    assert out.endswith("\n") and not out.endswith("\n\n")


def test_main_empty_tsv_output_writes_nothing(stdin_text, capsys):
    stdin_text("")
    rc = main([])
    assert (rc, capsys.readouterr().out) == (0, "")


def test_main_case_sensitive_flag_keeps_case(stdin_text, capsys):
    stdin_text("Apple apple\n")
    main(["--case-sensitive"])
    assert capsys.readouterr().out == "Apple\t1\napple\t1\n"


def test_main_default_lowercases_input(stdin_text, capsys):
    stdin_text("Apple apple\n")
    main([])
    assert capsys.readouterr().out == "apple\t2\n"


def test_main_top_flag_limits_rows(stdin_text, capsys):
    stdin_text("apple apple banana banana cherry\n")
    main(["--top", "1"])
    assert capsys.readouterr().out == "apple\t2\n"


def test_main_min_len_flag_filters_short_words(stdin_text, capsys):
    stdin_text("a an ant apple\n")
    main(["--min-len", "3"])
    assert capsys.readouterr().out == "ant\t1\napple\t1\n"


def test_main_json_flag_output_ends_with_newline(stdin_text, capsys):
    stdin_text("apple banana apple\n")
    main(["--json"])
    out = capsys.readouterr().out
    assert out.endswith("\n")


def test_main_json_flag_output_is_valid_json(stdin_text, capsys):
    stdin_text("apple banana apple\n")
    main(["--json"])
    assert json.loads(capsys.readouterr().out) is not None


def test_main_json_flag_empty_input_output_ends_with_newline(stdin_text, capsys):
    stdin_text("")
    main(["--json"])
    out = capsys.readouterr().out
    assert out.endswith("\n")


def test_main_json_flag_returns_zero(stdin_text, capsys):
    stdin_text("apple banana apple\n")
    rc = main(["--json"])
    assert rc == 0
