from index.formatter.configurable_formatter import ConfigurableFormatter

class FormatterTemplates:
    """Predefined templates for common query scenarios"""

    @staticmethod
    def code_review():
        """Template focused on code review information"""
        return ConfigurableFormatter().configure(
            columns=['name', 'file_path', 'line_range', 'complexity', 'size'],
            sort_by='complexity',
            format='table'
        )

    @staticmethod
    def api_explorer():
        """Template for exploring API endpoints"""
        return ConfigurableFormatter().configure(
            columns=['name', 'role', 'decorators', 'parameters', 'doc'],
            sort_by='name',
            format='text'
        )

    @staticmethod
    def dependency_analysis():
        """Template for analyzing dependencies"""
        return ConfigurableFormatter().configure(
            columns=['name', 'file_path', 'calls', 'called_by'],
            sort_by='file_path',
            format='table'
        )
