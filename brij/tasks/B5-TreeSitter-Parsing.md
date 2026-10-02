# B5 · Tree-sitter & Code Parsing Spike

**Engineer:** Brij  
**Date:** Week 1  
**Status:** Completed  
**Deliverable:** Working Python AST & Symbol Extraction script with benchmark timings.

---

## 1. Objective & Architecture Role
In the **Worker Analysis Pipeline (Stage 2: Fact Extraction)**, RepoLens needs to parse every code file in a repository to:
1. Extract structural symbols (Classes, Methods, Functions, Imports, Decorators, and Docstrings).
2. Segment files into coherent chunks for semantic search embeddings (`voyage-code-3`).
3. Prepare symbol outlines for the LLM File Summarizer (Stage 4).

---

## 2. Benchmark Results & Speed

Running against real Python repository files (`spikes/b5_treesitter_parser.py`):

```
Benchmarking against 11 Python files:
  • agent.py                  | 0 classes  | 2 funcs   | Latency: 18.56 ms
  • embeddings.py             | 1 classes  | 4 funcs   | Latency: 0.72 ms
  • gitlab_service.py         | 6 classes  | 16 funcs  | Latency: 5.47 ms
  • main.py                   | 1 classes  | 19 funcs  | Latency: 4.04 ms
  • vector_db.py              | 1 classes  | 6 funcs   | Latency: 2.12 ms
  • test_gitlab_service.py    | 3 classes  | 9 funcs   | Latency: 1.14 ms
-------------------------------------------------------------------------
Summary: Extracted 15 classes, 78 functions in 40.72 ms total.
Average latency per file: ~3.70 ms
```

---

## 3. Key Findings & Tradeoffs

| Parser Approach | Pros | Cons | Recommendation |
|---|---|---|---|
| **Python `ast` (Standard Library)** | Zero binary dependencies, ultra-fast (~3.7 ms/file), 100% native Python 3.13 support. | Python only. Cannot parse C# / .NET files. | Use for all Python fact extraction and symbol analysis. |
| **`tree-sitter` (via C bindings)** | Polyglot (supports both Python and C# in one engine), fault-tolerant to syntax errors. | Requires pre-compiled shared libraries (`.dll`/`.so`) per architecture. | Use `tree-sitter-c-sharp` for .NET repos and `ast` / `tree-sitter-python` for Python. |

### Edge Case Mitigations:
1. **UTF-8 BOM Characters (`\ufeff`):** Handled by opening files with `encoding="utf-8-sig"`.
2. **Nested & Async Functions:** Extracted recursively with `parent_class` tracking and `is_async=True` flags.
3. **Chunking Boundary:** Chunks are split by top-level class/function boundaries rather than arbitrary line counts, preserving full semantic context for Claude and embeddings.
