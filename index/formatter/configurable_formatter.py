import json
import csv
import io
from tabulate import tabulate  # Ensure this is installed or catch ImportError
from index.formatter.default_formatter import ResultFormatter


class ConfigurableFormatter(ResultFormatter):
    """Formatter with user-configurable columns and formats"""

    def __init__(self):
        self.available_fields = {
            'type': {'description': 'Element type (function, class, etc.)'},
            'name': {'description': 'Element name'},
            'file_path': {'description': 'File path'},
            'line_range': {'description': 'Line number range (start, end)'},
            'role': {'description': 'Semantic role'},
            'doc': {'description': 'Documentation string'},
            'decorators': {'description': 'List of decorators'},
            'size': {'description': 'Size in lines of code'},
            'complexity': {'description': 'Cyclomatic complexity'},
            'calls': {'description': 'Functions called by this element'},
            'called_by': {'description': 'Functions that call this element'},
            'parent_class': {'description': 'Parent class for methods'},
            'return_type': {'description': 'Return type (if available)'},
            'parameters': {'description': 'Function parameters'},
        }

        self.default_config = {
            'columns': ['type', 'name', 'file_path', 'line_range', 'role'],
            'sort_by': 'name',
            'max_width': {
                'name': 30,
                'file_path': 50,
                'doc': 60
            },
            'format': 'text'
        }

        self.config = self.default_config.copy()

    def configure(self, **kwargs):
        """Update configuration with user settings"""
        for key, value in kwargs.items():
            if key in self.config:
                if key == 'columns':
                    for col in value:
                        if col not in self.available_fields:
                            raise ValueError(f"Unknown column: {col}")
                self.config[key] = value
            else:
                raise ValueError(f"Unknown configuration option: {key}")
        return self

    def format_results(self, results, output_format=None):
        """Format results according to current configuration"""
        format_type = output_format or self.config['format']

        if format_type == "text":
            return self._format_as_text(results)
        elif format_type == "json":
            return self._format_as_json(results)
        elif format_type == "csv":
            return self._format_as_csv(results)
        elif format_type == "table":
            return self._format_as_table(results)
        else:
            raise ValueError(f"Unsupported output format: {format_type}")

    def format(self, results, output_format=None):
        """Add this method to support calls to .format() as expected by CLI."""
        return self.format_results(results, output_format)

    def _format_as_text(self, results):
        output = []
        columns = self.config['columns']

        if self.config['sort_by'] in self.available_fields:
            results = sorted(results, key=lambda x: getattr(x, self.config['sort_by'], ''))

        for item in results:
            line_parts = []
            for col in columns:
                value = getattr(item, col, "N/A")
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                value = str(value)
                if col in self.config['max_width']:
                    max_width = self.config['max_width'][col]
                    if len(value) > max_width:
                        value = value[:max_width - 3] + "..."
                line_parts.append(f"{col}: {value}")
            output.append(" | ".join(line_parts))
        return "\n".join(output)

    def _format_as_table(self, results):
        columns = self.config['columns']
        if self.config['sort_by'] in self.available_fields:
            results = sorted(results, key=lambda x: getattr(x, self.config['sort_by'], ''))

        table_data = []
        for item in results:
            row = []
            for col in columns:
                value = getattr(item, col, "N/A")
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                value = str(value)
                if col in self.config['max_width']:
                    max_width = self.config['max_width'][col]
                    if len(value) > max_width:
                        value = value[:max_width - 3] + "..."
                row.append(value)
            table_data.append(row)
        return tabulate(table_data, headers=columns, tablefmt="grid")

    def _format_as_json(self, results):
        columns = self.config['columns']
        serialized = []
        for item in results:
            entry = {}
            for col in columns:
                value = getattr(item, col, "N/A")
                if isinstance(value, list):
                    value = list(map(str, value))
                entry[col] = str(value)
            serialized.append(entry)
        return json.dumps(serialized, indent=2)

    def _format_as_csv(self, results):
        output = io.StringIO()
        writer = csv.writer(output)
        columns = self.config['columns']
        writer.writerow(columns)
        for item in results:
            row = []
            for col in columns:
                value = getattr(item, col, "N/A")
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                row.append(str(value))
            writer.writerow(row)
        return output.getvalue()
