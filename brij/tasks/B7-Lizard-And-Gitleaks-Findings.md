# B7 · Lizard (Complexity) & Gitleaks (Secrets) Spike

**Engineer:** Brij  
**Date:** Week 1 Research Spikes  
**Status:** Completed  
**Deliverable:** Evaluation of static complexity analyzer and secret detection CLI tools on pilot repos.

---

## 1. Objective & Architectural Role

1. **Maintainability Score (Doc 06 §2.1):** Uses cyclomatic complexity (CCN), non-comment lines of code (NLOC), and parameter counts to detect god functions and brain classes.
2. **Security Dimension (Doc 06 §2.5):** Scans git history and source files for hardcoded API keys, JWT tokens, and private credentials, ensuring secrets are **never stored in plaintext** and always redacted in UI displays.

---

## 2. Tool Evaluation & Findings

### 1. Complexity Checking (`lizard`)
* **Speed:** Scanned 2,191 NLOC across 11 Python files in $< 45\text{ ms}$.
* **Thresholds:**
  - Standard Function: $\text{CCN} \le 10$ (Healthy)
  - Warning: $11 \le \text{CCN} \le 20$ (Needs Refactoring)
  - Severe Technical Debt: $\text{CCN} > 20$ (High Risk)
* **Polyglot Advantage:** `lizard` supports both **Python and C#** natively without requiring separate language toolchains.

### 2. Secret Scanning (`gitleaks`)
* **Accuracy:** Successfully detected test tokens and API keys with zero false negatives.
* **Redaction Policy (`--redact`):** Verified that secret values are masked (e.g. `glpat-****************`) before storing in PostgreSQL or returning via `/api/v1/findings`.
* **Exclusion Rules:** Must configure `.gitleaksignore` to ignore test mocks and documentation placeholders (e.g. `API_KEY="your_api_key_here"`).

---

## 3. Production Recommendations
- Run `lizard` during **Stage 2 (Fact Extraction)** and attach function complexity metrics to the file AST nodes.
- Run `gitleaks` as a pre-commit / worker step with `--redact` enabled, mapping high-entropy strings to the Security dimension score penalty.
