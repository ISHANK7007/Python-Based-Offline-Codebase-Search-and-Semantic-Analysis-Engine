from pathlib import Path
from typing import List, Dict

class SemanticDiffRegressionTracker:
    """Generates HTML regression reports for semantic diffs."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.reports: List[Dict[str, str]] = []

    def add_diff_case(self, test_name: str, symbol: str, before: str, after: str, diff_summary: str):
        """Register a new regression comparison."""
        self.reports.append({
            "test": test_name,
            "symbol": symbol,
            "before": before,
            "after": after,
            "summary": diff_summary
        })

    def write_html_report(self, filename: str = "semantic_diff_report.html"):
        """Write the full HTML report to disk."""
        html = [
            "<html><head><title>Semantic Diff Regression Report</title></head><body>",
            "<h1>Semantic Diff Regression Summary</h1>",
            "<table border='1' cellpadding='6'>",
            "<tr><th>Test Case</th><th>Symbol</th><th>Before</th><th>After</th><th>Diff Summary</th></tr>"
        ]

        for case in self.reports:
            html.append(f"""
                <tr>
                    <td>{case['test']}</td>
                    <td><code>{case['symbol']}</code></td>
                    <td><pre>{case['before']}</pre></td>
                    <td><pre>{case['after']}</pre></td>
                    <td>{case['summary']}</td>
                </tr>
            """)

        html.append("</table></body></html>")

        output_path = self.output_dir / filename
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(html), encoding="utf-8")
        return output_path