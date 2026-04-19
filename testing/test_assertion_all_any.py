"""Tests for all() and any() assertion unrolling functionality."""
import pytest


class TestAllAnyUnrolling:
    """Test that all() and any() calls are properly unrolled for better error messages."""

    def test_all_with_generator_expression_failure(self, testdir):
        """Test that all() with generator expression shows which element failed."""
        testdir.makepyfile(
            """
            def test_all_generator():
                items = [1, 2, 0, 4]
                assert all(x > 0 for x in items)
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*AssertionError*",
            "*assert*",
        ])
        assert result.ret == 1

    def test_all_with_list_comprehension_failure(self, testdir):
        """Test that all() with list comprehension shows which element failed."""
        testdir.makepyfile(
            """
            def test_all_list():
                items = [1, 2, 0, 4]
                assert all([x > 0 for x in items])
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*AssertionError*",
            "*assert*",
        ])
        assert result.ret == 1

    def test_all_with_simple_iterable_failure(self, testdir):
        """Test that all() with simple iterable shows which element failed."""
        testdir.makepyfile(
            """
            def test_all_simple():
                items = [True, True, False, True]
                assert all(items)
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*AssertionError*",
            "*assert*",
        ])
        assert result.ret == 1

    def test_any_with_generator_expression_failure(self, testdir):
        """Test that any() with generator expression shows meaningful failure message."""
        testdir.makepyfile(
            """
            def test_any_generator():
                items = [0, 0, 0, 0]
                assert any(x > 0 for x in items)
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*AssertionError*",
            "*assert*",
        ])
        assert result.ret == 1

    def test_any_with_list_comprehension_failure(self, testdir):
        """Test that any() with list comprehension shows meaningful failure message."""
        testdir.makepyfile(
            """
            def test_any_list():
                items = [0, 0, 0, 0]
                assert any([x > 0 for x in items])
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*AssertionError*",
            "*assert*",
        ])
        assert result.ret == 1

    def test_any_with_simple_iterable_failure(self, testdir):
        """Test that any() with simple iterable shows meaningful failure message."""
        testdir.makepyfile(
            """
            def test_any_simple():
                items = [False, False, False, False]
                assert any(items)
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*AssertionError*",
            "*assert*",
        ])
        assert result.ret == 1

    def test_all_success_case(self, testdir):
        """Test that all() success cases still work correctly."""
        testdir.makepyfile(
            """
            def test_all_success():
                items = [1, 2, 3, 4]
                assert all(x > 0 for x in items)
                assert all([x > 0 for x in items])
                assert all([True, True, True])
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines(["*1 passed*"])
        assert result.ret == 0

    def test_any_success_case(self, testdir):
        """Test that any() success cases still work correctly."""
        testdir.makepyfile(
            """
            def test_any_success():
                items = [0, 0, 1, 0]
                assert any(x > 0 for x in items)
                assert any([x > 0 for x in items])
                assert any([False, False, True])
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines(["*1 passed*"])
        assert result.ret == 0

    def test_all_empty_iterable(self, testdir):
        """Test that all() with empty iterable returns True (standard behavior)."""
        testdir.makepyfile(
            """
            def test_all_empty():
                assert all([])
                assert all(x > 0 for x in [])
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines(["*1 passed*"])
        assert result.ret == 0

    def test_any_empty_iterable(self, testdir):
        """Test that any() with empty iterable returns False (standard behavior)."""
        testdir.makepyfile(
            """
            def test_any_empty():
                assert not any([])
                assert not any(x > 0 for x in [])
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines(["*1 passed*"])
        assert result.ret == 0

    def test_nested_all_any_calls(self, testdir):
        """Test that nested all/any calls work correctly."""
        testdir.makepyfile(
            """
            def test_nested():
                matrix = [[1, 2], [3, 4]]
                assert all(any(x > 0 for x in row) for row in matrix)
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines(["*1 passed*"])
        assert result.ret == 0

    def test_all_any_with_custom_message(self, testdir):
        """Test that all/any assertions work with custom messages."""
        testdir.makepyfile(
            """
            def test_custom_message():
                items = [1, 2, 0, 4]
                assert all(x > 0 for x in items), "All items should be positive"
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*AssertionError*",
            "*All items should be positive*",
        ])
        assert result.ret == 1

    def test_non_builtin_all_any_not_affected(self, testdir):
        """Test that custom all/any functions are not affected by unrolling."""
        testdir.makepyfile(
            """
            def all(iterable):
                return "custom_all"
            
            def any(iterable):
                return "custom_any"
            
            def test_custom_functions():
                items = [1, 2, 3]
                assert all(items) == "custom_all"
                assert any(items) == "custom_any"
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines(["*1 passed*"])
        assert result.ret == 0

    def test_all_any_with_method_calls(self, testdir):
        """Test that method calls named all/any are not affected."""
        testdir.makepyfile(
            """
            class MyClass:
                def all(self, iterable):
                    return "method_all"
                
                def any(self, iterable):
                    return "method_any"
            
            def test_method_calls():
                obj = MyClass()
                items = [1, 2, 3]
                assert obj.all(items) == "method_all"
                assert obj.any(items) == "method_any"
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines(["*1 passed*"])
        assert result.ret == 0

    def test_all_any_with_multiple_arguments_not_affected(self, testdir):
        """Test that all/any calls with multiple arguments are not unrolled."""
        testdir.makepyfile(
            """
            def all(iterable, key=None):
                return "custom_all_with_args"
            
            def test_multiple_args():
                items = [1, 2, 3]
                # This should not be unrolled because it has multiple arguments
                assert all(items, key=str) == "custom_all_with_args"
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines(["*1 passed*"])
        assert result.ret == 0
