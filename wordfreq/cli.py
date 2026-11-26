"""Command-line entry point and word frequency helpers for wordfreq."""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from collections import Counter
from collections.abc import Sequence

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")


def count_words(
    text: str,
    *,
    min_len: int = 1,
    ignore_case: bool = True,
    top: int | None = None,
) -> list[tuple[str, int]]:
    """Count word occurrences in *text* and return `(word, count)` pairs."""
    if min_len < 1:
        msg = "min_len must be >= 1"
        raise ValueError(msg)
    if top is not None and top < 0:
        msg = "top must be >= 0"
        raise ValueError(msg)

    tokens = _TOKEN_PATTERN.findall(text)
    if ignore_case:
        tokens = [token.lower() for token in tokens]
    counts = Counter(token for token in tokens if len(token) >= min_len)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    if top is not None:
        ranked = ranked[:top]
    return ranked


def format_table(rows: Sequence[tuple[str, int]]) -> str:
    """Format `(word, count)` pairs as tab-separated lines."""
    return "\n".join(f"{word}\t{count}" for word, count in rows)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wordfreq",
        description="Deterministically count and rank words in text.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="file to read; reads stdin when omitted or '-'",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="show only the N most frequent words",
    )
    parser.add_argument(
        "--min-len",
        type=int,
        default=1,
        help="ignore words shorter than N characters (default: 1)",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="count 'Word' and 'word' as different words",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print results as a JSON array of {word, count} objects",
    )
    return parser


def _read_text(path: str | None) -> str:
    """Return the text of *path*, or of stdin when *path* is None or '-'."""
    if path is None or path == "-":
        if isinstance(sys.stdin, io.TextIOWrapper):
            sys.stdin.reconfigure(encoding="utf-8")
        return sys.stdin.read()
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def main(argv: Sequence[str] | None = None) -> int:
    """Run the wordfreq CLI and return the process exit code."""
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse has already written the usage/error message to stderr.
        return exc.code if isinstance(exc.code, int) else 2

    try:
        text = _read_text(args.path)
    except (OSError, UnicodeDecodeError) as exc:
        sys.stderr.write(
            f"wordfreq: error: cannot read {args.path or 'stdin'}: {exc}\n"
        )
        return 2

    try:
        rows = count_words(
            text,
            min_len=args.min_len,
            ignore_case=not args.case_sensitive,
            top=args.top,
        )
    except ValueError as exc:
        sys.stderr.write(f"wordfreq: error: {exc}\n")
        return 2

    if args.json:
        payload = [{"word": word, "count": count} for word, count in rows]
        sys.stdout.write(json.dumps(payload) + "\n")
    elif rows:
        sys.stdout.write(format_table(rows) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
