"""
Tests for the Codex CLI generation provider.

All tests mock `shutil.which` and `subprocess.run` so no real `codex exec`
process is ever spawned. The success path's fake `subprocess.run` writes valid
JSON to the `-o` output file the generator reads back.
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from study_guide.generation.generator import StudyMaterialGenerator
from study_guide.generation.schemas import FlashcardSet

_FAKE_CODEX = "/fake/path/codex"

_VALID_FLASHCARDS = {
    "cards": [
        {
            "question": "What is evaporation?",
            "answer": "Liquid water turning into vapor.",
            "tags": ["water cycle"],
            "difficulty": "easy",
        }
    ]
}


def _output_path_from_argv(argv: list[str]) -> str:
    """Return the value following the -o flag in a codex argv list."""
    return argv[argv.index("-o") + 1]


def _make_generator() -> StudyMaterialGenerator:
    return StudyMaterialGenerator(provider="codex")


def test_codex_success_parses_output_file():
    """Exit 0 with valid JSON in the -o file yields a parsed FlashcardSet."""

    def fake_run(argv, **kwargs):
        Path(_output_path_from_argv(argv)).write_text(
            json.dumps(_VALID_FLASHCARDS), encoding="utf-8"
        )
        return subprocess.CompletedProcess(argv, 0, stdout="tokens used\n21116", stderr="")

    with patch(
        "study_guide.generation.generator.shutil.which", return_value=_FAKE_CODEX
    ), patch("study_guide.generation.generator.subprocess.run", side_effect=fake_run):
        result = _make_generator().generate_flashcards("some content", count=1)

    assert result.success is True
    assert result.status_code == 200
    assert result.tokens_used == 0
    assert result.model == "codex-default"
    assert isinstance(result.content, FlashcardSet)
    assert result.content.cards[0].question == "What is evaporation?"


def test_codex_prompt_piped_via_stdin_not_argv():
    """The prompt must be sent as stdin input, and argv must end with '-'."""
    captured: dict[str, object] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["input"] = kwargs.get("input")
        Path(_output_path_from_argv(argv)).write_text(
            json.dumps(_VALID_FLASHCARDS), encoding="utf-8"
        )
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    with patch(
        "study_guide.generation.generator.shutil.which", return_value=_FAKE_CODEX
    ), patch("study_guide.generation.generator.subprocess.run", side_effect=fake_run):
        _make_generator().generate_flashcards("content about the water cycle", count=1)

    argv = captured["argv"]
    assert isinstance(argv, list)
    assert argv[0] == _FAKE_CODEX
    assert argv[-1] == "-", "codex must read the prompt from stdin (trailing '-')"
    assert "--output-schema" not in argv, "output-schema is intentionally omitted"
    # The prompt content lives in stdin, never in argv.
    assert isinstance(captured["input"], str)
    assert "water cycle" in captured["input"]
    assert not any("water cycle" in str(token) for token in argv)


def test_codex_model_flag_only_when_model_set():
    """An explicit model adds -m and is reported; default omits -m."""
    captured: dict[str, object] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        Path(_output_path_from_argv(argv)).write_text(
            json.dumps(_VALID_FLASHCARDS), encoding="utf-8"
        )
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    with patch(
        "study_guide.generation.generator.shutil.which", return_value=_FAKE_CODEX
    ), patch("study_guide.generation.generator.subprocess.run", side_effect=fake_run):
        gen = StudyMaterialGenerator(provider="codex", model="gpt-5.6-sol")
        result = gen.generate_flashcards("content", count=1)

    argv = captured["argv"]
    assert isinstance(argv, list)
    assert "-m" in argv
    assert argv[argv.index("-m") + 1] == "gpt-5.6-sol"
    assert result.model == "gpt-5.6-sol"


def test_codex_cli_missing_returns_503():
    """No codex on PATH yields an actionable 503 error."""
    with patch("study_guide.generation.generator.shutil.which", return_value=None):
        result = _make_generator().generate_flashcards("content", count=1)

    assert result.success is False
    assert result.status_code == 503
    assert result.error is not None
    assert "not installed" in result.error.lower() or "not on path" in result.error.lower()


def test_codex_timeout_returns_504():
    """A subprocess timeout maps to 504 and includes the timeout value."""

    def fake_run(argv, **kwargs):
        raise subprocess.TimeoutExpired(cmd=argv, timeout=300)

    with patch(
        "study_guide.generation.generator.shutil.which", return_value=_FAKE_CODEX
    ), patch("study_guide.generation.generator.subprocess.run", side_effect=fake_run):
        result = _make_generator().generate_flashcards("content", count=1)

    assert result.success is False
    assert result.status_code == 504
    assert result.error is not None
    assert "300" in result.error


def test_codex_nonzero_exit_returns_502():
    """A generic nonzero exit (no auth markers) maps to 502 with stderr tail."""

    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(
            argv, 1, stdout="", stderr="some internal failure occurred"
        )

    with patch(
        "study_guide.generation.generator.shutil.which", return_value=_FAKE_CODEX
    ), patch("study_guide.generation.generator.subprocess.run", side_effect=fake_run):
        result = _make_generator().generate_flashcards("content", count=1)

    assert result.success is False
    assert result.status_code == 502
    assert result.error is not None
    assert "some internal failure occurred" in result.error


def test_codex_auth_pattern_stderr_returns_401():
    """Auth-shaped stderr maps to 401 so the frontend can fall back."""

    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(
            argv, 1, stdout="", stderr="Error: 401 Unauthorized - please login"
        )

    with patch(
        "study_guide.generation.generator.shutil.which", return_value=_FAKE_CODEX
    ), patch("study_guide.generation.generator.subprocess.run", side_effect=fake_run):
        result = _make_generator().generate_flashcards("content", count=1)

    assert result.success is False
    assert result.status_code == 401
    assert result.error is not None
    assert "codex login" in result.error.lower()


def test_codex_rejects_metacharacter_model_without_spawning():
    """A model with cmd.exe metacharacters is rejected 400 before any subprocess."""
    with patch(
        "study_guide.generation.generator.shutil.which", return_value=_FAKE_CODEX
    ), patch("study_guide.generation.generator.subprocess.run") as mock_run:
        gen = StudyMaterialGenerator(provider="codex", model='x" & calc & "')
        result = gen.generate_flashcards("content", count=1)

    assert result.success is False
    assert result.status_code == 400
    assert result.error is not None
    assert "invalid model name" in result.error.lower()
    mock_run.assert_not_called()


def test_codex_accepts_legit_model_passes_to_flag():
    """A legitimate model id passes validation and reaches the -m flag."""
    captured: dict[str, object] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        Path(_output_path_from_argv(argv)).write_text(
            json.dumps(_VALID_FLASHCARDS), encoding="utf-8"
        )
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    with patch(
        "study_guide.generation.generator.shutil.which", return_value=_FAKE_CODEX
    ), patch("study_guide.generation.generator.subprocess.run", side_effect=fake_run):
        gen = StudyMaterialGenerator(provider="codex", model="gpt-5.6-terra")
        result = gen.generate_flashcards("content", count=1)

    argv = captured["argv"]
    assert isinstance(argv, list)
    assert argv[argv.index("-m") + 1] == "gpt-5.6-terra"
    assert result.success is True
    assert result.model == "gpt-5.6-terra"


def test_codex_auth_substring_in_word_maps_to_502_not_401():
    """stderr like 'authored by' must NOT be misread as an auth error."""

    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(
            argv, 1, stdout="", stderr="crash in module authored by acme"
        )

    with patch(
        "study_guide.generation.generator.shutil.which", return_value=_FAKE_CODEX
    ), patch("study_guide.generation.generator.subprocess.run", side_effect=fake_run):
        result = _make_generator().generate_flashcards("content", count=1)

    assert result.success is False
    assert result.status_code == 502


def test_codex_invalid_json_returns_502():
    """Exit 0 but unparseable output maps to 502."""

    def fake_run(argv, **kwargs):
        Path(_output_path_from_argv(argv)).write_text(
            "this is not json at all", encoding="utf-8"
        )
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    with patch(
        "study_guide.generation.generator.shutil.which", return_value=_FAKE_CODEX
    ), patch("study_guide.generation.generator.subprocess.run", side_effect=fake_run):
        result = _make_generator().generate_flashcards("content", count=1)

    assert result.success is False
    assert result.status_code == 502
    assert result.error is not None
    assert "unparseable" in result.error.lower()
