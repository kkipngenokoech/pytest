import sys
import pytest
from _pytest._code.source import Source, getstatementrange_ast
import ast

def test_issue_reproduction():
    """Test that assertion error messages don't include extra lines in Python 3.9+."""
    # Create a test source with a decorator and assertion
    source_code = '''@pytest.fixture
def some_fixture():
    return 42

def test_function():
    x = 1
    assert x == 2
'''
    
    source = Source(source_code)
    
    # Find the line with the assertion (line 6, 0-indexed as line 5)
    assertion_lineno = 5  # "assert x == 2" line
    
    # Parse the AST
    astnode = ast.parse(str(source), "test", "exec")
    
    # Get the statement range for the assertion
    _, start, end = getstatementrange_ast(assertion_lineno, source, astnode=astnode)
    
    # Extract the lines that would be shown in the error
    error_lines = source[start:end]
    
    # The error should only show the assertion and related lines,
    # not the decorator from the fixture above
    error_text = str(error_lines).strip()
    
    # In Python 3.9+, this incorrectly includes the decorator line
    # The bug causes extra lines to be included in the statement range
    if sys.version_info >= (3, 9):
        # This assertion will fail on buggy code because it includes extra lines
        assert "@pytest.fixture" not in error_text, f"Extra decorator line included in error: {error_text}"
        # Also check that we don't get too many lines
        assert len(error_lines.lines) <= 2, f"Too many lines in assertion error: {error_lines.lines}"
    
    # The assertion line should always be present
    assert "assert x == 2" in error_text