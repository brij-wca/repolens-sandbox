"""
Task B4: Python Project Module & Package Dependency Graph Generator
Author: Brij (RepoLens Team)

Parses Python files in a repository, extracts module imports via AST,
and outputs a deterministic, formatted Mermaid architecture diagram.
"""

import ast
import os
import sys
from pathlib import Path
from collections import defaultdict

def extract_python_imports(file_path: Path):
    """Extracts all imported modules and relative imports from a Python file using AST."""
    imports = set()
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
                elif node.level > 0:
                    imports.add(f"relative_level_{node.level}")
    except Exception as e:
        pass
    return imports

def build_project_graph(root_dir: str):
    """Scans repository and builds internal module and third-party dependency graph."""
    root_path = Path(root_dir)
    internal_modules = set()
    file_to_imports = defaultdict(set)
    
    # Scan all python files
    for py_file in root_path.rglob("*.py"):
        if any(part in py_file.parts for part in [".venv", "venv", "__pycache__", ".git", "build", "dist"]):
            continue
        rel_module = py_file.relative_to(root_path).with_suffix("")
        module_name = ".".join(rel_module.parts)
        top_package = rel_module.parts[0]
        internal_modules.add(top_package)
        
        raw_imports = extract_python_imports(py_file)
        file_to_imports[top_package].update(raw_imports)
        
    # Generate Mermaid Diagram
    mermaid_lines = ["flowchart TD"]
    mermaid_lines.append("  %% Subgraphs for Internal Packages")
    
    dependencies = set()
    for pkg, imports in file_to_imports.items():
        for imp in imports:
            if imp == pkg:
                continue
            if imp in internal_modules:
                dependencies.add(f"  {pkg}[\"{pkg}\"] --> {imp}[\"{imp}\"]")
            elif not imp.startswith("relative_"):
                # Third-party or stdlib
                dependencies.add(f"  {pkg}[\"{pkg}\"] -.-> ext_{imp}[\"({imp})\"]")
                
    mermaid_lines.extend(sorted(list(dependencies)))
    return "\n".join(mermaid_lines)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"Generating Mermaid dependency graph for: {target}")
    graph = build_project_graph(target)
    print("\n--- [MERMAID OUTPUT] ---")
    print(graph)
    print("------------------------")
