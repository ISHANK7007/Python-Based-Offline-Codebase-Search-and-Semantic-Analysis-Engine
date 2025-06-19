import os
import ast
import time
import threading
from collections import defaultdict

from index.git_blame_resolver import GitMetadataManager
from parser.visitor import CodeVisitor


class CodebaseIndex:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_metadata_manager = GitMetadataManager(repo_path)
        self.elements = {}

    def index_codebase(self, git_mode="hybrid", **options):
        """
        Index the codebase with a configurable Git metadata strategy.

        git_mode: 'eager', 'lazy', 'hybrid', or 'deferred'
        """
        visitor = CodeVisitor(git_mode=git_mode, git_manager=self.git_metadata_manager)

        for file_path in self._find_python_files():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=file_path)
                    visitor.visit(tree)
            except (SyntaxError, FileNotFoundError, UnicodeDecodeError) as e:
                print(f"Skipping file {file_path}: {e}")
                continue

        self.elements.update(visitor.elements)

        if git_mode == "deferred":
            self._start_background_blame_processing()

        return self

    def _start_background_blame_processing(self):
        """Start a background thread to populate blame metadata asynchronously."""

        def process_blame_background():
            try:
                elements_to_process = sorted(
                    [e for e in self.elements.values()
                     if getattr(e.git_metadata, "commit_hash", None) == "pending"],
                    key=lambda e: os.path.getmtime(getattr(e, "file_path", "")),
                    reverse=True
                )

                for batch in self._batch_by_file(elements_to_process):
                    for element in batch:
                        if hasattr(element.git_metadata, "lazy_loader"):
                            element.git_metadata = element.git_metadata.lazy_loader()
                        time.sleep(0.01)  # avoid I/O overload
            except Exception as e:
                print(f"[Deferred Blame Thread] Error: {e}")

        threading.Thread(target=process_blame_background, daemon=True).start()

    def _batch_by_file(self, elements, batch_size=100):
        """Group elements by file to reduce blame overhead."""
        by_file = defaultdict(list)
        for element in elements:
            by_file[element.file_path].append(element)

        result = []
        current_batch = []

        for file_path, file_elements in by_file.items():
            file_elements.sort(key=lambda e: getattr(e, "line_start", 0))

            if len(current_batch) + len(file_elements) <= batch_size:
                current_batch.extend(file_elements)
            else:
                if current_batch:
                    result.append(current_batch)
                current_batch = file_elements

        if current_batch:
            result.append(current_batch)

        return result

    def _find_python_files(self):
        """Find all .py files under the repository path."""
        python_files = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        return python_files
