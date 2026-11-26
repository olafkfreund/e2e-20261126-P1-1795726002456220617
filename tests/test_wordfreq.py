"""Unit and CLI tests for the wordfreq package."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from wordfreq.cli import count_words, format_table, main

REPO_ROOT = Path(__file__).resolve().parents[1]


def _set_stdin(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(text))


# --- count_words / format_table -------------------------------------------


def test_count_words_basic_ranking() -> None:
    text = "Apple banana apple, cherry! Banana apple."
    assert count_words(text) == [("apple", 3), ("banana", 2), ("cherry", 1)]


def test_count_words_tie_breaks_alphabetically() -> None:
    text = "pear fig apple fig pear kiwi"
    assert count_words(text) == [
        ("fig", 2),
        ("pear", 2),
        ("apple", 1),
        ("kiwi", 1),
    ]


def test_count_words_order_is_independent_of_input_order() -> None:
    forward = count_words("a b c d")
    backward = count_words("d c b a")
    assert forward == backward == [("a", 1), ("b", 1), ("c", 1), ("d", 1)]


def test_count_words_lowercases_by_default() -> None:
    assert count_words("Word word WORD") == [("word", 3)]


def test_count_words_preserves_case_when_ignore_case_false() -> None:
    result = count_words("Word word WORD", ignore_case=False)
    # All three have count 1, so ties break by plain string order where
    # uppercase letters sort before lowercase.
    assert result == [("WORD", 1), ("Word", 1), ("word", 1)]


def test_count_words_token_pattern_splits_on_non_alphanumerics() -> None:
    assert count_words("don't stop_now route66 66") == [
        ("66", 1),
        ("don", 1),
        ("now", 1),
        ("route66", 1),
        ("stop", 1),
        ("t", 1),
    ]


def test_count_words_min_len_filters_short_words() -> None:
    assert count_words("a bb ccc bb", min_len=2) == [("bb", 2), ("ccc", 1)]


def test_count_words_top_limits_results() -> None:
    assert count_words("x y y z z z", top=2) == [("z", 3), ("y", 2)]


def test_count_words_top_zero_returns_empty() -> None:
    assert count_words("x y y", top=0) == []


def test_count_words_empty_text_returns_empty() -> None:
    assert count_words("") == []


@pytest.mark.parametrize("min_len", [0, -1])
def test_count_words_rejects_min_len_below_one(min_len: int) -> None:
    with pytest.raises(ValueError, match=r"^min_len must be >= 1$"):
        count_words("hello", min_len=min_len)


def test_count_words_rejects_negative_top() -> None:
    with pytest.raises(ValueError, match=r"^top must be >= 0$"):
        count_words("hello", top=-1)


def test_format_table_empty_returns_empty_string() -> None:
    assert format_table([]) == ""


def test_format_table_tsv() -> None:
    assert format_table([("apple", 3), ("banana", 2)]) == "apple\t3\nbanana\t2"


# --- main() / CLI ----------------------------------------------------------


def test_cli_top_and_min_len(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("to be or not to be that is the question", encoding="utf-8")
    rc = main([str(sample), "--min-len", "3", "--top", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().splitlines() == ["not\t1", "question\t1"]


def test_cli_reads_stdin_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _set_stdin(monkeypatch, "b a b\n")
    assert main([]) == 0
    assert capsys.readouterr().out == "b\t2\na\t1\n"


def test_cli_reads_stdin_when_path_is_dash(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _set_stdin(monkeypatch, "b a b\n")
    assert main(["-"]) == 0
    assert capsys.readouterr().out == "b\t2\na\t1\n"


def test_cli_case_sensitive_flag_splits_case_variants(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "case.txt"
    sample.write_text("Word word WORD\n", encoding="utf-8")

    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == "word\t3\n"

    assert main([str(sample), "--case-sensitive"]) == 0
    assert capsys.readouterr().out == "WORD\t1\nWord\t1\nword\t1\n"


def test_cli_tsv_output_ends_with_exactly_one_newline(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _set_stdin(monkeypatch, "apple apple banana banana banana\n")
    assert main([]) == 0
    out = capsys.readouterr().out
    assert out == "banana\t3\napple\t2\n"
    assert out.endswith("\n")
    assert not out.endswith("\n\n")


def test_cli_empty_tsv_prints_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _set_stdin(monkeypatch, "!!! --- ...\n")
    assert main([]) == 0
    assert capsys.readouterr().out == ""


def test_cli_json_output_ends_with_exactly_one_newline(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _set_stdin(monkeypatch, "b a b\n")
    assert main(["--json"]) == 0
    out = capsys.readouterr().out
    assert out.endswith("\n")
    assert not out.endswith("\n\n")
    assert json.loads(out) == [
        {"word": "b", "count": 2},
        {"word": "a", "count": 1},
    ]


def test_cli_json_empty_input_prints_empty_array(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _set_stdin(monkeypatch, "")
    assert main(["--json"]) == 0
    assert capsys.readouterr().out == "[]\n"


def test_cli_json_respects_case_sensitive_and_top(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _set_stdin(monkeypatch, "Word word WORD\n")
    assert main(["--json", "--case-sensitive", "--top", "1"]) == 0
    assert json.loads(capsys.readouterr().out) == [{"word": "WORD", "count": 1}]


def test_cli_rejects_min_len_zero(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _set_stdin(monkeypatch, "hello\n")
    assert main(["--min-len", "0"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "min_len must be >= 1" in captured.err


def test_cli_rejects_negative_top(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _set_stdin(monkeypatch, "hello\n")
    assert main(["--top", "-1"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "top must be >= 0" in captured.err


def test_cli_rejects_non_integer_top(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _set_stdin(monkeypatch, "hello\n")
    assert main(["--top", "abc"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "invalid int value" in captured.err


def test_cli_missing_file_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "does-not-exist.txt"
    assert main([str(missing)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "cannot read" in captured.err
    assert str(missing) in captured.err


# --- python -m wordfreq ----------------------------------------------------


def _run_module(*args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "wordfreq", *args],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )


def test_python_m_wordfreq_reads_stdin() -> None:
    result = _run_module(stdin="b a b\n")
    assert result.returncode == 0
    assert result.stdout == "b\t2\na\t1\n"
    assert result.stderr == ""


def test_python_m_wordfreq_json_output_has_trailing_newline() -> None:
    result = _run_module("--json", stdin="b a b\n")
    assert result.returncode == 0
    assert result.stdout.endswith("\n")
    assert not result.stdout.endswith("\n\n")
    assert json.loads(result.stdout) == [
        {"word": "b", "count": 2},
        {"word": "a", "count": 1},
    ]


def test_python_m_wordfreq_invalid_argument_exits_2() -> None:
    result = _run_module("--min-len", "0", stdin="hello\n")
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr != ""


def test_python_m_wordfreq_missing_file_exits_2(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    result = _run_module(str(missing))
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr != ""
