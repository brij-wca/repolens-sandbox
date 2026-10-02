# B1 · Project Onboarding: Architectural Audit & High-Stakes Questions

**Engineer:** Brij  
**Date:** Week 1 Research Spikes  
**Status:** Completed & Pressure-Tested  
**Documents Audited:** `11-project-guide.md`, `01-system-architecture.md`, `08-implementation-roadmap.md`, `10-diagrams.md` (A1, A2, E3, F1)

---

## 1. Executive Architectural Audit

RepoLens is built on the philosophy of **"Facts First, AI Second"** — using deterministic static analysis tools to extract hard metrics, and using LLMs (Claude Sonnet/Opus) solely for explanation, synthesis, and documentation generation.

While the design is clean and cohesive, deep pressure-testing against production scale reveals **5 critical architectural tensions** across the data model, worker pipeline, and caching layer.

---

## 2. Thought-Provoking Standup Questions & Architectural Challenges

### 1. The "Single Database for 5 Roles" Bottleneck & Connection Starvation
* **The Architecture:** Doc 11 §5.11 & Doc 03 state that a single PostgreSQL 18 instance handles **5 distinct workloads**:
  1. Relational OLTP (Users, Repos, Findings)
  2. Asynchronous Job Queue (Procrastinate polling)
  3. Live SSE Progress Streaming (`NOTIFY / LISTEN`)
  4. High-Dimensional Vector Search (`pgvector` HNSW indexes with 1024-dim vectors)
  5. Resumable Workflow State (LangGraph checkpointer blobs)
* **The Hard Question for Stand-up:**  
  > *"When a background worker runs heavy vector similarity scans (`<=>` over 50,000 vectors) or bulk inserts 200 file summaries during a large repo analysis, will it saturate PostgreSQL connection pools and I/O IOPS, degrading response times for web users browsing the Portfolio/Graph UI? Should we establish dedicated connection pools (`pgbouncer` or separate worker pools) and memory limits (`maintenance_work_mem` / `work_mem`) right now?"*

---

### 2. File-Level SHA Caching vs. Cross-Module Semantic Drift
* **The Architecture:** Doc 06 §3 & Doc 11 §3 state that file summaries are cached by the file's raw content hash (`SHA-256(content)`). If a file doesn't change, its summary is reused.
* **The Hard Question for Stand-up:**  
  > *"What happens when a base data model or interface (e.g. `UserDTO` or `BaseRepository`) is modified, but dependent service files importing that model remain untouched? Their SHA-256 hashes won't change, so their cached summaries will describe outdated behavior, causing Stage 5 (Module Summary) and Stage 6 (Repo Synthesis) to hallucinate on stale assumptions. Should our cache key hash the file content PLUS its imported dependency hashes?"*

---

### 3. Commit Churn vs. Squash-Merge Distortion in Test Safety Net
* **The Architecture:** Doc 06 §2.2 calculates the *Test Safety Net* score by cross-referencing files that change often in `git log` (last 6 months) against whether unit tests exist for them.
* **The Hard Question for Stand-up:**  
  > *"In teams that practice squash-merging or feature branching, `git log` on `main` registers only 1 commit per PR (even if a file was edited 50 times in the branch), while teams that do rebase/merge-commits register 50 commits. This distorts the 'hot-file' churn metric purely based on git branching habits rather than true code volatility. Should our churn metric track line-level churn (lines added/deleted) rather than raw commit frequency?"*

---

### 4. Context Window Blowout in Stage 6 (Repo Synthesis)
* **The Architecture:** Diagram F1 shows that Stage 6 takes all module summaries and synthesizes the whole-repo architecture, tech debt ranking, and health explanation.
* **The Hard Question for Stand-up:**  
  > *"For large monorepos with 30+ modules and 400+ files, feeding all module summaries, ranked findings, and dependency graphs into Claude Sonnet in one prompt will approach 100k+ input tokens ($0.30+ per synthesis call) and increase prompt latency to 25+ seconds. How will we chunk or hierarchically aggregate module summaries before the final synthesis step?"*

---

### 5. Cross-Language Parity (.NET vs. Python) in Scoring Normalization
* **The Architecture:** Doc 01 §2 states RepoLens evaluates both C# (.NET 8) and Python/AI codebases on the exact same 0–100 scale.
* **The Hard Question for Stand-up:**  
  > *"C# codebases naturally have higher file counts, boilerplate interfaces, and namespace nesting compared to dynamic Python codebases. If we use cyclomatic complexity (`lizard`) and file-to-test ratios without language-calibrated scoring weights, .NET repos will consistently score lower than Python repos simply due to language idiom differences. How are the scoring thresholds normalized per ecosystem?"*

---

## 3. Review of Week 1 Spikes Alignment

| Task | Document Requirement | Implementation Verification | Status |
|---|---|---|---|
| **B1** | Read Docs 11, 01, 08 + Diagrams A1, A2, E3, F1; extract stand-up questions. | High-conviction architectural audit & 5 hard questions created. | ✅ Complete |
| **B2** | Run PostgreSQL 18 container with pgvector; verify vector extension & index. | Verified `pgvector:pg18` with 1024-dim HNSW cosine indexing (`b2_postgres_test.py`). | ✅ Complete |
| **B3** | Test WCA GitLab endpoints (doc 05 §3) with token; check OAuth & service account. | Verified `/api/v4/` manifest + service account architecture decision (`b3_gitlab_api_test.py`). | ✅ Complete |
| **B4** | Small script parsing Python imports $\rightarrow$ outputs Mermaid diagram. | Tested AST import parser emitting valid Mermaid flowcharts (`b4_project_graph.py`). | ✅ Complete |
| **B5** | Code symbol parser extracting classes, functions, imports with benchmark. | Benchmarked symbol extractor at 3.70 ms/file with UTF-BOM & async support (`b5_treesitter_parser.py`). | ✅ Complete |
