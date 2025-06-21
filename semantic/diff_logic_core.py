import hashlib

class FunctionElement:
    """Represents a function or method with full semantic information."""

    def __init__(self, name, file_path, line_start, line_end, ast_node=None):
        # Basic metadata
        self.name = name
        self.file_path = file_path
        self.line_start = line_start
        self.line_end = line_end

        # AST node reference (may be None if loaded from cache)
        self._ast_node = ast_node

        # Semantic information (populated by analyzers)
        self.arguments = []
        self.decorators = []
        self.docstring = None
        self.return_annotation = None
        self.calls = []
        self.semantic_role = None

        # Version tracking for cache invalidation
        self.version_hash = None
        self._content_hash = None

    @property
    def ast_node(self):
        """Safe getter for AST node."""
        return self._ast_node

    def get_content_hash(self):
        """Get stable hash of function content for change detection."""
        if self._content_hash is None:
            source_lines = self._get_source_lines()
            if source_lines:
                joined = '\n'.join(source_lines)
                self._content_hash = hashlib.md5(joined.encode()).hexdigest()
            else:
                fallback_parts = [
                    self.name,
                    self.line_start,
                    self.line_end,
                    str(self.arguments),
                    str(self.decorators),
                    str(self.return_annotation)
                ]
                self._content_hash = hashlib.md5('|'.join(map(str, fallback_parts)).encode()).hexdigest()

        return self._content_hash

    def _get_source_lines(self):
        """Extract source code lines for this function."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return lines[self.line_start - 1:self.line_end]
        except (FileNotFoundError, IndexError, UnicodeDecodeError):
            return None

    def __getstate__(self):
        """Prepare for pickling by removing non-serializable ast_node."""
        state = self.__dict__.copy()
        state['_ast_node'] = None
        return state

    def __repr__(self):
        return f"<FunctionElement name={self.name}, file={self.file_path}, lines=({self.line_start}-{self.line_end})>"
