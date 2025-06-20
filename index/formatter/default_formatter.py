class ResultFormatter:
    """Base class for formatting query results"""
    
    def format_results(self, results, output_format="text"):
        """Format a list of results into the specified output format"""
        raise NotImplementedError()

class DefaultFormatter(ResultFormatter):
    """Default implementation with reasonable defaults"""
    
    def __init__(self, default_columns=None):
        self.default_columns = default_columns or [
            'type', 'name', 'file_path', 'line_range', 'role'
        ]
    
    def format_results(self, results, output_format="text"):
        if output_format == "text":
            return self._format_as_text(results)
        elif output_format == "json":
            return self._format_as_json(results)
        elif output_format == "csv":
            return self._format_as_csv(results)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _format_as_text(self, results):
        """Format results as human-readable text"""
        output = []
        for item in results:
            line = []
            for col in self.default_columns:
                value = getattr(item, col, "N/A")
                line.append(f"{col}: {value}")
            output.append(" | ".join(line))
        return "\n".join(output)
    
    def _format_as_json(self, results):
        """Format results as JSON"""
        import json
        
        json_results = []
        for item in results:
            result_dict = {}
            for col in self.default_columns:
                result_dict[col] = str(getattr(item, col, "N/A"))
            json_results.append(result_dict)
        
        return json.dumps(json_results, indent=2)
    
    def _format_as_csv(self, results):
        """Format results as CSV"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=self.default_columns)
        writer.writeheader()
        
        for item in results:
            row = {}
            for col in self.default_columns:
                row[col] = str(getattr(item, col, "N/A"))
            writer.writerow(row)
        
        return output.getvalue()