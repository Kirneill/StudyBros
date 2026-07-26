"""
Study material generator using provider-specific LLM APIs.
"""

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Literal, Type, TypeVar

from anthropic import Anthropic
from anthropic import APIStatusError as AnthropicAPIStatusError
from anthropic import AuthenticationError as AnthropicAuthenticationError
from openai import APIStatusError as OpenAIAPIStatusError
from openai import AuthenticationError as OpenAIAuthenticationError
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.shared_params import ResponseFormatJSONObject
from pydantic import BaseModel

from study_guide.config import config
from study_guide.generation.prompts import (
    SYSTEM_PROMPT,
    get_audio_summary_prompt,
    get_flashcard_prompt,
    get_practice_test_prompt,
    get_quiz_prompt,
)
from study_guide.generation.schemas import AudioSummary, FlashcardSet, PracticeTest, Quiz

GenerationProvider = Literal["openai", "anthropic", "openrouter", "codex"]
T = TypeVar("T", bound=BaseModel)

# stderr/stdout fragments that indicate a Codex login/auth problem rather than
# a transient failure. Matched case-insensitively. Kept tight so substrings like
# "authored by" do not misclassify unrelated failures as 401.
_CODEX_AUTH_PATTERNS = ("not logged in", "login", "unauthorized", "401", "authentication")

# Allowed characters for a codex `-m <model>` argument. Excludes shell/cmd.exe
# metacharacters (&, |, %, ", ^, <, >, spaces, /) because on Windows the resolved
# `codex.cmd` shim re-enters cmd.exe, which re-parses metacharacters that Python's
# argv quoting does not escape (BatBadBut / CVE-2024-1874 class). No real Codex
# model id needs anything outside this set. Note this is stricter than the
# API-level GenerateRequest.model pattern, which allows `/` for OpenRouter ids.
_CODEX_MODEL_PATTERN = re.compile(r"^[A-Za-z0-9._:-]+$")


class GenerationResult:
    """Result of a generation operation."""

    def __init__(
        self,
        content: BaseModel | None,
        success: bool,
        error: str | None = None,
        tokens_used: int = 0,
        model: str | None = None,
        status_code: int = 200,
    ):
        self.content = content
        self.success = success
        self.error = error
        self.tokens_used = tokens_used
        self.model = model
        self.status_code = status_code


