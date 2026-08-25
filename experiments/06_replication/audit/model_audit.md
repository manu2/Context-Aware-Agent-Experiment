# Model Identifier & Interface Audit

**Date:** August 2026  
**Artifact Scope:** Audit of evaluated model identifiers, API interfaces, sampling parameters, and replication availability.  

---

## 1. Audited Models in Historical Experiments

| Model Name (Manuscript) | Exact API Model Identifier | Provider / API Gateway | Historical Sampling Parameters | Availability & Replication Notes |
|---|---|---|---|---|
| **Anthropic Claude Opus 5** | `claude-opus-5` | Anthropic Messages API (`https://api.anthropic.com/v1/messages`) | `max_tokens: 8192`, `temperature: 0.1` | **Replication Limitation**: `claude-opus-5` is an exploratory/frontier research alias. In public commercial API, Anthropic provides `claude-3-opus-20240229` and `claude-3-7-sonnet-20250219`. |
| **OpenAI GPT-5.6-Sol** | `gpt-5.6-sol` | OpenAI Chat Completions API (`https://api.openai.com/v1/chat/completions`) | `temperature: default (1.0)` | **Replication Limitation**: `gpt-5.6-sol` is an exploratory model identifier. In public commercial API, OpenAI provides `gpt-4o`, `o1`, and `o3-mini`. |
| **Google Gemini 3.7 Flash** | `gemini-3.7-flash` (or `gemini-2.5-flash`) | Vertex AI / Google AI Studio API (`generateContent`) | `temperature: 0.1` | **Replication Limitation**: Commercial Vertex AI endpoints currently host `gemini-2.0-flash` and `gemini-1.5-pro`. |
| **OpenAI GPT-4o (Legacy)** | `gpt-4o` | OpenAI Chat Completions API | `temperature: 0.1` | Publicly available. |
| **Anthropic Claude Sonnet 5** | `claude-sonnet-5` | Anthropic Messages API | `temperature: 0.1` | Frontier alias. Public equivalent is `claude-3-7-sonnet-20250219`. |

---

## 2. Replication Model Set Freeze & Policy

For the frozen replication protocol:
1. **Zero Silent Substitution**: We will not substitute model identifiers without explicit documentation.
2. **Documented Replication Baseline**: When executing live API calls, the exact string passed to the API gateway (e.g. `model="claude-opus-5"`, `model="gpt-5.6-sol"`, `model="gemini-3.7-flash"`, or fallback to authorized API endpoints) must be immutably recorded in `RUN_MANIFEST.json` and in every run's `metadata.json`.
3. **Manuscript Transparency**: The manuscript Section 5.2 explicitly notes that evaluations were performed on frozen model snapshots.
