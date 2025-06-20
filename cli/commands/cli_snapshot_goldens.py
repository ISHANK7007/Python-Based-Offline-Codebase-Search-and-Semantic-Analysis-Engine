import subprocess
import random
from typing import Dict, Any
from pathlib import Path

from mockpackage.symbol_evolution import SymbolEvolutionGenerator
from mockpackage.mock_git_repo_builder import GitRepoEvolver

def simulate_repo_evolution(repo_path: Path, num_versions: int = 5, seed: int = 42) -> Dict[str, Any]:
    """Create a repository with simulated evolution across versions."""
    evolver = GitRepoEvolver(repo_path, seed=seed)

    stages = ["initial", "feature_addition", "refactoring", "api_change", "bugfix", "deprecation"]
    symbols = {"functions": {}, "classes": {}}
    versions = {}

    evolver.create_branch("main")

    # Initial version
    initial_code = """
# Initial module
from typing import Dict, List, Optional, Any

def hello(name: str) -> str:
    \"\"\"Say hello to someone.\"\"\"
    return f"Hello, {name}!"

def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"Process input data.\"\"\"
    result = {}
    for key, value in data.items():
        result[key] = str(value).upper()
    return result

class DataHandler:
    \"\"\"Handle data processing.\"\"\"
    def __init__(self, prefix: str = ""):
        self.prefix = prefix
    def format(self, data: str) -> str:
        return f"{self.prefix}{data}"
"""
    evolver.add_file("src/module.py", initial_code)
    evolver.add_file("src/__init__.py", "# Package initialization")
    commit_hash = evolver._commit_changes("Initial code")

    symbols["functions"]["hello"] = "src/module.py"
    symbols["functions"]["process_data"] = "src/module.py"
    symbols["classes"]["DataHandler"] = "src/module.py"
    evolver.create_tag("v0.1.0", "Initial version")
    versions["v0.1.0"] = commit_hash

    for i in range(1, num_versions):
        stage = stages[i % len(stages)]
        branch_name = f"feature/{stage}_{i}"
        evolver.create_branch(branch_name)

        if stage == "feature_addition":
            mod_path = f"src/features_{i}/features_{i}.py"
            func = f"feature{i}_function"
            cls = f"Feature{i}Class"
            code = [
                f"# Module for feature {i}",
                "from typing import Dict, List, Any, Optional",
                SymbolEvolutionGenerator.add_function(func, 2),
                "",
                SymbolEvolutionGenerator.add_class(cls, [f"method{j}" for j in range(3)], 2),
            ]
            evolver.add_file(mod_path, "\n".join(code))
            evolver.add_file(f"src/features_{i}/__init__.py", f"from .features_{i} import {func}, {cls}")

            main_path = evolver.repo_path / "src/module.py"
            lines = main_path.read_text().splitlines()
            lines.insert(2, f"from features_{i} import {func}, {cls}")
            evolver.update_file("src/module.py", "\n".join(lines))

            symbols["functions"][func] = mod_path
            symbols["classes"][cls] = mod_path
            commit_hash = evolver._commit_changes(f"Add feature {i}")

        elif stage in {"refactoring", "api_change", "bugfix"}:
            if symbols["functions"]:
                func = random.choice(list(symbols["functions"].keys()))
                mod_path = symbols["functions"][func]
                content = (evolver.repo_path / mod_path).read_text().splitlines()

                start, end = None, None
                for j, line in enumerate(content):
                    if f"def {func}" in line:
                        start = j
                        for k in range(j + 1, len(content)):
                            if content[k] and not content[k].startswith(" "):
                                end = k
                                break
                        if end is None:
                            end = len(content)
                        break

                if start is not None:
                    segment = "\n".join(content[start:end])
                    change_type = (
                        "body" if stage == "refactoring"
                        else "signature" if stage == "api_change"
                        else "body"
                    )
                    updated = SymbolEvolutionGenerator.modify_function(segment, change_type).splitlines()
                    content = content[:start] + updated + content[end:]
                    evolver.update_file(mod_path, "\n".join(content))
                    commit_hash = evolver._commit_changes(f"{stage.title()} {func}")

        elif stage == "deprecation" and len(symbols["functions"]) > 1:
            func = random.choice(list(symbols["functions"].keys()))
            mod_path = symbols["functions"][func]
            mod_full = evolver.repo_path / mod_path
            lines = mod_full.read_text().splitlines()

            if random.random() < 0.3:
                start, end = None, None
                for j, line in enumerate(lines):
                    if f"def {func}" in line:
                        start = j
                        for k in range(j + 1, len(lines)):
                            if lines[k] and not lines[k].startswith(" "):
                                end = k
                                break
                        if end is None:
                            end = len(lines)
                        break

                if start is not None:
                    lines = lines[:start] + lines[end:]
                    evolver.update_file(mod_path, "\n".join(lines))
                    del symbols["functions"][func]
                    commit_hash = evolver._commit_changes(f"Remove {func}")
            else:
                for j, line in enumerate(lines):
                    if f"def {func}" in line:
                        indent = len(line) - len(line.lstrip())
                        lines.insert(j, " " * indent + "@deprecated")
                        break
                if "from deprecated import deprecated" not in "\n".join(lines):
                    for j, line in enumerate(lines):
                        if line.startswith("import") or line.startswith("from"):
                            lines.insert(j, "from deprecated import deprecated")
                            break
                evolver.update_file(mod_path, "\n".join(lines))
                commit_hash = evolver._commit_changes(f"Deprecate {func}")

        evolver.switch_branch("main")
        subprocess.run(
            ["git", "merge", "--no-ff", branch_name, "-m", f"Merge {branch_name}"],
            cwd=evolver.repo_path,
            check=True,
        )
        tag = f"v0.{i+1}.0"
        evolver.create_tag(tag, f"Version {tag}")
        versions[tag] = commit_hash

    return {"path": repo_path, "versions": versions, "symbols": symbols}
