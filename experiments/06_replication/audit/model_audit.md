# Model Identifier & Interface Audit

**Date:** August 2026  
**Artifact Scope:** Audit of evaluated frontier model identifiers, API interfaces, sampling parameters, and replication availability.  

---

## 1. Frozen Frontier Replication Models & Sampling Configuration

| Research Label (Manuscript) | Exact Frozen API Model Identifier | Provider / API Endpoint | Sampling Parameters | Replication Interface |
|---|---|---|---|---|
| **Claude Opus 5** | `claude-opus-5` | Anthropic Messages API (`https://api.anthropic.com/v1/messages`) | Provider-default sampling; `max_tokens: 8192` | Direct REST / Anthropic Messages API |
| **GPT-5.6-Sol** | `gpt-5.6-sol` | OpenAI Chat Completions API (`https://api.openai.com/v1/chat/completions`) | `temperature: 1.0`, `max_completion_tokens: 8192`, `top_p: 1.0` | Direct REST / OpenAI Chat Completions API |
| **Gemini 3.7 Flash** | `gemini-3.7-flash` | Google AI Studio API (`generateContent`) | `temperature: 0.1`, `max_output_tokens: 8192`, `top_p: 0.95` | Direct REST / Google AI Studio API |

---

## 2. Replication Model Freeze Policy

1. **Explicit API Metadata Logging**: For every trial execution, the runner writes a `metadata.json` capturing the exact frontier API model identifier, provider endpoint, all applicable sampling controls, output-token cap, and timestamp. Claude Opus 5 uses provider-default sampling because its API rejects explicit `temperature` or `top_p`; this applies equally to both members of every Claude pair.
2. **Zero Silent Substitution**: All replication trials strictly target the state-of-the-art frontier models (`gemini-3.7-flash`, `gpt-5.6-sol`, `claude-opus-5`).
3. **Manuscript Consistency**: The manuscript and replication harness are 100% aligned on frontier model definitions.
