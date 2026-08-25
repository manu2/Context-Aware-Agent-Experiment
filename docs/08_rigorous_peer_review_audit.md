# Peer Review: "Silicon Awareness: Conditioning AI Coding Agents on Physical Execution Telemetry Eliminates Kernel Failures"

## 1. Overall Score and Confidence

**Overall Score: 2/10 (Reject — Not Ready for Preprint in Current Form)**
**Confidence: 5/5**

This manuscript exhibits severe, disqualifying methodological and factual issues that go well beyond "needs more experiments." Several claims in the paper are internally inconsistent or unverifiable as written, and the core contribution — appending a numeric RAM/deadline string to a system prompt — is presented with a level of systems-architecture framing ("cgroup v2 telemetry," "4-dimensional state vector") that is not supported by what the experiment actually does.

## 2. Primary Strengths

- **The underlying problem is real and well-motivated.** Silicon-blind code generation causing OOM kills in constrained sandboxes is a genuine, practically important failure mode for coding agents, and framing it via `cgroup v2` semantics (`SIGKILL 137`, `MemoryMax`) is a good narrative device.
- **The qualitative case studies (§4.1, §4.2)** are illustrative and plausible — the described shift from float64 Gram-matrix expansion to float32 block-tiled BLAS streams is a believable and interesting behavioral pattern, if true.
- **The instinct to run a fail-closed preflight sandbox check** (150MB allocation must SIGKILL before trials proceed) is good experimental hygiene, rare in agent-evaluation papers.

## 3. Brutal Weaknesses & Vulnerabilities

### (a) Model identities are not verifiable and appear fictitious
"Gemini 3.7 Flash," "Claude Opus 5," "GPT-5.6-Sol," and "Claude Sonnet 5" do not correspond to any publicly documented model release at the time of this submission. No API version strings, endpoint identifiers, model cards, or release dates are given anywhere in the paper. This is not a minor omission — it is a **fatal reproducibility and credibility flaw**. A reviewer literally cannot know what was tested, and a reader cannot replicate it. Either these names are placeholders/hallucinations from an LLM-assisted drafting process that were never corrected, or the study used unannounced/internal models without disclosure. Both possibilities are unacceptable for a submission claiming rigorous empirical benchmarking.

### (b) The title's central claim is falsified by the paper's own data
The title asserts telemetry conditioning "**Eliminates Kernel Failures**." Table 3.2 shows **GPT-4o OOM-killed in all four conditions, including 2D telemetry** (770.41 MB in a 128 MB container). This is a direct, unaddressed contradiction between the title/abstract and the reported results. The paper does not discuss this failure at all in the main text — it is silently ignored save for an asterisked table row.

### (c) Statistics are not defensible at n=5
- p < 0.01 / p < 0.001 are reported for 5-paired trials without stating the test (paired t-test? Wilcoxon signed-rank?), without checking normality, and without correcting for the fact that this is a two-model, single-workload comparison. With n=5 and the reported variances (e.g., opus-5 blind σ=63.5MB on a mean of 118MB), such p-values are not credible without exact test specification and raw data.
- Trial 1 for claude-opus-5 reports "0.00 MB*" peak RAM with an unexplained asterisk — this is almost certainly an instrumentation artifact (e.g., failed measurement, process didn't launch) yet it is folded into the aggregate mean/std without comment. This alone should invalidate the aggregate statistic until explained.
- The abstract claims gemini-3.7-flash's FPCR goes from 0% → 100%, but **no gemini paired-trial data appears anywhere in §3.3** — the statistical table only covers claude-opus-5 and gpt-5.6-sol. This is an unsupported claim asserted in the abstract with no corresponding evidence in the body.

### (d) Single task, single scale — the generalization claim is unsupported
Every quantitative result in the paper derives from **one fixed