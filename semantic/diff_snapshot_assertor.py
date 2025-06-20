from pathlib import Path
from typing import List, Dict, Any

class DiffSnapshotAssertor:
    """Asserts and reports snapshot changes across runs."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.stats = {
            "new_files": [],
            "updated_files": [],
            "stale_files": [],
            "unchanged": []
        }

    def record_file_status(self, file_path: str, status: str):
        """Record a file snapshot status (new, updated, stale, unchanged)."""
        if status not in self.stats:
            raise ValueError(f"Unknown snapshot status: {status}")
        self.stats[status].append(file_path)

    def write_html_report(self, filename: str = "snapshot_diff_report.html"):
        """Generate an HTML report summarizing snapshot changes."""
        html = [
            "<html><head><title>Snapshot Diff Report</title></head><body>",
            "<h1>Snapshot Comparison Report</h1>"
        ]

        for category, label in [
            ("new_files", "New Snapshots Created"),
            ("updated_files", "Snapshots Updated"),
            ("stale_files", "Stale Snapshots (Unused)"),
            ("unchanged", "Unchanged Snapshots")
        ]:
            html.append(f"<h2>{label}</h2>")
            if self.stats[category]:
                html.append("<ul>")
                for path in self.stats[category]:
                    html.append(f"<li><code>{path}</code></li>")
                html.append("</ul>")
            else:
                html.append("<p><i>None</i></p>")

        html.append("</body></html>")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / filename
        output_path.write_text("\n".join(html), encoding="utf-8")
        return output_path