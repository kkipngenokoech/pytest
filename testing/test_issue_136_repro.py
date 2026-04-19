import ast
import tempfile
from pathlib import Path
from _pytest.assertion.rewrite import rewrite_asserts

def test_issue_reproduction():
    """Test that numeric literals at start of file are not mistaken as docstrings."""
    # Create a test file with a numeric literal as the first expression
    source_code = b"""42
assert 1 == 2
"""
    
    # Parse the source into an AST
    tree = ast.parse(source_code, filename="test_file.py")
    
    # The rewrite should not fail when the first expression is a number
    # This will fail on buggy code that mistakes the number for a docstring
    try:
        rewrite_asserts(tree, source_code, "test_file.py", None)
        # If we get here without exception, the bug is fixed
        success = True
    except (AttributeError, TypeError) as e:
        # These exceptions would occur if the rewriter tries to treat
        # the numeric literal as a string docstring
        success = False
    
    # The test should pass (success=True) when the bug is fixed
    # but will fail (success=False) on the current buggy code
    assert success, "Rewrite failed when first expression is a numeric literal"