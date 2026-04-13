import tempfile
import textwrap
from pathlib import Path

import pytest

from _pytest.assertion.rewrite import rewrite_asserts
import ast


def test_issue_reproduction():
    """Test that rewriting fails when first expression is a number mistaken as docstring."""
    # Create a test file content where the first expression is a numeric literal
    source_code = textwrap.dedent("""\
        123
        
        def test_something():
            assert True
        """)
    
    # Parse the source into an AST
    tree = ast.parse(source_code, filename="test_file.py")
    
    # This should fail with TypeError: argument of type 'int' is not iterable
    # when the rewriter tries to check if the numeric literal contains docstring markers
    rewrite_asserts(tree, source_code.encode(), "test_file.py", None)