import os
from pathlib import Path
import random

def create_test_repositories(repo_path: Path, loc: int) -> Path:
    """
    Create a fake Python repository with approximately `loc` lines of code.

    Args:
        repo_path: The directory to create the repository in.
        loc: Total number of lines of code to generate.

    Returns:
        Path to the created repository.
    """
    repo_path.mkdir(parents=True, exist_ok=True)
    file_count = max(1, loc // 200)  # Each file ~200 LOC
    lines_per_file = loc // file_count

    for i in range(file_count):
        file_path = repo_path / f"module_{i}.py"
        with file_path.open("w", encoding="utf-8") as f:
            f.write(f"# Auto-generated module {i}\n\n")
            for j in range(lines_per_file):
                func_name = f"func_{i}_{j}"
                f.write(f"def {func_name}(x):\n")
                f.write(f"    return x + {random.randint(1, 100)}\n\n")

    init_file = repo_path / "__init__.py"
    init_file.touch()
    return repo_path
