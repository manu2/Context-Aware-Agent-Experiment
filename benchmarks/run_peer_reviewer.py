"""
Local Manuscript Consistency Checker for Substrate-Aware Code Generation Draft.

Preflight utility to verify keyword alignment, structure integrity, and formatting assertions.
"""

import os
import sys

def audit_manuscript():
    paper_path = "paper_draft.md"
    if not os.path.exists(paper_path):
        print(f"Error: {paper_path} not found.")
        sys.exit(1)
        
    with open(paper_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    print("=" * 80)
    print("  LOCAL PRE-FLIGHT CONSISTENCY CHECK: paper_draft.md")
    print("=" * 80)
    print(f"Total Lines: {len(content.splitlines())}")
    print(f"Total Characters: {len(content)}")
    
    # Check key empirical claims present
    claims = [
        "Substrate-Aware",
        "128 MB",
        "gemini-3.7-flash",
        "claude-opus-5",
        "gpt-5.6-sol",
        "claude-sonnet-5",
        "MaxRSS",
        "Budget Compliance",
        "resource-efficient"
    ]
    
    print("\n[+] Verification of Key Scientific Claims & Models:")
    for claim in claims:
        status = "✅ PRESENT" if claim in content else "❌ MISSING"
        print(f"  - {claim:<30}: {status}")
        
    print("=" * 80)
    print("To run a deep semantic review, invoke the 'peer_reviewer' subagent in chat.")

if __name__ == "__main__":
    audit_manuscript()
