# benchmarks/benchmarks.py

import os
import tempfile
import shutil
from pathlib import Path

from benchmarks.benchmark_utils import create_test_repositories
from index.codebase_index import CodebaseIndex
from index.formatter.query_engine import QueryEngine


class IndexingBenchmarks:
    """Benchmarks for indexing operations."""

    def setup(self):
        """Set up benchmark environment."""
        self.base_dir = Path(tempfile.mkdtemp())
        self.sizes = [1000, 10000, 100000]
        self.repos = {}

        for size in self.sizes:
            repo_dir = self.base_dir / f"repo_{size}"
            self.repos[size] = create_test_repositories(repo_dir, size)

    def teardown(self):
        """Clean up after benchmarks."""
        shutil.rmtree(self.base_dir)

    def time_indexing_small(self):
        index = CodebaseIndex(self.repos[1000])
        return index

    def time_indexing_medium(self):
        index = CodebaseIndex(self.repos[10000])
        return index

    def time_indexing_large(self):
        index = CodebaseIndex(self.repos[100000])
        return index

    def mem_indexing_small(self):
        index = CodebaseIndex(self.repos[1000])
        return index

    def peakmem_indexing_large(self):
        index = CodebaseIndex(self.repos[100000])
        return index


class QueryBenchmarks:
    """Benchmarks for query operations."""

    def setup(self):
        self.base_dir = Path(tempfile.mkdtemp())
        self.repo_dir = self.base_dir / "repo"
        create_test_repositories(self.repo_dir, 10000)

        self.index = CodebaseIndex(self.repo_dir)
        self.query_engine = QueryEngine(self.index)

    def teardown(self):
        shutil.rmtree(self.base_dir)

    def time_search_by_name(self):
        return self.query_engine.query(name_pattern="*test*")

    def time_search_by_type(self):
        return self.query_engine.query(type="function")

    def time_complex_query(self):
        return self.query_engine.query(
            type="function", has_decorator=True, max_depth=3
        )

    def track_query_result_count(self):
        results = self.query_engine.query(type="function")
        return len(results)
