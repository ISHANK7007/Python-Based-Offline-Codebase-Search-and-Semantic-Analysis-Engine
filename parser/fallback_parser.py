# parser/fallback_parser.py
import os
import io
import re
import ast
import tokenize
import logging
import chardet
from pathlib import Path
from typing import Optional, Tuple, Dict, List, Any, Union
import traceback
from models import ModuleElement, ElementKind  # Add this to fix missing names

from models import ElementType, CodeElement, ElementReference, Location
from models.syntax_nodes import SyntaxNodeInfo  # adjusted to correct filename

from .safe_parser import ParsingError


class FallbackParser:
    """
    Fallback parser for handling problematic Python files.
    
    This class implements a multi-stage fallback strategy for parsing
    files that cannot be correctly processed by the standard AST parser.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the fallback parser."""
        self.logger = logger or logging.getLogger(__name__)
    
    def parse_with_fallbacks(self, file_path: Path) -> Tuple[Optional[ast.AST], Optional[ParsingError], Dict[str, Any]]:
        """
        Attempt to parse a file using progressively more aggressive fallbacks.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Tuple containing:
            - AST if successful, None otherwise
            - ParsingError if parsing failed completely
            - Metadata about the fallback process
        """
        metadata = {
            "fallback_used": False,
            "fallback_level": 0,
            "original_error": None,
            "encoding_detected": None,
            "sanitized_lines": 0,
            "issues_found": []
        }
        
        # Attempt 1: Standard parsing
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            ast_tree = ast.parse(source, filename=str(file_path))
            return ast_tree, None, metadata
            
        except UnicodeDecodeError as e:
            # Encoding issue
            metadata["fallback_used"] = True
            metadata["fallback_level"] = 1
            metadata["original_error"] = str(e)
            metadata["issues_found"].append(f"Unicode decode error: {e}")
            
            # Try to detect encoding
            detected_encoding = self._detect_encoding(file_path)
            metadata["encoding_detected"] = detected_encoding
            
            if detected_encoding:
                try:
                    with open(file_path, 'r', encoding=detected_encoding) as f:
                        source = f.read()
                    
                    ast_tree = ast.parse(source, filename=str(file_path))
                    self.logger.info(f"Successfully parsed {file_path} with detected encoding: {detected_encoding}")
                    return ast_tree, None, metadata
                    
                except Exception as e2:
                    metadata["issues_found"].append(f"Failed with detected encoding: {e2}")
            
            # If we get here, encoding detection didn't work, fall through to next fallback
            
        except SyntaxError as e:
            # Syntax error - record details for fallback
            metadata["fallback_used"] = True
            metadata["fallback_level"] = 2
            metadata["original_error"] = str(e)
            metadata["issues_found"].append(f"Syntax error at line {e.lineno}: {e.msg}")
            
            # Fall through to sanitization
            
        except Exception as e:
            # Other error - record details for fallback
            metadata["fallback_used"] = True
            metadata["fallback_level"] = 2
            metadata["original_error"] = str(e)
            metadata["issues_found"].append(f"Unexpected error: {e}")
            
            # Fall through to sanitization
        
        # Attempt 2: Sanitize and reparse
        try:
            sanitized_source, sanitize_meta = self._sanitize_source(file_path)
            metadata.update(sanitize_meta)
            
            if sanitized_source:
                try:
                    ast_tree = ast.parse(sanitized_source, filename=str(file_path))
                    self.logger.info(f"Successfully parsed {file_path} after sanitization")
                    return ast_tree, None, metadata
                except Exception as e:
                    metadata["issues_found"].append(f"Failed after sanitization: {e}")
            
        except Exception as e:
            metadata["issues_found"].append(f"Error during sanitization: {e}")
        
        # Attempt 3: Tokenize-based partial parsing
        try:
            token_based_ast, token_meta = self._parse_with_tokens(file_path)
            metadata.update(token_meta)
            metadata["fallback_level"] = 3
            
            if token_based_ast:
                self.logger.info(f"Successfully created partial AST for {file_path} using tokenizer")
                return token_based_ast, None, metadata
                
        except Exception as e:
            metadata["issues_found"].append(f"Error during token-based parsing: {e}")
        
        # Attempt 4: Create stub AST with minimal information
        stub_ast = self._create_stub_ast(file_path, metadata)
        metadata["fallback_level"] = 4
        
        # Create a parsing error to record the failure
        error = ParsingError(
            file_path=file_path,
            error_type="MultipleFallbackFailure",
            error_message=f"All parsing approaches failed: {', '.join(metadata['issues_found'])}",
            traceback=traceback.format_exc()
        )
        
        return stub_ast, error, metadata
    
    def _detect_encoding(self, file_path: Path) -> Optional[str]:
        """
        Detect the encoding of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding or None
        """
        try:
            # Read a chunk of the file as bytes
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read up to 10KB
            
            # Try to detect encoding with chardet
            result = chardet.detect(raw_data)
            if result and result['confidence'] > 0.7:
                return result['encoding']
            
            # Try to detect with tokenize as a fallback
            try:
                with open(file_path, 'rb') as f:
                    encoding = tokenize.detect_encoding(f.readline)[0]
                return encoding
            except:
                pass
                
            return None
            
        except Exception as e:
            self.logger.warning(f"Error detecting encoding for {file_path}: {e}")
            return None
    
    def _sanitize_source(self, file_path: Path) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Attempt to sanitize source code with various fixes.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of sanitized source and metadata
        """
        metadata = {
            "sanitized_lines": 0,
            "indentation_fixed": False,
            "encoding_issues_fixed": False,
            "control_chars_removed": False,
            "bom_removed": False,
            "sanitization_details": []
        }
        
        try:
            # First, try to read with permissive encoding
            source_lines = []
            encoding_issues = False
            
            try:
                # Try UTF-8 first
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    source_lines = f.readlines()
            except UnicodeError:
                # Fall back to latin-1 which can read any byte
                with open(file_path, 'r', encoding='latin-1') as f:
                    source_lines = f.readlines()
                encoding_issues = True
                metadata["sanitization_details"].append("Used latin-1 encoding fallback")
            
            if encoding_issues:
                metadata["encoding_issues_fixed"] = True
            
            # Check for and remove BOM
            if source_lines and source_lines[0].startswith('\ufeff'):
                source_lines[0] = source_lines[0][1:]
                metadata["bom_removed"] = True
                metadata["sanitization_details"].append("Removed UTF-8 BOM")
            
            # Track sanitized lines
            sanitized_count = 0
            
            # Process line by line
            for i in range(len(source_lines)):
                original_line = source_lines[i]
                
                # Fix mixed tabs and spaces
                if '\t' in original_line and ' ' in original_line.lstrip('\t'):
                    # Replace tabs with 4 spaces
                    source_lines[i] = original_line.replace('\t', '    ')
                    sanitized_count += 1
                    metadata["indentation_fixed"] = True
                    metadata["sanitization_details"].append(f"Fixed mixed tabs/spaces at line {i+1}")
                
                # Remove control characters
                cleaned_line = ''.join(c if c >= ' ' else ' ' for c in source_lines[i])
                if cleaned_line != source_lines[i]:
                    source_lines[i] = cleaned_line
                    sanitized_count += 1
                    metadata["control_chars_removed"] = True
                    metadata["sanitization_details"].append(f"Removed control chars at line {i+1}")
            
            # Handle indentation issues across the file
            leading_whitespace = [len(line) - len(line.lstrip()) for line in source_lines if line.strip()]
            if leading_whitespace and max(leading_whitespace) > 0:
                # Check for inconsistent indentation units
                indent_units = set()
                for i in range(1, len(source_lines)):
                    if not source_lines[i].strip():
                        continue  # Skip empty lines
                        
                    indent = len(source_lines[i]) - len(source_lines[i].lstrip())
                    if indent > 0:
                        # Find the indentation unit (number of spaces that makes up one level)
                        for j in range(1, indent+1):
                            if indent % j == 0 and indent // j <= 10:  # Reasonable indentation levels
                                indent_units.add(j)
                
                # If multiple indent units found, normalize to 4 spaces
                if len(indent_units) > 1:
                    # Try to normalize to the most common unit
                    for i in range(len(source_lines)):
                        line = source_lines[i]
                        if not line.strip():
                            continue
                            
                        indent = len(line) - len(line.lstrip())
                        if indent > 0:
                            # Normalize to 4 spaces per level
                            indent_level = indent // min(indent_units)
                            source_lines[i] = ' ' * (indent_level * 4) + line.lstrip()
                            sanitized_count += 1
                    
                    metadata["indentation_fixed"] = True
                    metadata["sanitization_details"].append(f"Normalized indentation units: {indent_units}")
            
            metadata["sanitized_lines"] = sanitized_count
            
            if sanitized_count > 0:
                return ''.join(source_lines), metadata
            else:
                return None, metadata
            
        except Exception as e:
            self.logger.warning(f"Error during source sanitization for {file_path}: {e}")
            metadata["sanitization_details"].append(f"Sanitization error: {e}")
            return None, metadata
    
    def _parse_with_tokens(self, file_path: Path) -> Tuple[Optional[ast.AST], Dict[str, Any]]:
        """
        Create a simplified AST using the tokenize module.
        
        This approach extracts top-level definitions even when the full file
        cannot be parsed due to syntax errors in some functions or classes.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of AST (or None) and metadata
        """
        metadata = {
            "token_based_parsing": True,
            "elements_extracted": 0,
            "syntax_errors_bypassed": 0
        }
        
        try:
            # Read the file as bytes for tokenize
            with open(file_path, 'rb') as f:
                # Create a list to hold mock AST nodes
                module_body = []
                
                # Track indentation for structure
                indentation_stack = [0]
                current_class = None
                
                # State for tracking definitions
                in_function_def = False
                in_class_def = False
                current_element_name = None
                current_element_line = 0
                current_element_indent = 0
                syntax_errors = 0
                
                # Process tokens
                tokens = list(tokenize.tokenize(f.readline))
                
                i = 0
                while i < len(tokens):
                    token = tokens[i]
                    
                    # Track indentation
                    if token.type == tokenize.INDENT:
                        indentation_stack.append(token.start[1])
                    elif token.type == tokenize.DEDENT:
                        if indentation_stack:
                            indentation_stack.pop()
                            
                            # Check if we're exiting a definition
                            if in_function_def and len(indentation_stack) <= current_element_indent:
                                in_function_def = False
                            if in_class_def and len(indentation_stack) <= current_element_indent:
                                in_class_def = False
                                current_class = None
                    
                    # Look for top-level definitions
                    elif token.type == tokenize.NAME:
                        if token.string == 'def' and not in_function_def:
                            # Found a function definition
                            if i + 1 < len(tokens) and tokens[i+1].type == tokenize.NAME:
                                current_element_name = tokens[i+1].string
                                current_element_line = token.start[0]
                                current_element_indent = len(indentation_stack)
                                in_function_def = True
                                
                                # Create a mock function node
                                func_node = self._create_mock_function(
                                    current_element_name, 
                                    current_element_line,
                                    parent_class=current_class
                                )
                                
                                if current_class is None:
                                    module_body.append(func_node)
                                metadata["elements_extracted"] += 1
                                
                        elif token.string == 'class' and not in_class_def:
                            # Found a class definition
                            if i + 1 < len(tokens) and tokens[i+1].type == tokenize.NAME:
                                current_element_name = tokens[i+1].string
                                current_element_line = token.start[0]
                                current_element_indent = len(indentation_stack)
                                in_class_def = True
                                current_class = current_element_name
                                
                                # Create a mock class node
                                class_node = self._create_mock_class(
                                    current_element_name, 
                                    current_element_line
                                )
                                module_body.append(class_node)
                                metadata["elements_extracted"] += 1
                    
                    # Look for syntax errors
                    elif token.type == tokenize.ERRORTOKEN:
                        syntax_errors += 1
                    
                    i += 1
                
                metadata["syntax_errors_bypassed"] = syntax_errors
                
                if module_body:
                    # Create a Module node
                    module = ast.Module(body=module_body, type_ignores=[])
                    ast.fix_missing_locations(module)
                    return module, metadata
                    
                return None, metadata
                
        except Exception as e:
            self.logger.warning(f"Error during token-based parsing for {file_path}: {e}")
            metadata["token_parse_error"] = str(e)
            return None, metadata
    
    def _create_mock_function(self, name: str, lineno: int, parent_class: Optional[str] = None) -> ast.FunctionDef:
        """Create a minimal mock function node for the AST."""
        # Create a pass statement for the body
        pass_stmt = ast.Pass()
        pass_stmt.lineno = lineno + 1
        pass_stmt.col_offset = 4
        
        # Create function parameters
        if parent_class and name == '__init__':
            # For constructors, add self parameter
            self_arg = ast.arg(arg='self', annotation=None)
            self_arg.lineno = lineno
            self_arg.col_offset = 8
            
            arguments = ast.arguments(
                posonlyargs=[],
                args=[self_arg],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
                vararg=None,
                kwarg=None
            )
        else:
            arguments = ast.arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
                vararg=None,
                kwarg=None
            )
        
        # Create the function definition
        func_def = ast.FunctionDef(
            name=name,
            args=arguments,
            body=[pass_stmt],
            decorator_list=[],
            returns=None,
        )
        func_def.lineno = lineno
        func_def.col_offset = 0
        
        return func_def
    
    def _create_mock_class(self, name: str, lineno: int) -> ast.ClassDef:
        """Create a minimal mock class node for the AST."""
        # Create a pass statement for the body
        pass_stmt = ast.Pass()
        pass_stmt.lineno = lineno + 1
        pass_stmt.col_offset = 4
        
        # Create the class definition
        class_def = ast.ClassDef(
            name=name,
            bases=[],
            keywords=[],
            body=[pass_stmt],
            decorator_list=[]
        )
        class_def.lineno = lineno
        class_def.col_offset = 0
        
        return class_def
    
    def _create_stub_ast(self, file_path: Path, metadata: Dict[str, Any]) -> ast.Module:
        """
        Create a minimal stub AST with a module docstring containing error information.
        
        This is the last resort when all other parsing attempts fail.
        """
        # Create a docstring with error information
        issues = metadata.get('issues_found', [])
        docstring = f"# PARSE ERROR: Could not parse {file_path.name}\n"
        docstring += f"# Issues: {'; '.join(issues)}\n"
        
        # Create a string node for the docstring
        str_node = ast.Constant(value=docstring)
        str_node.lineno = 1
        str_node.col_offset = 0
        
        # Wrap in an Expr node
        expr = ast.Expr(value=str_node)
        expr.lineno = 1
        expr.col_offset = 0
        
        # Create the module
        module = ast.Module(body=[expr], type_ignores=[])
        
        return module


class StubElementFactory:
    """
    Creates stub code elements for files that couldn't be parsed.
    
    This allows the indexer to include files that have syntax errors
    or other issues, providing at least minimal metadata.
    """
    
    @staticmethod
    def create_stub_module(file_path: Path, error: ParsingError) -> CodeElement:
        """
        Create a stub module element for a file that couldn't be parsed.
        
        Args:
            file_path: Path to the file
            error: Parsing error information
            
        Returns:
            A stub CodeElement
        """
        # Determine module name from file path
        module_name = file_path.stem
        if module_name == '__init__':
            module_name = file_path.parent.name
        
        # Create location
        location = Location(
            file_path=file_path,
            line_start=1,
            line_end=1  # We don't know the actual length
        )
        
        # Create docstring with error information
        docstring = f"ERROR: This module could not be parsed.\n"
        docstring += f"Error type: {error.error_type}\n"
        docstring += f"Message: {error.error_message}\n"
        
        if error.line_number:
            docstring += f"Location: Line {error.line_number}"
            if error.column:
                docstring += f", Column {error.column}"
            docstring += "\n"
        
        if error.code_snippet:
            docstring += f"\nCode context:\n{error.code_snippet}\n"
        
        # Create module element
        module_element = ModuleElement(
            id=f"stub:{file_path}",
            name=module_name,
            qualified_name=module_name,
            element_type=ElementType.MODULE,
            element_kind=ElementKind.MODULE,
            location=location,
            docstring=docstring,
            module_path=module_name,
            is_stub=True,
            has_parsing_error=True,
            error_type=error.error_type
        )
        
        return module_element