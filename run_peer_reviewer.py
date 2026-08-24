import os
import sys
import json
import urllib.request
import urllib.error
import subprocess
import shutil

MODEL_NAME = os.environ.get("SCAC_MODEL", "gemini-2.5-flash")
GCP_PROJECT = os.environ.get("GCP_PROJECT", "project-a9fc9225-58b8-41d1-bac")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-central1")


def get_vertex_token() -> str:
    token = os.environ.get("VERTEX_TOKEN")
    if token:
        return token
    try:
        gcloud_bin = shutil.which("gcloud") or "/Users/manuagrawal/Downloads/google-cloud-sdk/bin/gcloud"
        env = dict(os.environ)
        if "CLOUDSDK_PYTHON" not in env:
            env["CLOUDSDK_PYTHON"] = sys.executable
        out = subprocess.check_output([gcloud_bin, "auth", "print-access-token"], text=True, env=env)
        return out.strip()
    except Exception as e:
        print(f"[!] Warning: Token fetch failed ({e})")
        return ""


def run_peer_review():
    paper_path = "paper_draft.md"
    if not os.path.exists(paper_path):
        print(f"[!] Error: {paper_path} not found.")
        sys.exit(1)

    with open(paper_path, "r", encoding="utf-8") as f:
        paper_text = f.read()

    reviewer_system_prompt = (
        "You are an expert Senior Area Chair and Peer Reviewer for top-tier AI and Systems conferences (MLSys, NeurIPS Systems Track, OSDI, ICLR).\n"
        "You are known for rigorous, constructive, uncompromising academic standards. You do not give flattery or superficial praise.\n"
        "You evaluate papers based on four foundational criteria:\n"
        "1. Novelty and Problem Formulation (Is 'Silicon Blindness' a genuine problem? Is the SCAC framework novel?)\n"
        "2. Technical Rigor & Empirical Evidence (Are the benchmarks sufficiently diverse or too narrow? Are statistical claims supported?)\n"
        "3. Baselines & Ablation Studies (Are comparisons fair? Does the paper address counterarguments?)\n"
        "4. Actionable Deficiencies (What specific experiments, tables, or sections are missing before this can be accepted?)\n\n"
        "Review the attached manuscript thoroughly and provide a structured review in standard Markdown format including:\n"
        "- Summary of the Paper\n"
        "- Overall Recommendation Score (1-10) and Confidence Score (1-5)\n"
        "- Major Strengths (What works well?)\n"
        "- Critical Weaknesses & Gaps (Be brutally honest)\n"
        "- Detailed Questions for the Authors\n"
        "- Prioritized Action Plan to Reach Top-Tier Acceptance"
    )

    user_prompt = f"{reviewer_system_prompt}\n\n=== MANUSCRIPT TO REVIEW ===\n\n{paper_text}"

    print(f"[*] Invoking Senior Area Chair Reviewer Subagent (Model: {MODEL_NAME})...")
    token = get_vertex_token()
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if token:
        url = f"https://{GCP_LOCATION}-aiplatform.googleapis.com/v1/projects/{GCP_PROJECT}/locations/{GCP_LOCATION}/publishers/google/models/{MODEL_NAME}:generateContent"
        req_data = {
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.2}
        }
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            data=json.dumps(req_data).encode("utf-8")
        )
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={gemini_key}"
        req_data = {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.2}
        }
        req = urllib.request.Request(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(req_data).encode("utf-8")
        )

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        review_text = data["candidates"][0]["content"]["parts"][0]["text"]

    out_file = "reviewer_feedback.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(review_text)

    print(f"[+] Peer Review complete! Saved to {out_file}.")

if __name__ == "__main__":
    run_peer_review()
