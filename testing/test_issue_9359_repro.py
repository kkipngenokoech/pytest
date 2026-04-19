import sys
import pytest
from _pytest._code.source import Source

def test_issue_reproduction():
    """Test that assertion error context doesn't include extra lines in Python 3.9+"""
    # Create a test source with a decorator followed by an assertion
    source_lines = [
        "@pytest.fixture",
        "def test_func():",
        "    assert False, 'test message'"
    ]
    
    source = Source(source_lines)
    
    # Get the statement range for the assertion line (line 2, 0-indexed)
    assertion_lineno = 2
    start, end = source.getstatementrange(assertion_lineno)
    
    # The statement should only include the assertion line itself,
    # not the decorator from the previous function
    statement = source[start:end]
    
    # In Python 3.9+, this incorrectly includes the decorator line
    # The bug causes start to be 0 instead of 2, including the decorator
    if sys.version_info >= (3, 9):
        # This assertion will FAIL on buggy code because it includes extra lines
        assert len(statement.lines) == 1, f"Expected 1 line but got {len(statement.lines)}: {statement.lines}"
        assert statement.lines[0].strip() == "assert False, 'test message'", f"Expected assertion line but got: {statement.lines[0]}"
    else:
        # On Python < 3.9, this should work correctly
        assert len(statement.lines) == 1
        assert statement.lines[0].strip() == "assert False, 'test message'"