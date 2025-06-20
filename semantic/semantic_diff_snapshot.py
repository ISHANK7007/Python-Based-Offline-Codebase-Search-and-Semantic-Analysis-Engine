from pathlib import Path
from typing import Dict, Any
import json

class SemanticDiffSnapshotManager:
    """Handles saving and comparing semantic diff snapshots."""

    def __init__(self, snapshot_dir: Path):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def save_snapshot(self, test_id: str, symbol: str, diff_data: Dict[str, Any]):
        """Persist a semantic diff snapshot to a JSON file."""
        file_path = self._get_snapshot_path(test_id, symbol)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(diff_data, f, indent=2, sort_keys=True)

    def load_snapshot(self, test_id: str, symbol: str) -> Dict[str, Any]:
        """Load an existing semantic diff snapshot."""
        file_path = self._get_snapshot_path(test_id, symbol)
        if not file_path.exists():
            raise FileNotFoundError(f"Snapshot not found for {symbol} under {test_id}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def assert_snapshot_match(self, test_id: str, symbol: str, actual_data: Dict[str, Any]):
        """Compare current diff data against saved snapshot."""
        expected_data = self.load_snapshot(test_id, symbol)
        if actual_data != expected_data:
            import difflib
            actual_lines = json.dumps(actual_data, indent=2, sort_keys=True).splitlines()
            expected_lines = json.dumps(expected_data, indent=2, sort_keys=True).splitlines()
            diff = "\n".join(
                difflib.unified_diff(expected_lines, actual_lines, fromfile="expected", tofile="actual", lineterm="")
            )
            raise AssertionError(f"Semantic diff mismatch for '{symbol}':\n{diff}")

    def _get_snapshot_path(self, test_id: str, symbol: str) -> Path:
        """Get the snapshot file path for a symbol under a test case."""
        sanitized_symbol = symbol.replace("/", "_").replace(":", "_")
        return self.snapshot_dir / f"{test_id}__{sanitized_symbol}.snapshot.json"