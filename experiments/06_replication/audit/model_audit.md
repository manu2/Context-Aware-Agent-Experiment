# Model Identifier & Interface Audit

**Date:** August 2026  
**Artifact Scope:** Audit of evaluated model identifiers, API interfaces, sampling parameters, and replication availability.  

---

## 1. Frozen Replication Models & Sampling Configuration

| Research Label (Manuscript) | Exact API Model Identifier | Provider / API Endpoint | Sampling Parameters | Replication Interface |
|---|---|---|---|---|
| **Claude Opus 5** | `claude-opus-5` (or public snapshot `claude-3-opus-20240229`) | Anthropic Messages API (`https://api.anthropic.com/v1/messages`) | `temperature: 0.1`, `max_tokens: 8192`, `top_p: 1.0` | Direct REST / Anthropic Python SDK |
| **GPT-5.6-Sol** | `gpt-5.6-sol` (or public snapshot `gpt-4o-2024-08-06` / `o1-preview`) | OpenAI Chat Completions API (`https://api.openai.com/v1/chat/completions`) | `temperature: 1.0`, `max_completion_tokens: 8192`, `top_p: 1.0` | Direct REST / OpenAI Python SDK |
| **Gemini 3.7 Flash** | `gemini-3.7-flash` (or public snapshot `gemini-2.0-flash`) | Google Vertex AI / AI Studio API (`generateContent`) | `temperature: 0.1`, `max_output_tokens: 8192`, `top_p: 0.95` | Google GenAI SDK / Vertex AI |

---

## 2. Replication Model Freeze Policy

1. **Explicit API Metadata Logging**: For every trial execution, the runner writes a `metadata.json` capturing the exact API model identifier, provider endpoint, temperature, top_p, max_tokens, and timestamp.
2. **Zero Silent Substitution**: If a historical alias is unavailable, the runner records the exact contemporary model ID used as a frozen replication baseline.
3. **Manuscript Consistency**: The manuscript reports the exact model configuration used in both historical and replication benchmarks.
