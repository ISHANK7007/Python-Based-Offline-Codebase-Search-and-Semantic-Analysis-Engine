from index.formatter.default_formatter import DefaultFormatter
from index.formatter.configurable_formatter import ConfigurableFormatter
from index.query.execution_plan import ExecutionPlan  # if used elsewhere

class QueryEngine:
    def __init__(self, codebase_index, formatter=None):
        self.index = codebase_index
        self.formatter = formatter or DefaultFormatter()

    def query(self, filter_expression, output_format=None):
        """Execute a query and format the results"""
        raw_results = self._execute_query(filter_expression)

        # Use configured or fallback format
        try:
            return self.formatter.format_results(raw_results, output_format)
        except Exception as e:
            raise RuntimeError(f"Error formatting results: {e}")

    def _execute_query(self, filter_expression):
        """Stub method – implement query logic or plan execution"""
        if hasattr(self.index, 'query'):
            return self.index.query(filter_expression)
        raise NotImplementedError("Codebase index does not support querying.")

    def set_formatter(self, formatter):
        """Set a new formatter for the query engine"""
        if not hasattr(formatter, 'format_results'):
            raise TypeError("Formatter must implement 'format_results'")
        self.formatter = formatter
        return self

    def configure_output(self, **kwargs):
        """Configure the current formatter"""
        if hasattr(self.formatter, 'configure'):
            self.formatter.configure(**kwargs)
        else:
            # Replace with configurable formatter if not supported
            self.formatter = ConfigurableFormatter().configure(**kwargs)
        return self
