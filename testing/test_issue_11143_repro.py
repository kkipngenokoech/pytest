import tempfile
import os
import pytest
from _pytest.assertion.rewrite import rewrite_asserts
import ast

def test_issue_reproduction():
    """Test that rewrite_asserts handles numeric literals as first expression without error."""
    # Create a test file content where the first expression is a number
    test_content = b"42\nassert True"
    
    # Parse the content into an AST
    tree = ast.parse(test_content, filename="test_file.py")
    
    # This should not raise TypeError: argument of type 'int' is not iterable
    # The bug occurs when rewrite_asserts tries to check if the first expression
    # (which is the number 42) is a docstring by doing string operations on it
    rewrite_asserts(tree, test_content, "test_file.py", None)