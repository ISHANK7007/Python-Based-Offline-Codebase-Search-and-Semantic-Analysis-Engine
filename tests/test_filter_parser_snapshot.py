import pytest
from pathlib import Path
from cli.cli_filter_parser import parse_filter_expression

class SnapshotValidator:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def assert_snapshot(self, test_case: str, actual: str):
        snapshot_path = self.base_dir / f"{test_case}.snapshot.txt"
        if "--update-snapshots" in pytest.config.getoption("args"):
            snapshot_path.write_text(actual)
        elif not snapshot_path.exists():
            raise AssertionError(f"Snapshot missing: {snapshot_path}")
        else:
            expected = snapshot_path.read_text()
            if expected != actual:
                import difflib
                diff = "\n".join(difflib.unified_diff(
                    expected.splitlines(), actual.splitlines(),
                    fromfile="expected", tofile="actual", lineterm=""
                ))
                raise AssertionError(f"Snapshot mismatch for {test_case}:\n{diff}")

@pytest.fixture
def snapshot_validator(tmp_path):
    return SnapshotValidator(tmp_path / "filter_snapshots")

@pytest.mark.parametrize("expression", [
    "type:function AND visibility:public",
    "decorator:login_required OR decorator:admin_required",
    "arg:name:str AND return:str",
    "arg:name:str AND NOT arg:id:int",
])
def test_filter_parser_snapshot(expression, snapshot_validator):
    result = parse_filter_expression(expression)
    pretty = repr(result)  # Or use a structured formatter if available
    snapshot_validator.assert_snapshot(expression.replace(" ", "_"), pretty)
