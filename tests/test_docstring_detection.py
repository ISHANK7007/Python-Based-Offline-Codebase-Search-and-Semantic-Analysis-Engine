import pytest
from pathlib import Path
from parser.safe_parser import SafeParser
from semantic.semantic_indexer import SemanticIndexer
from models.versioned_element import VersionedElement

class ReferenceFileRegistry:
    """Minimal registry to track golden file registrations and updates."""
    def __init__(self):
        self.registered_files = []
        self.updated_files = []

    def register_file(self, path, filetype, test_name):
        self.registered_files.append((path, filetype, test_name))

    def record_update(self, path):
        self.updated_files.append(path)

class GoldenFileTester:
    """Reusable class for golden file assertions."""
    def __init__(self, request, base_dir: Path, registry: ReferenceFileRegistry, file_suffix: str = ".docstring"):
        self.request = request
        self.base_dir = Path(base_dir)
        self.registry = registry
        self.file_suffix = file_suffix
        self.update_golden = request.config.getoption("--update-golden")
        self.validate_only = request.config.getoption("--validate-only")
        self.interactive = request.config.getoption("--interactive-update")
        if self.validate_only:
            self.update_golden = False

    def get_golden_path(self, name: str, format_type: str = "txt") -> Path:
        test_name = self.request.node.name
        module_name = self.request.module.__name__.split('.')[-1]
        golden_dir = self.base_dir / "golden" / module_name
        golden_dir.mkdir(parents=True, exist_ok=True)
        sanitized_name = name.replace('/', '_').replace('\\', '_')
        path = golden_dir / f"{sanitized_name}{self.file_suffix}.{format_type}"
        self.registry.register_file(path, "golden", test_name)
        return path

    def assert_match_golden(self, name: str, actual_content: str, format_type: str = "txt", normalize_fn=None) -> None:
        golden_path = self.get_golden_path(name, format_type)
        if normalize_fn:
            actual_content = normalize_fn(actual_content)
        if not golden_path.exists():
            if self.validate_only:
                raise AssertionError(f"Golden file {golden_path} doesn't exist, and --validate-only was specified")
            if self.update_golden:
                golden_path.parent.mkdir(parents=True, exist_ok=True)
                golden_path.write_text(actual_content)
                self.registry.record_update(golden_path)
                print(f"Created new golden file: {golden_path}")
            else:
                raise AssertionError(f"Golden file {golden_path} doesn't exist. Run with --update-golden to create it.")
            return
        expected_content = golden_path.read_text()
        if actual_content != expected_content:
            if self.validate_only:
                raise AssertionError(f"Content mismatch in {golden_path} (validate-only mode)")
            if self.update_golden:
                golden_path.write_text(actual_content)
                self.registry.record_update(golden_path)
                print(f"Updated golden file: {golden_path}")
            else:
                import difflib
                diff = "\n".join(difflib.unified_diff(expected_content.splitlines(), actual_content.splitlines(), fromfile="expected", tofile="actual", lineterm=""))
                raise AssertionError(f"Content mismatch in {golden_path}.\n\nDiff:\n{diff}\n\nRun with --update-golden to update.")

@pytest.fixture
def golden_tester(request, tmp_path):
    registry = ReferenceFileRegistry()
    return GoldenFileTester(
        request=request,
        base_dir=tmp_path,
        registry=registry,
        file_suffix=".docstring"
    )

def extract_docstring_summary(code: str) -> str:
    parser = SafeParser()
    elements = parser.parse_string(code)
    summaries = []
    for elem in elements:
        if isinstance(elem, VersionedElement):
            name = elem.qualified_name or elem.name
            doc = elem.docstring or "<no docstring>"
            summaries.append(f"{name}: {doc.strip()}")
    return "\n".join(sorted(summaries))

@pytest.mark.parametrize("source_file", [
    "mock_repos.py",
    "mock_flask_like.py",
    "mock_nested_churn.py",
    "mock_py38_to_312.py",
])
def test_docstring_extraction(source_file, golden_tester):
    source_path = Path("mockpackage") / source_file
    code = source_path.read_text(encoding="utf-8")
    summary = extract_docstring_summary(code)
    golden_tester.assert_match_golden(name=source_file, actual_content=summary)