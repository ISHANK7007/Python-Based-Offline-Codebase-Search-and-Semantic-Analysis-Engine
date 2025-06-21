import os
from pathlib import Path
from typing import List, Dict, Optional


class CLISnapshotRegressionRenderer:
    """Generates an HTML report summarizing snapshot CLI regression outcomes."""

    def __init__(self, results_dir: Path):
        self.results_dir = results_dir
        self.sections: List[str] = []

    def render_intro(self, title: str, description: str) -> None:
        """Render the report introduction."""
        intro_html = f"""
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial; }}
                h1 {{ color: #333; }}
                .section {{ margin-bottom: 20px; }}
                .diff {{ font-family: monospace; background: #f9f9f9; padding: 10px; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p>{description}</p>
        """
        self.sections.append(intro_html)

    def render_section(self, heading: str, diff_text: str) -> None:
        """Add a snapshot diff section."""
        section_html = f"""
        <div class="section">
            <h2>{heading}</h2>
            <div class="diff">{diff_text.replace('\n', '<br>')}</div>
        </div>
        """
        self.sections.append(section_html)

    def render_summary(self, summary_stats: Dict[str, int]) -> None:
        """Append a summary section at the end."""
        html = """
        <div class="section">
            <h2>Summary</h2>
            <ul>
        """
        for key, val in summary_stats.items():
            html += f"<li><strong>{key}</strong>: {val}</li>"
        html += """
            </ul>
        </div>
        """
        self.sections.append(html)

    def finalize(self) -> str:
        """Finalize the HTML output and return as string."""
        self.sections.append("</body></html>")
        return "\n".join(self.sections)

    def save_report(self, filename: str = "cli_snapshot_regression.html") -> None:
        """Save the generated HTML report to disk."""
        html_content = self.finalize()
        out_path = self.results_dir / filename
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html_content)
