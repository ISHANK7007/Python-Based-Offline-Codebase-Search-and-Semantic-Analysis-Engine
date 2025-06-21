import sys
from pathlib import Path

# ✅ Ensure Output_code is importable
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import subprocess
import time
import os
import psutil

from parser.safe_parser import SafeParser
from parser.visitor import ASTParser
from scanner.file_scanner import FileCrawler
from index.codebase_index import CodebaseIndex
from tests.utils.output_normalizer import normalize_output, normalize_golden


def test_ast_decorator_detection_matches_golden():
    """
    TC1: AST Parser-based detection of functions decorated with `@login_required`
    and compare output against golden snapshot.
    """
    print("🔍 Starting TC1: AST Decorator Detection Golden Snapshot Test...")
    golden_path = BASE_DIR / "tests/golden/decorator_login_required.golden"

    # Extract decorated functions via AST
    crawler = FileCrawler()
    parser = SafeParser()
    visitor = ASTParser()
    files = crawler.scan_directory(str(BASE_DIR / "mockpackage"))

    collected_output = []
    for file in files:
        tree = parser.parse_file(Path(file))
        if tree:
            elements = visitor.parse(tree, file)
            for el in elements:
                if any("login_required" in d.name for d in el.decorators):
                    collected_output.append(f"{el.file_path}:{el.name}")

    final_output = "\n".join(sorted(collected_output)).strip()

    if not golden_path.exists():
        golden_path.parent.mkdir(parents=True, exist_ok=True)
        golden_path.write_text(final_output)
        print(f"📸 Golden snapshot created at: {golden_path}")
    else:
        expected = normalize_golden(golden_path.read_text())
        actual = normalize_output(final_output)
        assert actual == expected, "❌ AST output does not match golden snapshot"
        print("✅ TC1 passed: AST decorator search matches golden file.")


def test_indexing_performance_on_benchmark_repo():
    """
    TC2: Index at least 1K Python files and verify performance and memory usage.
    Constraints: Time < 1.5s, Memory < 200MB
    """
    print("\n🚀 Starting TC2: Indexing Benchmark on Large Repo...")
    repo_path = BASE_DIR / "benchmark_repo"

    if not repo_path.exists():
        print("⚠️ Skipping TC2: benchmark_repo directory is missing.")
        return

    crawler = FileCrawler()
    files = crawler.scan_directory(str(repo_path))
    if len(files) < 1000:
        print("⚠️ Skipping TC2: benchmark_repo has fewer than 1000 Python files.")
        return

    parser = SafeParser()
    visitor = ASTParser()
    index = CodebaseIndex()

    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss
    start_time = time.time()
    parsed_count = 0

    for file in files:
        tree = parser.parse_file(Path(file))
        if tree:
            elements = visitor.parse(tree, file)
            for el in elements:
                index.add(el)
            parsed_count += 1

    elapsed = time.time() - start_time
    mem_after = process.memory_info().rss
    peak_mem_mb = (mem_after - mem_before) / (1024 * 1024)

    print(f"\n📊 Indexed Files: {parsed_count}")
    print(f"⏱️  Elapsed Time : {elapsed:.2f} seconds")
    print(f"💾 Peak Memory  : {peak_mem_mb:.1f} MB")

    assert elapsed < 1.5, f"❌ Indexing took too long: {elapsed:.2f}s"
    assert peak_mem_mb < 200, f"❌ Memory usage exceeded: {peak_mem_mb:.1f}MB"
    print("✅ TC2 passed: Indexing benchmark within performance limits.")


# ✅ Run tests when file is executed directly
if __name__ == "__main__":
    test_ast_decorator_detection_matches_golden()
    test_indexing_performance_on_benchmark_repo()
