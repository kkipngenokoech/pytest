"""Tests for assertion rewriting."""
import ast
import sys
import textwrap
from pathlib import Path

import pytest

from _pytest.assertion.rewrite import rewrite_asserts


class TestAssertionRewrite:
    def test_numeric_literal_at_start_of_file(self, tmp_path):
        """Test that files starting with numeric literals don't cause TypeError during rewriting."""
        # Create a test file that starts with a numeric literal
        test_file = tmp_path / "test_numeric_start.py"
        test_file.write_text(textwrap.dedent("""
            123
            
            def test_something():
                assert True
        """).strip())
        
        # Read and parse the file
        source = test_file.read_bytes()
        tree = ast.parse(source, filename=str(test_file))
        
        # This should not raise a TypeError
        rewrite_asserts(tree, source, str(test_file), None)
        
        # Verify the tree is still valid
        assert isinstance(tree, ast.Module)
        assert len(tree.body) >= 2  # numeric literal + function
        
    def test_string_literal_at_start_of_file(self, tmp_path):
        """Test that files starting with string literals work correctly."""
        # Create a test file that starts with a string literal (docstring)
        test_file = tmp_path / "test_string_start.py"
        test_file.write_text(textwrap.dedent("""
            """This is a docstring"""
            
            def test_something():
                assert True
        """).strip())
        
        # Read and parse the file
        source = test_file.read_bytes()
        tree = ast.parse(source, filename=str(test_file))
        
        # This should work fine
        rewrite_asserts(tree, source, str(test_file), None)
        
        # Verify the tree is still valid
        assert isinstance(tree, ast.Module)
        assert len(tree.body) >= 2  # docstring + function
        
    def test_rewrite_disabled_docstring(self, tmp_path):
        """Test that PYTEST_DONT_REWRITE in docstring disables rewriting."""
        # Create a test file with PYTEST_DONT_REWRITE in docstring
        test_file = tmp_path / "test_disabled.py"
        test_file.write_text(textwrap.dedent("""
            """PYTEST_DONT_REWRITE"""
            
            def test_something():
                assert False, "This should not be rewritten"
        """).strip())
        
        # Read and parse the file
        source = test_file.read_bytes()
        tree = ast.parse(source, filename=str(test_file))
        
        # Store original tree for comparison
        original_body_count = len(tree.body)
        
        # Rewrite - should be disabled due to docstring
        rewrite_asserts(tree, source, str(test_file), None)
        
        # Tree should be unchanged (no rewriting occurred)
        assert len(tree.body) == original_body_count
        
    def test_various_literal_types_at_start(self, tmp_path):
        """Test various literal types at the start of files."""
        literals = [
            "123",  # int
            "123.45",  # float
            "True",  # bool
            "None",  # None
            "[1, 2, 3]",  # list
            "{1, 2, 3}",  # set
            "{1: 2}",  # dict
        ]
        
        for i, literal in enumerate(literals):
            test_file = tmp_path / f"test_literal_{i}.py"
            test_file.write_text(textwrap.dedent(f"""
                {literal}
                
                def test_something():
                    assert True
            """).strip())
            
            # Read and parse the file
            source = test_file.read_bytes()
            tree = ast.parse(source, filename=str(test_file))
            
            # This should not raise any errors
            rewrite_asserts(tree, source, str(test_file), None)
            
            # Verify the tree is still valid
            assert isinstance(tree, ast.Module)
            assert len(tree.body) >= 2  # literal + function
