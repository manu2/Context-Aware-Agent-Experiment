"""Fail-closed direct provider backends used by empirical trajectories."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

from .generation import extract_python
from .models import GenerationRecord


class ProviderRequestError(RuntimeError):
    """Provider-level HTTP failure: no model generation was obtained."""

    def __init__(self, status_code: int, message: str, retry_after: str | None = None) -> None:
        super().__init__(f"provider HTTP {status_code}: {message}")
        self.status_code = status_code
        self.retry_after = retry_after


class BudgetLedger:
    def __init__(self, path: Path, hard_cap_usd: float, max_calls: int) -> None:
        self.path = path
        self.hard_cap_usd = hard_cap_usd
        self.max_calls = max_calls

    def _read(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {"schema_version": "api-budget-ledger/v0.1", "calls": 0, "estimated_cost_usd": 0.0, "entries": []}

    def begin(self, projected_call_usd: float, metadata: dict) -> int:
        ledger = self._read()
        if ledger["calls"] >= self.max_calls:
            raise RuntimeError("API call cap reached")
        if ledger["estimated_cost_usd"] + projected_call_usd > self.hard_cap_usd:
            raise RuntimeError("API cost cap would be exceeded")
        ledger["calls"] += 1
        ledger["estimated_cost_usd"] += projected_call_usd
        ledger["entries"].append({**metadata, "status": "started", "reserved_cost_usd": projected_call_usd})
        self._write(ledger)
        return len(ledger["entries"]) - 1

    def settle(self, index: int, entry: dict) -> None:
        ledger = self._read()
        reserved = ledger["entries"][index]["reserved_cost_usd"]
        ledger["estimated_cost_usd"] += entry["estimated_cost_usd"] - reserved
        ledger["entries"][index] = {**entry, "status": "complete", "reserved_cost_usd": reserved}
        self._write(ledger)

    def fail(self, index: int, error: Exception) -> None:
        ledger = self._read()
        current = ledger["entries"][index]
        if current["status"] != "started":
            raise RuntimeError("only an active reservation can fail")
        reserved = current["reserved_cost_usd"]
        ledger["estimated_cost_usd"] -= reserved
        ledger["entries"][index] = {
            **current, "status": "failed", "error_type": type(error).__name__,
            "error": str(error), "estimated_cost_usd": 0.0,
        }
        self._write(ledger)

    def _write(self, ledger: dict) -> None:
        temp = self.path.with_suffix(".tmp")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
        temp.replace(self.path)


def _json_request(endpoint: str, body: dict, headers: dict[str, str], timeout: int = 300) -> tuple[dict, str | None, float]:
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw_bytes = response.read()
            request_id = response.headers.get("request-id") or response.headers.get("x-request-id") or response.headers.get("x-goog-request-id")
    except urllib.error.HTTPError as exc:
        body = exc.read(4000).decode("utf-8", errors="replace").strip()
        raise ProviderRequestError(exc.code, body or exc.reason, exc.headers.get("retry-after")) from exc
    return json.loads(raw_bytes.decode("utf-8")), request_id, time.monotonic() - started


def _prompt_token_projection(prompt: str) -> int:
    """Conservative provider-neutral estimate used only for pre-call budget reservation."""
    return max(1, (len(prompt) + 2) // 3)


@dataclass
class GeminiDirectAPIBackend:
    api_key: str
    ledger: BudgetLedger
    model: str = "gemini-3.8-flash"
    temperature: float | None = None
    top_p: float | None = None
    thinking_level: str | None = "medium"
    max_output_tokens: int = 4096
    development_only: bool = False

    def __post_init__(self) -> None:
        if self.model == "gemini-3.8-flash" and (self.temperature is not None or self.top_p is not None):
            raise ValueError("Gemini 3.8 Flash must not receive deprecated sampling parameters")
        if self.thinking_level not in {None, "low", "medium", "high"}:
            raise ValueError("unsupported Gemini thinking level")

    def generation_config(self) -> dict:
        config: dict = {"maxOutputTokens": self.max_output_tokens}
        if self.temperature is not None:
            config["temperature"] = self.temperature
        if self.top_p is not None:
            config["topP"] = self.top_p
        if self.thinking_level is not None:
            config["thinkingConfig"] = {"thinkingLevel": self.thinking_level}
        return config

    def generate(self, prompt: str) -> GenerationRecord:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        projected = (len(prompt) / 4 * 0.75 + self.max_output_tokens * 3.75) / 1_000_000
        prompt_hash = sha256(prompt.encode()).hexdigest()
        ledger_index = self.ledger.begin(projected, {"provider": "google", "model": self.model,
                                                      "prompt_sha256": prompt_hash})
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": self.generation_config()}
        try:
            payload, request_id, elapsed = _json_request(
                endpoint, body, {"x-goog-api-key": self.api_key}, timeout=300
            )
        except ProviderRequestError as exc:
            self.ledger.fail(ledger_index, exc)
            raise
        candidates = payload.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned no candidate")
        text = "".join(part.get("text", "") for part in candidates[0].get("content", {}).get("parts", []))
        if not text:
            raise RuntimeError(f"Gemini returned no text (finishReason={candidates[0].get('finishReason')})")
        usage = payload.get("usageMetadata", {})
        input_tokens = int(usage.get("promptTokenCount", 0))
        total_tokens = int(usage.get("totalTokenCount", input_tokens))
        output_tokens = max(0, total_tokens - input_tokens)
        cost = (input_tokens * 0.75 + output_tokens * 3.75) / 1_000_000
        entry = {"provider": "google", "model": self.model, "input_tokens": input_tokens,
                 "output_tokens_including_thoughts": output_tokens, "estimated_cost_usd": cost,
                 "candidate_tokens": int(usage.get("candidatesTokenCount", 0)),
                 "thinking_tokens": int(usage.get("thoughtsTokenCount", 0)),
                 "finish_reason": candidates[0].get("finishReason"),
                 "request_id": request_id, "prompt_sha256": prompt_hash}
        self.ledger.settle(ledger_index, entry)
        return GenerationRecord(
            backend="google-generative-language/v1beta", model=self.model,
            raw_response=text, extracted_program=extract_python(text),
            request_metadata={**entry, "generation_seconds": elapsed,
                              "development_only": self.development_only,
                              "generation_config": self.generation_config()},
            raw_provider_payload=json.dumps(payload, indent=2, sort_keys=True),
        )


@dataclass
class OpenAIResponsesBackend:
    api_key: str
    ledger: BudgetLedger
    model: str = "gpt-5.6-sol"
    reasoning_effort: str = "medium"
    max_output_tokens: int = 32768
    development_only: bool = False
    input_usd_per_million: float = 4.0
    cached_input_usd_per_million: float = 0.4
    output_usd_per_million: float = 20.0

    def __post_init__(self) -> None:
        if self.reasoning_effort not in {"none", "low", "medium", "high", "xhigh", "max"}:
            raise ValueError("unsupported OpenAI reasoning effort")

    def request_body(self, prompt: str) -> dict:
        return {
            "model": self.model,
            "input": prompt,
            "reasoning": {"effort": self.reasoning_effort},
            "max_output_tokens": self.max_output_tokens,
            "store": False,
            "service_tier": "default",
        }

    def generate(self, prompt: str) -> GenerationRecord:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        projected = (
            _prompt_token_projection(prompt) * self.input_usd_per_million
            + self.max_output_tokens * self.output_usd_per_million
        ) / 1_000_000
        prompt_hash = sha256(prompt.encode()).hexdigest()
        ledger_index = self.ledger.begin(projected, {
            "provider": "openai", "model": self.model, "prompt_sha256": prompt_hash,
        })
        try:
            payload, request_id, elapsed = _json_request(
                "https://api.openai.com/v1/responses",
                self.request_body(prompt),
                {"Authorization": f"Bearer {self.api_key}"},
            )
        except ProviderRequestError as exc:
            self.ledger.fail(ledger_index, exc)
            raise
        texts = []
        for item in payload.get("output", []):
            if item.get("type") != "message":
                continue
            texts.extend(part.get("text", "") for part in item.get("content", []) if part.get("type") == "output_text")
        response_text = "".join(texts)
        if not response_text:
            raise RuntimeError(f"OpenAI returned no output text (status={payload.get('status')})")
        usage = payload.get("usage", {})
        input_tokens = int(usage.get("input_tokens", 0))
        cached_tokens = int(usage.get("input_tokens_details", {}).get("cached_tokens", 0))
        output_tokens = int(usage.get("output_tokens", 0))
        uncached_tokens = max(0, input_tokens - cached_tokens)
        cost = (
            uncached_tokens * self.input_usd_per_million
            + cached_tokens * self.cached_input_usd_per_million
            + output_tokens * self.output_usd_per_million
        ) / 1_000_000
        entry = {
            "provider": "openai", "model": self.model, "input_tokens": input_tokens,
            "cached_input_tokens": cached_tokens, "output_tokens_including_reasoning": output_tokens,
            "reasoning_tokens": int(usage.get("output_tokens_details", {}).get("reasoning_tokens", 0)),
            "estimated_cost_usd": cost, "status_code": payload.get("status"),
            "incomplete_reason": payload.get("incomplete_details"), "request_id": request_id,
            "prompt_sha256": prompt_hash,
        }
        self.ledger.settle(ledger_index, entry)
        return GenerationRecord(
            backend="openai-responses/v1", model=self.model, raw_response=response_text,
            extracted_program=extract_python(response_text),
            request_metadata={**entry, "generation_seconds": elapsed,
                              "development_only": self.development_only,
                              "reasoning_effort": self.reasoning_effort,
                              "max_output_tokens": self.max_output_tokens},
            raw_provider_payload=json.dumps(payload, indent=2, sort_keys=True),
        )


@dataclass
class AnthropicMessagesBackend:
    api_key: str
    ledger: BudgetLedger
    model: str = "claude-sonnet-5"
    effort: str = "medium"
    max_tokens: int = 32768
    development_only: bool = False
    input_usd_per_million: float = 2.0
    output_usd_per_million: float = 10.0

    def __post_init__(self) -> None:
        if self.effort not in {"low", "medium", "high", "xhigh", "max"}:
            raise ValueError("unsupported Anthropic effort")

    def request_body(self, prompt: str) -> dict:
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": self.effort},
            "messages": [{"role": "user", "content": prompt}],
        }

    def generate(self, prompt: str) -> GenerationRecord:
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        projected = (
            _prompt_token_projection(prompt) * self.input_usd_per_million
            + self.max_tokens * self.output_usd_per_million
        ) / 1_000_000
        prompt_hash = sha256(prompt.encode()).hexdigest()
        ledger_index = self.ledger.begin(projected, {
            "provider": "anthropic", "model": self.model, "prompt_sha256": prompt_hash,
        })
        try:
            payload, request_id, elapsed = _json_request(
                "https://api.anthropic.com/v1/messages",
                self.request_body(prompt),
                {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
            )
        except ProviderRequestError as exc:
            self.ledger.fail(ledger_index, exc)
            raise
        response_text = "".join(block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text")
        if not response_text:
            raise RuntimeError(f"Anthropic returned no text (stop_reason={payload.get('stop_reason')})")
        usage = payload.get("usage", {})
        input_tokens = int(usage.get("input_tokens", 0))
        output_tokens = int(usage.get("output_tokens", 0))
        cost = (input_tokens * self.input_usd_per_million + output_tokens * self.output_usd_per_million) / 1_000_000
        entry = {
            "provider": "anthropic", "model": self.model, "input_tokens": input_tokens,
            "output_tokens_including_thinking": output_tokens, "estimated_cost_usd": cost,
            "stop_reason": payload.get("stop_reason"), "request_id": request_id,
            "prompt_sha256": prompt_hash,
        }
        self.ledger.settle(ledger_index, entry)
        return GenerationRecord(
            backend="anthropic-messages/v1", model=self.model, raw_response=response_text,
            extracted_program=extract_python(response_text),
            request_metadata={**entry, "generation_seconds": elapsed,
                              "development_only": self.development_only,
                              "effort": self.effort, "thinking": "adaptive",
                              "max_tokens": self.max_tokens},
            raw_provider_payload=json.dumps(payload, indent=2, sort_keys=True),
        )


def load_dotenv(path: Path) -> None:
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
