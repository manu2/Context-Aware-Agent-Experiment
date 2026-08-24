# PROJECT AETHER-BUS / SCAC: GCP EXECUTION TRACKER

**Project:** Substrate & Self-Telemetry Conditioned Agentic Computation (SST-SCAC)  
**Target Deployment:** Google Compute Engine (GCE)  
**Host VM Spec:** Ubuntu 24.04 LTS (Kernel 6.8+, unified cgroup v2 active) | `e2-medium` (2 vCPU / 4GB RAM)  
**Model Under Test:** `gemini-3.7-flash` (via Google Generative Language v1beta API)  
**Sandbox Ceiling:** 128 MB RAM (`MemoryMax=128M`, `MemorySwapMax=0`)  

---

## 1. Live Deployment & Execution Checklist

| Stage | Action / Step | Target / Command | Status | Notes / Output |
|---|---|---|---|---|
| **0.1** | Host Admin & gcloud Python Config | `CLOUDSDK_PYTHON=~/.local/share/uv/python/.../python3.12` | ✅ **DONE** | Installed Python 3.12 via `uv`; gcloud 581.0.0 verified |
| **0.2** | GCP Account & Project Setup | `project-a9fc9225-58b8-41d1-bac` | ✅ **DONE** | GCP Project configured & gcloud added to `~/.zshrc` |
| **0.3** | API Key Provisioning | `gemini-3.6-flash` (Free Tier) | ✅ **DONE** | Key authenticated & gemini-3.6-flash verified |
| **1.0** | Provision GCE VM (`scac-foil-node`) | `gcloud compute instances create scac-foil-node ...` | ✅ **DONE** | Ubuntu 24.04 LTS e2-medium VM created |
| **2.0** | Transfer Codebase | `gcloud compute scp week1_foil_test.py scac-foil-node:~` | ✅ **DONE** | Harness uploaded to GCE |
| **3.0** | Remote VM Dependency Prep | `sudo apt install python3-numpy python3-pandas` | ✅ **DONE** | Environment dependencies installed |
| **4.0** | Execute 10 Paired Trials (20 Runs) | `python3 week1_foil_test.py` | ✅ **DONE** | Executed 10 Paired Trials (20 runs) under 128MB ceiling |
| **5.0** | Retrieve Artifacts (`/foil_runs/`) | `gcloud compute scp --recurse scac-foil-node:~/foil_runs ./` | ✅ **DONE** | 20 Python trial script artifacts fetched locally |
| **6.0** | Destroy Phase 1 VM Instance | `gcloud compute instances delete scac-foil-node --quiet` | ✅ **DONE** | VM deleted; zero lingering cloud cost |
| **7.0** | Vertex AI Billing & Quota Setup | `gcloud services enable aiplatform.googleapis.com` | ✅ **DONE** | Unlimited pay-as-you-go Vertex AI quota active on project |
| **8.0** | Phase 2 Single-Trial Verification | `systemd-run -p MemoryMax=128M ...` | ✅ **DONE** | Verified Exit 137 SIGKILL OOM vs Exit 0 32.03MB Success |
| **9.0** | Phase 2 10-Trial Benchmark | `gcloud compute instances delete scac-matrix-node` | ✅ **DONE** | 10 Trials completed, results retrieved, node torn down |
| **10.0** | Local Prompt Ablation & Sensitivity Study | `python3 local_experiments/prompt_ablation_study/reproduce_ablation_study.py` | ✅ **DONE** | Tested 4 Prompt Variants (Blind vs 128M vs 2GB vs 2D 128M+10s) |
| **11.0** | Natural Language vs Quantitative Telemetry | `test_prompt_variants_locally.py` | ✅ **DONE** | NL advice ("be memory efficient") → timeout; Explicit telemetry → Pareto-optimal 2D block tiling |
| **12.0** | Peer Review Simulation & Paper Strategy | `run_peer_reviewer.py` + `paper_draft.md` | ✅ **DONE** | Simulated Senior Area Chair review scored 6/10; Roadmap to 8.5/10 identified (multi-model diversity, statistical rigor, non-matrix benchmarks) |
| **13.0** | Multi-Model Benchmark Script | `multi_model_benchmark.py` | ✅ **READY** | Script supports Gemini, Claude, GPT-4o, DeepSeek; awaiting API keys for non-Gemini models |
| **14.0** | Subagent-Based Local Testing (Claude Opus 4.6) | `invoke_subagent` via Antigravity IDE | 🔄 **IN PROGRESS** | Exploring `invoke_subagent` for zero-cost Claude testing; user investigating access |

---

## 2. Detailed Execution Command Sequences

### Stage 1: Provisioning GCE VM
```bash
gcloud compute instances create scac-foil-node \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=ubuntu-2404-lts-amd64 \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB
```

### Stage 2 & 3: Code Upload & Environment Setup
```bash
# Upload code harness
gcloud compute scp week1_foil_test.py scac-foil-node:~ --zone=us-central1-a

# Install runtime dependencies on VM
gcloud compute ssh scac-foil-node --zone=us-central1-a --command="
    sudo apt update && sudo apt install -y python3 python3-pip python3-numpy python3-pandas
"
```

### Stage 4: Execution under Gemini 3.7 Flash
```bash
gcloud compute ssh scac-foil-node --zone=us-central1-a --command="
    export GEMINI_API_KEY='${GEMINI_API_KEY}' && \
    export SCAC_MODEL='gemini-3.7-flash' && \
    python3 week1_foil_test.py
"
```

### Stage 5 & 6: Download Results & Teardown
```bash
# Copy results back to local repository
gcloud compute scp --recurse scac-foil-node:~/foil_runs ./foil_runs --zone=us-central1-a

# Delete VM instance
gcloud compute instances delete scac-foil-node --zone=us-central1-a --quiet
```

---

## 3. Failure Mode Contingencies & Audit Log

- **Fail-Closed Verification**: `verify_environment_or_abort()` will test a 150MB bytearray allocation inside the VM's 128MB container before any LLM calls are issued. If `cgroup v2` enforcement fails, the script immediately aborts.
- **API Retries**: `query_llm_with_retry()` uses exponential backoff (up to 5 retries) for HTTP 429 rate limits.
- **Fallback Permission**: Automatically handles `--user` or `sudo` for `systemd-run`.
