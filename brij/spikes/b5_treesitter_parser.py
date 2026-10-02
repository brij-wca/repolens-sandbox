"""
Task B5: Code Chunking & Symbol Extraction Spike
Author: Brij (RepoLens Team)

Demonstrates extracting structured code symbols (Classes, Functions, Methods, Imports)
and chunking for semantic search embeddings and file summaries.
Measures parsing latency across files.
"""

import ast
import os
import sys
import time
from pathlib import Path

class PythonSymbolExtractor(ast.NodeVisitor):
    def __init__(self, filename="<unknown>"):
        self.filename = filename
        self.classes = []
        self.functions = []
        self.imports = []
        self.current_class = None

    def visit_ClassDef(self, node):
        prev_class = self.current_class
        self.current_class = node.name
        docstring = ast.get_docstring(node)
        self.classes.append({
            "name": node.name,
            "line_start": node.lineno,
            "line_end": getattr(node, "end_lineno", node.lineno),
            "docstring": docstring or "No docstring",
            "decorators": [ast.unparse(d) if hasattr(ast, "unparse") else d for d in node.decorator_list]
        })
        self.generic_visit(node)
        self.current_class = prev_class

    def visit_FunctionDef(self, node):
        self._record_func(node, is_async=False)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._record_func(node, is_async=True)
        self.generic_visit(node)

    def _record_func(self, node, is_async=False):
        docstring = ast.get_docstring(node)
        self.functions.append({
            "name": node.name,
            "parent_class": self.current_class,
            "is_async": is_async,
            "line_start": node.lineno,
            "line_end": getattr(node, "end_lineno", node.lineno),
            "docstring": docstring or "No docstring",
            "args": [arg.arg for arg in node.args.args]
        })

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        mod = node.module or ""
        for alias in node.names:
            self.imports.append(f"{mod}.{alias.name}")
        self.generic_visit(node)

def parse_and_benchmark(file_path: Path):
    start = time.perf_counter()
    content = file_path.read_text(encoding="utf-8-sig", errors="ignore")
    try:
        tree = ast.parse(content, filename=str(file_path))
        extractor = PythonSymbolExtractor(file_path.name)
        extractor.visit(tree)
    except Exception as e:
        extractor = PythonSymbolExtractor(file_path.name)
    duration_ms = (time.perf_counter() - start) * 1000
    
    return {
        "file": file_path.name,
        "classes": extractor.classes,
        "functions": extractor.functions,
        "imports_count": len(extractor.imports),
        "duration_ms": duration_ms
    }

def run_benchmark_suite(target_dir: str):
    root = Path(target_dir)
    py_files = list(root.rglob("*.py"))
    valid_files = [f for f in py_files if not any(p in f.parts for p in [".venv", "venv", "__pycache__", ".git"])]
    
    print(f"Benchmarking parser against {len(valid_files)} Python files in: {target_dir}\n")
    total_time = 0
    total_classes = 0
    total_funcs = 0
    
    for f in valid_files[:15]:
        res = parse_and_benchmark(f)
        total_time += res["duration_ms"]
        total_classes += len(res["classes"])
        total_funcs += len(res["functions"])
        print(f"  * {f.name:<30} | {len(res['classes']):<2} classes | {len(res['functions']):<2} funcs | Latency: {res['duration_ms']:.2f} ms")
        
    print("\n---------------------------------------------------------")
    print(f"Summary: Extracted {total_classes} classes, {total_funcs} functions in {total_time:.2f} ms total.")
    print(f"Average latency per file: {total_time / max(len(valid_files[:15]), 1):.2f} ms")
    print("---------------------------------------------------------")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    run_benchmark_suite(target)
