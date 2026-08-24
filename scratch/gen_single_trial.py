import os
import json
import urllib.request
import subprocess

cmd = ["/Users/manuagrawal/Downloads/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]
env = {"CLOUDSDK_PYTHON": "/Users/manuagrawal/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12"}
token = subprocess.check_output(cmd, env=env, text=True).strip()

project = "project-a9fc9225-58b8-41d1-bac"
location = "us-central1"
url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/gemini-2.5-flash:generateContent"

prompt_euclidean_a = (
    "Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).\n"
    "Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.\n"
    "Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages."
)

prompt_euclidean_b = f"{prompt_euclidean_a}\n\nExecution environment:\nRAM limit: 128 MB."

def ask(prompt):
    req_data = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2}
    }
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=json.dumps(req_data).encode("utf-8")
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        if "```python" in raw:
            return raw.split("```python")[1].split("```")[0].strip()
        elif "```" in raw:
            return raw.split("```")[1].split("```")[0].strip()
        return raw.strip()

code_euc_a = ask(prompt_euclidean_a)
code_euc_b = ask(prompt_euclidean_b)

with open("single_test_EUC_A_blind.py", "w") as f:
    f.write(code_euc_a)

with open("single_test_EUC_B_aware.py", "w") as f:
    f.write(code_euc_b)

print("[+] Clean Pairwise Euclidean Distance trial pair generated.")
