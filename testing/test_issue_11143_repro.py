import tempfile
import textwrap
from pathlib import Path

import pytest

from _pytest.assertion.rewrite import rewrite_asserts
import ast


def test_issue_reproduction():
    """Test that rewrite doesn't fail when first expression is a number."""
    # Create a test file content that starts with a number
    source_code = textwrap.dedent("""\
        123
        
        def test_something():
            assert True
        """)
    
    # Parse the source code into an AST
    tree = ast.parse(source_code, filename="test_file.py")
    
    # This should not raise a TypeError about 'int' not being iterable
    # The bug occurs when rewrite_asserts tries to process the numeric literal
    # as if it were a docstring
    rewrite_asserts(tree, source_code.encode(), "test_file.py", None)