from enum import Enum
import json

class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"

class ConfigurableFormatter:
    def __init__(self, verbosity=None, format="text"):
        self.verbosity = verbosity
        self.format = format

    def format(self, results, output_format):
        if output_format == OutputFormat.TEXT or output_format == "text":
            return self._format_text(results)
        elif output_format == OutputFormat.JSON or output_format == "json":
            return self._format_json(results)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _format_text(self, results):
        lines = []
        for r in results:
            try:
                name = getattr(r, "name", str(r))
                path = getattr(r, "file_path", "")
                lines.append(f"{name} — {path}")
            except Exception:
                lines.append(str(r))
        return "\n".join(lines)

    def _format_json(self, results):
        try:
            return json.dumps(
                [r.to_dict() if hasattr(r, "to_dict") else str(r) for r in results],
                indent=2
            )
        except Exception:
            return json.dumps([str(r) for r in results], indent=2)
