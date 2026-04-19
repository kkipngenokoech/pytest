import tempfile
import textwrap
from pathlib import Path

import pytest

from _pytest.assertion.rewrite import rewrite_asserts
import ast


def test_issue_reproduction():
    """Test that rewrite_asserts handles numeric literals as first statement without error."""
    # Create a Python file content where the first statement is a number
    source_code = textwrap.dedent("""
        123
        
        def test_something():
            assert True
    """)
    
    # Parse the source into an AST
    tree = ast.parse(source_code, filename="test_file.py")
    
    # This should not raise a TypeError about 'int' not being iterable
    # The bug occurs when rewrite_asserts tries to check if 123 is a docstring
    rewrite_asserts(tree, source_code.encode(), "test_file.py", None)