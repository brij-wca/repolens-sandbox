# B8 · Package Dependency Lookups & Vulnerabilities Spike

**Engineer:** Brij  
**Date:** Week 1 Research Spikes  
**Status:** Completed  
**Deliverable:** Working OSV.dev and PyPI JSON API integration for Dependency Hygiene scoring.

---

## 1. Objective & Architectural Role
In **Stage 2 (Fact Extraction)**, RepoLens parses `pyproject.toml`, `requirements.txt`, and `.csproj` files to evaluate the **Dependency Hygiene Score (Doc 06 §2.3)**:
1. **Outdatedness:** How many major/minor versions behind is the installed package compared to the latest release?
2. **Security Vulnerabilities:** Are there open CVEs recorded against the currently locked version?

---

## 2. API Integration Benchmarks (`spikes/b8_package_lookups.py`)

```
===========================================================================
Package      | Current  | Latest (PyPI)  | CVE Vulnerabilities (OSV.dev) 
---------------------------------------------------------------------------
psycopg      | 3.1.0    | 3.3.6          | 0 known CVEs (Secure)
requests     | 2.20.0   | 2.34.2         | Found 8 CVE(s) -> High Risk
   -> [ALERT] CVE-2024-47081: Requests vulnerable to .netrc credentials leak
   -> [ALERT] CVE-2024-35195: Requests Session SSL bypass vulnerability
pydantic     | 2.10.0   | 2.13.5         | 0 known CVEs (Secure)
fastapi      | 0.110.0  | 0.142.2        | 0 known CVEs (Secure)
===========================================================================
```

---

## 3. Key Findings & Performance Notes
1. **OSV.dev API Speed & Rate Limits:**
   - Single-query latency: $\approx 150–250\text{ ms}$.
   - OSV supports **batch querying (`/v1/querybatch`)**, allowing a worker to scan 50 packages in a single HTTP request in $< 400\text{ ms}$.
2. **Ecosystem Support:**
   - OSV.dev natively supports both **PyPI (Python)** and **NuGet (C#/.NET)**, satisfying our polyglot requirements under a single API schema.
3. **Caching Strategy:**
   - Vulnerability and version data should be cached in PostgreSQL (`package_cache` table) with a 24-hour TTL to prevent redundant external API roundtrips.
