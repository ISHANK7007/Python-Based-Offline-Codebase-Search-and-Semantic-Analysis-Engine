# formatter.py (finalized and fixed)

import json
import yaml
import csv
from io import StringIO
from typing import Optional, List, Dict, Any
from pathlib import Path

from cli.utils.pager import Pager
from cli.enums import OutputFormat, VerbosityLevel


class ResultFormatter:
    """Formatter for code search results."""

    FIELD_SPECS = {
        "name": {"display": "Name", "width": 30},
        "element_type": {"display": "Type", "width": 12},
        "file_path": {"display": "Path", "width": 40},
        "line_number": {"display": "Line", "width": 6},
        "semantic_role": {"display": "Role", "width": 20},
        "score": {"display": "Score", "width": 6},
    }

    def __init__(
        self,
        format: OutputFormat = OutputFormat.TEXT,
        verbosity: VerbosityLevel = VerbosityLevel.BASIC,
        custom_fields: Optional[List[str]] = None,
        columns: Optional[int] = None,
        use_color: bool = True,
        path_style: str = "relative",
        base_dir: Optional[Path] = None,
        use_pager: bool = True,
        pager_threshold: int = 20,
        prefer_system_pager: bool = True,
    ):
        self.format = format
        self.verbosity = verbosity
        self.custom_fields = custom_fields
        self.columns = columns
        self.use_color = use_color
        self.path_style = path_style
        self.base_dir = base_dir
        self.use_pager = use_pager
        self.pager_threshold = pager_threshold
        self.prefer_system_pager = prefer_system_pager

        self.pager = Pager(prefer_system_pager=prefer_system_pager, page_threshold=pager_threshold) if use_pager else None

    def get_fields_for_display(self) -> List[str]:
        if self.custom_fields:
            return self.custom_fields
        return ["name", "element_type", "file_path", "line_number", "semantic_role", "score"]

    def display_results(self, results: List):
        """Display results in the specified format."""
        if not results:
            print("No results found.")
            return

        prepared_results = [self.prepare_result_for_display(r) for r in results]

        if not self.use_pager and self.format == OutputFormat.TEXT and self.use_color:
            self._display_rich_text_table(prepared_results)
            return

        if self.format == OutputFormat.JSON:
            output = self._get_json_output(prepared_results)
            syntax = "json"
        elif self.format == OutputFormat.YAML:
            output = self._get_yaml_output(prepared_results)
            syntax = "yaml"
        elif self.format == OutputFormat.CSV:
            output = self._get_csv_output(prepared_results)
            syntax = None
        elif self.format == OutputFormat.MARKDOWN:
            output = self._get_markdown_output(prepared_results)
            syntax = "markdown"
        else:
            output = self._get_text_output(prepared_results)
            syntax = None

        if self.use_pager:
            if syntax and self.use_color:
                self.pager.page_to_temp_file(output, syntax)
            else:
                self.pager.page(output)
        else:
            print(output)

    def prepare_result_for_display(self, result: Any) -> Dict[str, Any]:
        return result.to_dict()

    def _get_text_output(self, results: List[Dict[str, Any]]) -> str:
        buffer = StringIO()
        fields = self.get_fields_for_display()
        widths = {f: self.FIELD_SPECS.get(f, {}).get("width", 15) for f in fields}
        header = "  ".join(self.FIELD_SPECS.get(f, {}).get("display", f.capitalize()).ljust(widths[f]) for f in fields)
        buffer.write(header + "\n")
        buffer.write("-" * len(header) + "\n")
        for result in results:
            row = "  ".join(str(result.get(f, "")).ljust(widths[f]) for f in fields)
            buffer.write(row + "\n")
        return buffer.getvalue()

    def _get_json_output(self, results: List[Dict[str, Any]]) -> str:
        fields = self.get_fields_for_display()
        filtered = [{k: r.get(k) for k in fields if k in r} for r in results]
        return json.dumps(filtered, indent=2)

    def _get_yaml_output(self, results: List[Dict[str, Any]]) -> str:
        fields = self.get_fields_for_display()
        filtered = [{k: r.get(k) for k in fields if k in r} for r in results]
        return yaml.dump(filtered, sort_keys=False)

    def _get_csv_output(self, results: List[Dict[str, Any]]) -> str:
        fields = self.get_fields_for_display()
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow({k: result.get(k, "") for k in fields})
        return output.getvalue()

    def _get_markdown_output(self, results: List[Dict[str, Any]]) -> str:
        fields = self.get_fields_for_display()
        header = "| " + " | ".join(self.FIELD_SPECS.get(f, {}).get("display", f.capitalize()) for f in fields) + " |"
        separator = "| " + " | ".join("---" for _ in fields) + " |"
        rows = "\n".join("| " + " | ".join(str(r.get(f, "")) for f in fields) + " |" for r in results)
        return "\n".join([header, separator, rows])

    def _display_rich_text_table(self, results: List[Dict[str, Any]]):
        # Optional: add rich integration
        for r in results:
            print(f"- {r.get('name')} ({r.get('element_type')}) — {r.get('file_path')}:{r.get('line_number')}")
