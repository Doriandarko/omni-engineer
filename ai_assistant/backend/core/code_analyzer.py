# backend/core/code_analyzer.py

import ast
import os
from typing import List, Dict

class CodeAnalyzer:
    def analyze_code(self, code: str) -> List[Dict]:
        tree = ast.parse(code)
        analyzer = Analyzer()
        analyzer.visit(tree)
        return analyzer.issues

    def analyze_project(self, project_path: str) -> Dict[str, List[Dict]]:
        project_analysis = {}
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        code = f.read()
                    project_analysis[file_path] = self.analyze_code(code)
        return project_analysis

    def get_project_files(self, project_path: str) -> Dict[str, str]:
        project_files = {}
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        project_files[file_path] = f.read()
        return project_files

class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_FunctionDef(self, node):
        if len(node.body) > 20:
            self.issues.append({
                "type": "complexity",
                "message": f"Function '{node.name}' is too long. Consider breaking it into smaller functions.",
                "line": node.lineno
            })
        self.generic_visit(node)

    def visit_For(self, node):
        if isinstance(node.body[0], ast.For):
            self.issues.append({
                "type": "complexity",
                "message": "Nested loop detected. Consider extracting inner loop to a separate function.",
                "line": node.lineno
            })
        self.generic_visit(node)

    # Add more visit methods for other types of code analysis