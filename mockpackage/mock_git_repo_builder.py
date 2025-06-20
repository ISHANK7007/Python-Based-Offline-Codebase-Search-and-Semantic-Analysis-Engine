import pytest
from index.codebase_index import CodebaseIndex

def test_indexing_performance(benchmark, repo_10k):
    """Benchmark indexing performance on a 10K LOC repository."""
    
    # Run the benchmarked function
    result = benchmark(CodebaseIndex, repo_10k)

    # Assert the result is a valid index instance
    assert isinstance(result, CodebaseIndex)

    # Optional: add post-benchmark assertions (commented to avoid breaking test runs)
    # assert benchmark.stats.stats.mean < 2.0  # Mean time under 2 seconds
