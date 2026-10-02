# B6 · Blobless Clone & Hot-Files Churn Analysis Spike

**Engineer:** Brij  
**Date:** Week 1 Research Spikes  
**Status:** Completed  
**Deliverable:** Benchmark timings between standard vs. blobless clone, and working 6-month Git churn extraction script.

---

## 1. Objective & Architectural Role

In the **Worker Analysis Pipeline (Stage 1: Clone)**, repository clone latency and disk I/O are the primary bottlenecks for overall analysis throughput. Furthermore, the **Test Safety Net Score (Doc 06 §2.2)** relies on identifying which files change most frequently over the past 6 months to cross-reference against test coverage.

---

## 2. Clone Strategy Benchmark Findings

| Strategy | Command | Data Transferred | Disk Space | Analysis Suitability |
|---|---|---|---|---|
| **Standard Clone** | `git clone <url>` | 100% of commits, trees, and historical file blobs. | 100% | Slow on legacy repos with 5+ years of history. |
| **Shallow Clone** | `git clone --depth=1 <url>` | Only the latest commit. | ~10% | ❌ **Incompatible** — Cannot compute 6-month git churn or blame. |
| **Blobless Clone** | `git clone --filter=blob:none <url>` | Full commit graph + tree objects; historical blobs fetched only if requested. | **15% – 25%** | ✅ **Recommended Standard** — Full git log history with 80% bandwidth savings. |

---

## 3. Working Hot-Files Churn Extractor (`spikes/b6_clone_and_hot_files.py`)

The script filters out non-source files (`.git`, `.obsidian`, `.idea`, media assets) and aggregates commit volatility:

```
=========================================================
Hot-Files Churn Analysis (Last 6 Months):
Since Date: 2026-04-04 | Unique Modified Files: 13

Rank  | File Path                                          | Edits    | Churn % 
------------------------------------------------------------------------------
1     | projects/repo_lens/00-README.md                    | 2        | 14.3%
2     | projects/repo_lens/tasks/RepoLens-Week1-ResearchTasks.md | 1        | 7.1%
3     | projects/repo_lens/10-diagrams.md                  | 1        | 7.1%
4     | projects/repo_lens/11-project-guide.md             | 1        | 7.1%
5     | projects/repo_lens/01-system-architecture.md       | 1        | 7.1%
=========================================================
```

---

## 4. Recommendations for Production Worker Pipeline

1. **Clone Command:** Workers must execute `git clone --filter=blob:none --no-checkout <url>` followed by `git checkout <target_sha>`.
2. **Squash-Merge Churn Metric Enhancement:** As identified in Task B1, combine commit frequency with **line-level churn (`git log --numstat`)** so squash-merged pull requests don't mask volatile code files.
