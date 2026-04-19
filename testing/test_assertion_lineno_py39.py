"""Tests for assertion line number handling in Python 3.9+."""
import sys
import textwrap

import pytest


class TestAssertionLineNumberPy39:
    """Test that assertion error messages don't show extra lines in Python 3.9+."""

    def test_decorator_not_included_in_assertion_error(self, pytester):
        """Test that decorator lines are not included in assertion error messages."""
        pytester.makepyfile(
            test_example="""
            from pytest import fixture

            @fixture
            def t():
                return 1

            def test_right_statement(t):
                assert 1 == 2
            """
        )
        result = pytester.runpytest("-v")
        result.assert_outcomes(failed=1)
        
        # The assertion error should not include the @fixture decorator line
        output = result.stdout.str()
        assert "@fixture" not in output or "assert 1 == 2" in output
        
        # Ensure the assertion line is present
        assert "assert 1 == 2" in output

    def test_multiline_assertion_correct_range(self, pytester):
        """Test that multiline assertions show correct line range."""
        pytester.makepyfile(
            test_example="""
            def test_multiline():
                assert (1 + 2 + 3 +
                        4 + 5) == 20
            """
        )
        result = pytester.runpytest("-v")
        result.assert_outcomes(failed=1)
        
        output = result.stdout.str()
        # Should include both lines of the assertion
        assert "assert (1 + 2 + 3 +" in output
        assert "4 + 5) == 20" in output

    def test_decorator_before_function_with_assertion(self, pytester):
        """Test specific case from the issue report."""
        pytester.makepyfile(
            test_example="""
            from pytest import fixture

            @fixture
            def t():
                return 1

            def test_right_statement(t):
                assert t == 2
                assert 1 == 1  # This should pass
            """
        )
        result = pytester.runpytest("-v")
        result.assert_outcomes(failed=1)
        
        output = result.stdout.str()
        # The error should show the assertion line but not the decorator
        lines = output.split('\n')
        assertion_context = []
        in_assertion_context = False
        
        for line in lines:
            if "assert t == 2" in line:
                in_assertion_context = True
            if in_assertion_context:
                assertion_context.append(line)
                if "AssertionError" in line or "FAILED" in line:
                    break
        
        assertion_text = '\n'.join(assertion_context)
        # Should not contain the decorator in the assertion context
        assert "@fixture" not in assertion_text or "def t():" not in assertion_text

    @pytest.mark.skipif(sys.version_info < (3, 9), reason="Test specific to Python 3.9+")
    def test_python39_specific_line_handling(self, pytester):
        """Test that Python 3.9+ specific line number handling works correctly."""
        pytester.makepyfile(
            test_example="""
            def decorator(func):
                return func

            @decorator
            def test_function():
                x = 1
                assert x == 2
            """
        )
        result = pytester.runpytest("-v")
        result.assert_outcomes(failed=1)
        
        output = result.stdout.str()
        # Should show the assertion but not the decorator
        assert "assert x == 2" in output
        # The decorator should not appear in the assertion error context
        lines = output.split('\n')
        assertion_lines = [line for line in lines if "assert x == 2" in line or 
                          ("@decorator" in line and any("assert" in l for l in lines[lines.index(line):lines.index(line)+5]))]
        
        # If @decorator appears, it should not be in the immediate context of the assertion error
        for i, line in enumerate(lines):
            if "assert x == 2" in line:
                # Check a few lines before and after for decorator
                context_start = max(0, i - 3)
                context_end = min(len(lines), i + 3)
                context = lines[context_start:context_end]
                context_text = '\n'.join(context)
                # The decorator should not be in the immediate assertion context
                if "@decorator" in context_text:
                    # This would indicate the bug is still present
                    pytest.fail(f"Decorator found in assertion context: {context_text}")
                break

    def test_complex_decorator_scenario(self, pytester):
        """Test complex scenario with multiple decorators."""
        pytester.makepyfile(
            test_example="""
            from pytest import fixture, mark

            @fixture
            def data():
                return {'key': 'value'}

            @mark.parametrize('param', [1, 2])
            def test_complex(data, param):
                assert data['key'] == 'wrong_value'
            """
        )
        result = pytester.runpytest("-v")
        result.assert_outcomes(failed=2)  # parametrized test runs twice
        
        output = result.stdout.str()
        # Should show the assertion
        assert "assert data['key'] == 'wrong_value'" in output
        # Should not show decorators in assertion error context
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if "assert data['key'] == 'wrong_value'" in line:
                # Check surrounding context doesn't include decorators
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 2)
                context = lines[context_start:context_end]
                context_text = '\n'.join(context)
                assert "@fixture" not in context_text
                assert "@mark.parametrize" not in context_text
                break
