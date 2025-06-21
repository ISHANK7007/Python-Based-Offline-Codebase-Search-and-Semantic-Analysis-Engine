import ast
import logging
import sys
import traceback
from pathlib import Path
from typing import Optional, Dict, Any, Callable, Tuple, Union, List
from dataclasses import dataclass
from contextlib import contextmanager
from parser.visitor import ASTParser
from models.code_element import CodeElement
from scanner.file_scanner import FileCrawler

@dataclass
class ParsingError:
    file_path: Path
    error_type: str
    error_message: str
    line_number: Optional[int] = None
    column: Optional[int] = None
    traceback: Optional[str] = None
    code_snippet: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": str(self.file_path),
            "error_type": self.error_type,
            "message": self.error_message,
            "line": self.line_number,
            "column": self.column,
            "traceback": self.traceback,
            "code_snippet": self.code_snippet
        }

class SafeParser:
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        error_handler: Optional[Callable[[ParsingError], None]] = None,
        capture_code_snippets: bool = True,
        recursion_limit: int = 3000,
        collect_errors: bool = True
    ):
        self.logger = logger or self._create_default_logger()
        self.error_handler = error_handler
        self.capture_code_snippets = capture_code_snippets
        self.original_recursion_limit = sys.getrecursionlimit()
        self.recursion_limit = recursion_limit
        self.collect_errors = collect_errors
        self.errors = [] if collect_errors else None

    def _create_default_logger(self) -> logging.Logger:
        logger = logging.getLogger('safe_parser')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    @contextmanager
    def _custom_recursion_limit(self):
        try:
            sys.setrecursionlimit(self.recursion_limit)
            yield
        finally:
            sys.setrecursionlimit(self.original_recursion_limit)

    def parse_file(self, file_path: Path) -> Optional[ast.AST]:
        try:
            with self._custom_recursion_limit():
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                return ast.parse(code, filename=str(file_path))
        except SyntaxError as e:
            self._handle_syntax_error(file_path, e, code if 'code' in locals() else None)
        except UnicodeDecodeError as e:
            self._handle_unicode_error(file_path, e)
        except RecursionError as e:
            self._handle_recursion_error(file_path, e)
        except Exception as e:
            self._handle_generic_error(file_path, e)
        return None

    def safe_parse_file(self, file_path: Path) -> List[CodeElement]:
        """Safely parse file and extract CodeElement objects using ASTParser."""
        tree = self.parse_file(file_path)
        if tree is None:
            return []
        parser = ASTParser()
        return parser.parse(tree, file_path=str(file_path))

    def _get_code_snippet(self, code: str, line_number: int) -> str:
        if not code or not self.capture_code_snippets:
            return None
        lines = code.splitlines()
        start = max(0, line_number - 3)
        end = min(len(lines), line_number + 2)
        snippet_lines = []
        for i in range(start, end):
            prefix = ">>> " if i == line_number - 1 else "    "
            snippet_lines.append(f"{prefix}{i+1}: {lines[i]}")
        return "\n".join(snippet_lines)

    def _handle_syntax_error(self, file_path: Path, error: SyntaxError, code: Optional[str] = None) -> None:
        snippet = self._get_code_snippet(code, error.lineno) if code else None
        self._log_error(file_path, "SyntaxError", str(error), error.lineno, error.offset, None, snippet)

    def _handle_unicode_error(self, file_path: Path, error: UnicodeDecodeError) -> None:
        self._log_error(file_path, "UnicodeDecodeError", f"Unicode decode error: {error}")

    def _handle_recursion_error(self, file_path: Path, error: RecursionError) -> None:
        self._log_error(file_path, "RecursionError", f"Maximum recursion depth exceeded: {error}")

    def _handle_generic_error(self, file_path: Path, error: Exception) -> None:
        tb_str = traceback.format_exc()
        self._log_error(file_path, type(error).__name__, f"Unexpected error during parsing: {error}", traceback=tb_str)

    def _log_error(
        self,
        file_path: Path,
        error_type: str,
        message: str,
        line_number: Optional[int] = None,
        column: Optional[int] = None,
        traceback: Optional[str] = None,
        code_snippet: Optional[str] = None
    ) -> None:
        error = ParsingError(
            file_path=file_path,
            error_type=error_type,
            error_message=message,
            line_number=line_number,
            column=column,
            traceback=traceback,
            code_snippet=code_snippet
        )
        location = f" at line {line_number}" if line_number else ""
        self.logger.error(f"Error parsing {file_path}{location}: {error_type}: {message}")
        if code_snippet:
            self.logger.debug(f"Code context:\n{code_snippet}")
        if traceback:
            self.logger.debug(f"Traceback:\n{traceback}")
        if self.error_handler:
            self.error_handler(error)
        if self.collect_errors and self.errors is not None:
            self.errors.append(error)

    def get_errors(self) -> List[ParsingError]:
        return self.errors if self.collect_errors and self.errors is not None else []

    def clear_errors(self) -> None:
        if self.errors is not None:
            self.errors.clear()
