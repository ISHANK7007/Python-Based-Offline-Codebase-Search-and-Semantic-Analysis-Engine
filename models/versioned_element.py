class CodeElement:
    def __init__(self,
                 name,
                 parameters=None,
                 returns=None,
                 docstring=None,
                 decorators=None,
                 line_start=None,
                 line_end=None,
                 file_path=None,
                 type="function",
                 body_hash=None):
        """
        Represents a symbol (function, class, method) in the codebase.
        """
        self.name = name
        self.parameters = parameters or []
        self.returns = returns
        self.docstring = docstring
        self.decorators = decorators or []
        self.line_start = line_start
        self.line_end = line_end
        self.file_path = file_path
        self.type = type
        self.body_hash = body_hash

        self.git_metadata = None  # To be filled during indexing or by GitMetadataManager

    def __repr__(self):
        return f"<CodeElement {self.type} {self.name} ({self.file_path}:{self.line_start}-{self.line_end})>"
