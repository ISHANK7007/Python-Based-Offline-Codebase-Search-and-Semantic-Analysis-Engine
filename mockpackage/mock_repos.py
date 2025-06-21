from index.codebase_index import CodebaseIndex

def test_nested_function_detection(deeply_nested_repo):
    """Test that the indexer can handle deeply nested functions."""
    index = CodebaseIndex(deeply_nested_repo)
    nested_functions = index.query(type="function", max_depth=5)
    assert len(nested_functions) > 0

def test_docstring_reporting(missing_docstrings_repo):
    """Test that missing docstrings are correctly identified."""
    index = CodebaseIndex(missing_docstrings_repo)
    undocumented = index.query(has_docstring=False)
    documented = index.query(has_docstring=True)
    assert len(undocumented) > 0 and len(documented) > 0

def test_decorator_argument_parsing(decorated_repo):
    """Test parsing of complex decorator arguments."""
    index = CodebaseIndex(decorated_repo)
    functions = index.query(decorator_match="requires(permissions=*)")
    assert all(
        any("permissions" in arg for arg in func.decorators[0].args)
        for func in functions if func.decorators
    )