class StudyMaterialGenerator:
    """Generates study materials using supported LLM providers."""

    def __init__(
        self,
        provider: GenerationProvider | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ):
        default_provider = config.GENERATION_PROVIDER.lower()
        if default_provider not in {"openai", "anthropic", "openrouter", "codex"}:
            default_provider = "openai"

        self.provider: GenerationProvider = provider or default_provider  # type: ignore[assignment]
        self.api_key = api_key
        self.model = model or config.get_generation_model(self.provider)
        self._openai_client: OpenAI | None = None
        self._anthropic_client: Anthropic | None = None

    def _resolve_api_key(self) -> str:
        """Resolve API key from request override or server config."""
        api_key = self.api_key or config.get_provider_api_key(self.provider)
        if not api_key:
            provider_label = self.provider.capitalize()
            raise ValueError(f"{provider_label} API key is not set")
        return api_key

    def _get_openai_client(self, *, base_url: str | None = None) -> OpenAI:
        """Get or create an OpenAI-compatible client."""
        if self._openai_client is None:
            self._openai_client = OpenAI(api_key=self._resolve_api_key(), base_url=base_url)
        return self._openai_client

    def _get_anthropic_client(self) -> Anthropic:
        """Get or create an Anthropic client."""
        if self._anthropic_client is None:
            self._anthropic_client = Anthropic(api_key=self._resolve_api_key())
        return self._anthropic_client

    def _build_json_prompt(self, prompt: str, schema: Type[T]) -> str:
        """Append strict JSON output requirements to a generation prompt."""
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        return (
            f"{prompt}\n\n"
            "Return only valid JSON. Do not add commentary, markdown, or code fences.\n"
            f"The JSON must validate against this schema:\n{schema_json}\n"
        )

    def _extract_json_text(self, raw_text: str) -> str:
        """Strip common markdown fences from provider output."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        return cleaned

    def _parse_structured_text(self, raw_text: str, schema: Type[T]) -> T:
        """Parse provider text output into a validated schema instance."""
        payload = json.loads(self._extract_json_text(raw_text))
        return schema.model_validate(payload)

    def _generate_with_openai_compatible(
        self,
        prompt: str,
        schema: Type[T],
        *,
        base_url: str | None = None,
    ) -> GenerationResult:
        """Generate structured JSON using an OpenAI-compatible API."""
        try:
            client = self._get_openai_client(base_url=base_url)
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": self._build_json_prompt(prompt, schema)},
            ]
            if self.provider == "openai":
                response_format: ResponseFormatJSONObject = {"type": "json_object"}
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=config.MAX_TOKENS_PER_RESPONSE,
                    response_format=response_format,
                )
            else:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=config.MAX_TOKENS_PER_RESPONSE,
                )
            raw_content = response.choices[0].message.content or ""
            parsed = self._parse_structured_text(raw_content, schema)
            tokens_used = response.usage.total_tokens if response.usage else 0

            return GenerationResult(
                content=parsed,
                success=True,
                tokens_used=tokens_used,
                model=self.model,
            )
        except OpenAIAuthenticationError as exc:
            return GenerationResult(
                content=None,
                success=False,
                error=str(exc),
                model=self.model,
                status_code=401,
            )
        except OpenAIAPIStatusError as exc:
            return GenerationResult(
                content=None,
                success=False,
                error=str(exc),
                model=self.model,
                status_code=exc.status_code or 502,
            )
        except Exception as exc:
            return GenerationResult(
                content=None,
                success=False,
                error=str(exc),
                model=self.model,
                status_code=502,
            )

    def _generate_with_anthropic(self, prompt: str, schema: Type[T]) -> GenerationResult:
        """Generate structured JSON using Anthropic."""
        try:
            client = self._get_anthropic_client()
            response = client.messages.create(
                model=self.model,
                max_tokens=config.MAX_TOKENS_PER_RESPONSE,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": self._build_json_prompt(prompt, schema),
                    }
                ],
            )
            text_blocks: list[str] = []
            for block in response.content:
                if getattr(block, "type", "") != "text":
                    continue
                text = getattr(block, "text", None)
                if isinstance(text, str):
                    text_blocks.append(text)
            raw_content = "".join(text_blocks)
            parsed = self._parse_structured_text(raw_content, schema)
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            return GenerationResult(
                content=parsed,
                success=True,
                tokens_used=tokens_used,
                model=self.model,
            )
        except AnthropicAuthenticationError as exc:
            return GenerationResult(
                content=None,
                success=False,
                error=str(exc),
                model=self.model,
                status_code=401,
            )
        except AnthropicAPIStatusError as exc:
            return GenerationResult(
                content=None,
                success=False,
                error=str(exc),
                model=self.model,
                status_code=exc.status_code or 502,
            )
        except Exception as exc:
            return GenerationResult(
                content=None,
                success=False,
                error=str(exc),
                model=self.model,
                status_code=502,
            )

    def _generate_with_codex(self, prompt: str, schema: Type[T]) -> GenerationResult:
        """
        Generate structured JSON by shelling out to the local Codex CLI.

        Uses the user's Codex (ChatGPT) login rather than an API key. The full
        prompt (system + schema-embedded user prompt) is piped via stdin — never
        passed as an argv element — because on Windows the `codex.cmd` shim routes
        through cmd.exe, which mangles shell metacharacters (%, &, |, <, >) and
        caps the command line at 32767 chars. The trailing `-` argv element tells
        `codex exec` to read the prompt from stdin.

        Note: `--output-schema` is intentionally NOT used. It enables OpenAI strict
        constrained decoding, which requires `additionalProperties: false` on every
        object in the schema; Pydantic's default JSON schema does not emit that, so
        even simple schemas are rejected with HTTP 400. Instead the schema text is
        embedded in the prompt (via `_build_json_prompt`) and the result is parsed
        and validated with Pydantic, matching the anthropic/openrouter text path.
        """
        model_for_result = self.model or "codex-default"

        # Reject metacharacter-laden model names BEFORE spawning any process, so a
        # malicious `-m` value can never reach the cmd.exe-backed codex.cmd shim.
        if self.model and not _CODEX_MODEL_PATTERN.match(self.model):
            return GenerationResult(
                content=None,
                success=False,
                error=(
                    "Invalid model name for Codex provider. Use only letters, "
                    "digits, and the characters . _ : -"
                ),
                model=model_for_result,
                status_code=400,
            )

        codex_path = shutil.which("codex")
        if codex_path is None:
            return GenerationResult(
                content=None,
                success=False,
                error=(
                    "Codex CLI not installed or not on PATH. Install it "
                    "(`npm i -g @openai/codex`) and run `codex login`."
                ),
                model=model_for_result,
                status_code=503,
            )

        full_prompt = f"{SYSTEM_PROMPT}\n\n{self._build_json_prompt(prompt, schema)}"

        with tempfile.TemporaryDirectory() as tmpdir:
            last_message_path = Path(tmpdir) / "last_message.txt"
            argv = [
                codex_path,
                "exec",
                "--skip-git-repo-check",
                "--ephemeral",
                "-s",
                "read-only",
                "--color",
                "never",
                "-o",
                str(last_message_path),
            ]
            if self.model:
                argv += ["-m", self.model]
            argv.append("-")

            try:
                result = subprocess.run(
                    argv,
                    input=full_prompt,
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=config.CODEX_TIMEOUT_SECONDS,
                )
            except FileNotFoundError:
                return GenerationResult(
                    content=None,
                    success=False,
                    error=(
                        "Codex CLI not installed or not on PATH. Install it "
                        "(`npm i -g @openai/codex`) and run `codex login`."
                    ),
                    model=model_for_result,
                    status_code=503,
                )
            except subprocess.TimeoutExpired:
                return GenerationResult(
                    content=None,
                    success=False,
                    error=(
                        f"Codex CLI timed out after {config.CODEX_TIMEOUT_SECONDS}s. "
                        "Increase STUDY_GUIDE_CODEX_TIMEOUT or reduce the item count."
                    ),
                    model=model_for_result,
                    status_code=504,
                )

            if result.returncode != 0:
                combined = f"{result.stderr or ''}\n{result.stdout or ''}"
                tail = combined.strip()[-500:]
                lowered = combined.lower()
                if any(pattern in lowered for pattern in _CODEX_AUTH_PATTERNS):
                    return GenerationResult(
                        content=None,
                        success=False,
                        error=(
                            "Codex CLI is not authenticated. Run `codex login` on the "
                            f"server. Details: {tail}"
                        ),
                        model=model_for_result,
                        status_code=401,
                    )
                return GenerationResult(
                    content=None,
                    success=False,
                    error=f"Codex CLI failed (exit {result.returncode}): {tail}",
                    model=model_for_result,
                    status_code=502,
                )

            try:
                raw_text = last_message_path.read_text(encoding="utf-8")
            except OSError as exc:
                return GenerationResult(
                    content=None,
                    success=False,
                    error=f"Codex CLI produced no output file: {exc}",
                    model=model_for_result,
                    status_code=502,
                )

            try:
                parsed = self._parse_structured_text(raw_text, schema)
            except Exception as exc:
                return GenerationResult(
                    content=None,
                    success=False,
                    error=f"Codex CLI returned unparseable output: {exc}",
                    model=model_for_result,
                    status_code=502,
                )

            return GenerationResult(
                content=parsed,
                success=True,
                tokens_used=0,
                model=model_for_result,
            )

    def _generate_structured(
        self,
        prompt: str,
        schema: Type[T],
    ) -> GenerationResult:
        """
        Generate structured output using the configured provider.

        Args:
            prompt: The user prompt
            schema: Pydantic schema for the response

        Returns:
            GenerationResult with parsed content
        """
        if self.provider == "anthropic":
            return self._generate_with_anthropic(prompt, schema)
        if self.provider == "openrouter":
            return self._generate_with_openai_compatible(
                prompt,
                schema,
                base_url="https://openrouter.ai/api/v1",
            )
        if self.provider == "codex":
            return self._generate_with_codex(prompt, schema)
        return self._generate_with_openai_compatible(prompt, schema)

    def generate_flashcards(
        self,
        content: str,
        count: int = 10,
    ) -> GenerationResult:
        """Generate flashcards from content."""
        prompt = get_flashcard_prompt(content, count)
        return self._generate_structured(prompt, FlashcardSet)

    def generate_quiz(
        self,
        content: str,
        count: int = 10,
    ) -> GenerationResult:
        """Generate a multiple choice quiz from content."""
        prompt = get_quiz_prompt(content, count)
        return self._generate_structured(prompt, Quiz)

    def generate_practice_test(
        self,
        content: str,
        count: int = 15,
    ) -> GenerationResult:
        """Generate a practice test with mixed question types."""
        prompt = get_practice_test_prompt(content, count)
        return self._generate_structured(prompt, PracticeTest)

    def generate_audio_summary(
        self,
        content: str,
        concept_count: int = 5,
        point_count: int = 7,
    ) -> GenerationResult:
        """Generate an audio-friendly summary suitable for TTS."""
        prompt = get_audio_summary_prompt(content, concept_count, point_count)
        return self._generate_structured(prompt, AudioSummary)

    def generate_from_chunks(
        self,
        chunks: list[str],
        generation_type: str,
        count: int = 10,
    ) -> GenerationResult:
        """
        Generate study materials from multiple chunks.

        Respects the MAX_CHUNKS_PER_GENERATION limit.
        """
        max_chunks = config.MAX_CHUNKS_PER_GENERATION
        if len(chunks) > max_chunks:
            chunks = chunks[:max_chunks]

        combined_content = "\n\n---\n\n".join(chunks)

        if generation_type == "flashcards":
            return self.generate_flashcards(combined_content, count)
        if generation_type == "quiz":
            return self.generate_quiz(combined_content, count)
        if generation_type == "practice_test":
            return self.generate_practice_test(combined_content, count)
        if generation_type == "audio_summary":
            return self.generate_audio_summary(combined_content, concept_count=5, point_count=count)
        return GenerationResult(
            content=None,
            success=False,
            error=f"Unknown generation type: {generation_type}",
            status_code=400,
        )
