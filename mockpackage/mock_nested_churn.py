import os
from pathlib import Path

def create_nested_function_churn_repo(output_dir: str, depth: int = 10, num_versions: int = 3):
    """
    Generate a mock repository with deeply nested functions that evolve over versions.

    Args:
        output_dir (str): Path to output the mock repository.
        depth (int): Depth of nesting for each function.
        num_versions (int): Number of versions to simulate evolution.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for version in range(num_versions):
        file_path = Path(output_dir) / f"nested_v{version}.py"
        with open(file_path, "w") as f:
            f.write(f"# Version {version}\n\n")
            f.write("def root():\n")
            indent = "    "
            for i in range(depth):
                f.write(f"{indent}def nested_{i}():\n")
                indent += "    "
            f.write(f"{indent}print('Deepest level reached in version {version}')\n")
            for i in reversed(range(depth)):
                indent = "    " * (i + 1)
                f.write(f"{indent}nested_{i}()\n")
            f.write("    return 'done'\n")
