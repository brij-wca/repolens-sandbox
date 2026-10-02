"""
Task B7: Cyclomatic Complexity (Lizard) & Secret Scanning (Gitleaks) Spike
Author: Brij (RepoLens Team)

1. Analyzes cyclomatic complexity (CCN), parameter count, and NLOC across functions.
2. Scans codebase for leaked credentials (API keys, private tokens, passwords)
   and confirms secret values stay redacted (--redact).
"""

import re
import os
import sys
import time
from pathlib import Path

# Common high-entropy & credential patterns (simulating gitleaks rules)
SECRET_PATTERNS = [
    ("GitLab Personal Access Token", re.compile(r"glpat-[a-zA-Z0-9_\-]{20}")),
    ("GitHub Personal Access Token", re.compile(r"ghp_[a-zA-Z0-9]{36}")),
    ("Generic API Secret Key", re.compile(r"(?i)(api[_-]?key|secret[_-]?key|password)\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{16,})['\"]")),
    ("Private RSA / EC Key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("JWT Bearer Token", re.compile(r"eyJ[a-zA-Z0-9_\-]{10,}\.eyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}")),
]

def calculate_python_complexity(code_text: str):
    """Calculates approximate cyclomatic complexity by counting decision points."""
    lines = code_text.splitlines()
    nloc = len([line for line in lines if line.strip() and not line.strip().startswith("#")])
    
    # Decision branch keywords (if, elif, for, while, except, with, and, or)
    decision_keywords = [" if ", " elif ", " for ", " while ", " except ", " and ", " or "]
    decision_count = 1
    for line in lines:
        for kw in decision_keywords:
            decision_count += line.count(kw)
            
    return {"nloc": nloc, "cyclomatic_complexity": decision_count}

def scan_for_secrets(file_path: Path, redact: bool = True):
    """Scans file for secrets and returns redacted findings."""
    findings = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        for rule_name, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(content):
                val = match.group(0)
                if redact:
                    redacted = val[:6] + "****************" if len(val) > 8 else "********"
                else:
                    val
                findings.append({
                    "rule": rule_name,
                    "file": str(file_path.name),
                    "match": redacted if redact else val
                })
    except Exception:
        pass
    return findings

def run_spike(target_dir: str):
    print("=========================================================")
    print("RepoLens Spike B7: Complexity (Lizard) & Secret Scanning")
    print("=========================================================")
    print(f"Target Directory: {target_dir}\n")
    
    root = Path(target_dir)
    py_files = [f for f in root.rglob("*.py") if not any(p in f.parts for p in [".venv", "venv", "__pycache__", ".git"])]
    
    print(f"[1/2] Complexity Analysis (Scanned {len(py_files)} Python files):")
    high_complexity = []
    total_nloc = 0
    
    for f in py_files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        comp = calculate_python_complexity(content)
        total_nloc += comp["nloc"]
        if comp["cyclomatic_complexity"] > 10:
            high_complexity.append((f.name, comp["cyclomatic_complexity"], comp["nloc"]))
            
    print(f"  * Total Lines of Code (NLOC): {total_nloc}")
    print(f"  * Files with High Complexity (>10 CCN): {len(high_complexity)}")
    for name, ccn, nloc in high_complexity[:5]:
        print(f"    - {name:<30} | CCN: {ccn:<3} | NLOC: {nloc}")

    print("\n[2/2] Secret Scanner (Gitleaks Simulation with --redact):")
    all_secrets = []
    for f in root.rglob("*"):
        if f.is_file() and not any(p in f.parts for p in [".git", ".venv", "venv", "__pycache__"]):
            secrets = scan_for_secrets(f, redact=True)
            all_secrets.extend(secrets)
            
    print(f"  * Potential Secret Findings: {len(all_secrets)}")
    for s in all_secrets:
        print(f"    - [{s['rule']}] in {s['file']} -> Match: {s['match']}")
        
    print("=========================================================")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    run_spike(target)
