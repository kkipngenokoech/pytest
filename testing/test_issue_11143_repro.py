import tempfile
import textwrap
from pathlib import Path

import pytest

from _pytest.assertion.rewrite import _rewrite_test
from _pytest.config import Config


def test_issue_reproduction():
    """Test that rewriting fails when first expression is a number mistaken as docstring."""
    # Create a temporary Python file that starts with a numeric literal
    test_content = textwrap.dedent("""\
        42
        
        def test_something():
            assert True
        """)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        f.flush()
        
        # Create a minimal config
        config = Config.fromdictargs({}, [])
        
        # This should fail with TypeError: argument of type 'int' is not iterable
        # when the rewriter tries to check if test names are in the numeric literal
        try:
            _rewrite_test(Path(f.name), config)
        except TypeError as e:
            if "argument of type 'int' is not iterable" in str(e):
                # This is the expected failure - the bug is reproduced
                raise
            else:
                # Different TypeError, re-raise
                raise
        finally:
            Path(f.name).unlink()