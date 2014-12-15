import os
import subprocess
import sys
from pathlib import Path

import pytest

from backintheday import __version__
from backintheday.cli import main

from conftest import EXPECTED_COMMITS, NEWEST_FIRST, SampleRepo


def _positions(text: str, subjects: tuple[str, ...]) -> list[int]:
    return [text.index(subject) for subject in subjects]


def test_history_prints_aligned_table(sample_repo: SampleRepo, capsys) -> None:
    code = main(["history", str(sample_repo.path)])
    out = capsys.readouterr().out

    assert code == 0
    assert "COMMIT" in out and "AUTHOR" in out and "SUBJECT" in out
    assert "Alice <alice@example.com>" in out
    subjects = tuple(spec.subject for spec in NEWEST_FIRST)
    assert _positions(out, subjects) == sorted(_positions(out, subjects))


def test_history_honours_limit(sample_repo: SampleRepo, capsys) -> None:
    code = main(["history", str(sample_repo.path), "-n", "1"])
    out = capsys.readouterr().out

    assert code == 0
    assert NEWEST_FIRST[0].subject in out
    assert EXPECTED_COMMITS[0].subject not in out
    assert EXPECTED_COMMITS[1].subject not in out


def test_history_defaults_to_current_directory(
    sample_repo: SampleRepo, capsys, monkeypatch
) -> None:
    monkeypatch.chdir(sample_repo.path)
    code = main(["history"])
    out = capsys.readouterr().out

    assert code == 0
    assert all(spec.subject in out for spec in EXPECTED_COMMITS)


def test_empty_repository_prints_notice(empty_repo: Path, capsys) -> None:
    code = main(["history", str(empty_repo)])
    out = capsys.readouterr().out

    assert code == 0
    assert "No commits found." in out


def test_invalid_limit_reports_error(sample_repo: SampleRepo, capsys) -> None:
    code = main(["history", str(sample_repo.path), "--limit", "0"])
    captured = capsys.readouterr()

    assert code == 1
    assert captured.out == ""
    assert "error:" in captured.err
    assert "limit" in captured.err


def test_directory_without_repository_reports_error(tmp_path: Path, capsys) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    code = main(["history", str(plain)])
    captured = capsys.readouterr()

    assert code == 1
    assert captured.out == ""
    assert "error:" in captured.err
    assert "not a git repository" in captured.err


def test_no_arguments_prints_help(capsys) -> None:
    code = main([])
    out = capsys.readouterr().out

    assert code == 0
    assert "usage:" in out
    assert "history" in out


def test_version_prints_package_version(capsys) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])

    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_history_exits_cleanly_when_pipe_closes_early(sample_repo: SampleRepo) -> None:
    """`backintheday history | head` must not end in "Exception ignored" noise."""
    src = Path(__file__).resolve().parent.parent / "src"
    process = subprocess.Popen(
        [sys.executable, "-m", "backintheday", "history", str(sample_repo.path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONPATH": str(src)},
    )
    assert process.stdout is not None
    process.stdout.close()  # the reader disappears before the CLI writes its table
    process.wait(timeout=60)
    stderr = process.stderr.read()
    process.stderr.close()

    # Clean exit with a failure status: no traceback, no shutdown-flush noise.
    assert process.returncode == 1
    assert stderr == b""
