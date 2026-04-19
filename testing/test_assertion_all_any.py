"""Tests for all/any assertion rewriting."""
import pytest


def test_all_with_failing_item(testdir):
    """Test that all() shows which item failed."""
    testdir.makepyfile(
        """
        def test_all_even():
            numbers = [2, 4, 5, 6, 8]
            assert all(x % 2 == 0 for x in numbers)
        """
    )
    result = testdir.runpytest("-v")
    result.stdout.fnmatch_lines([
        "*AssertionError: all() failed at item: False*"
    ])
    assert result.ret == 1


def test_all_with_list_comprehension(testdir):
    """Test that all() works with list comprehensions."""
    testdir.makepyfile(
        """
        def test_all_positive():
            numbers = [-1, 2, 3, 4]
            assert all([x > 0 for x in numbers])
        """
    )
    result = testdir.runpytest("-v")
    result.stdout.fnmatch_lines([
        "*AssertionError: all() failed at item: False*"
    ])
    assert result.ret == 1


def test_all_with_simple_list(testdir):
    """Test that all() works with simple lists."""
    testdir.makepyfile(
        """
        def test_all_truthy():
            items = [1, 2, 0, 4]
            assert all(items)
        """
    )
    result = testdir.runpytest("-v")
    result.stdout.fnmatch_lines([
        "*AssertionError: all() failed at item: 0*"
    ])
    assert result.ret == 1


def test_all_passes(testdir):
    """Test that all() passes when all items are truthy."""
    testdir.makepyfile(
        """
        def test_all_true():
            numbers = [2, 4, 6, 8]
            assert all(x % 2 == 0 for x in numbers)
        """
    )
    result = testdir.runpytest("-v")
    assert result.ret == 0


def test_any_with_all_false(testdir):
    """Test that any() shows meaningful message when all items are false."""
    testdir.makepyfile(
        """
        def test_any_odd():
            numbers = [2, 4, 6, 8]
            assert any(x % 2 == 1 for x in numbers)
        """
    )
    result = testdir.runpytest("-v")
    result.stdout.fnmatch_lines([
        "*AssertionError: any() failed: no true items found*"
    ])
    assert result.ret == 1


def test_any_with_simple_list(testdir):
    """Test that any() works with simple lists."""
    testdir.makepyfile(
        """
        def test_any_truthy():
            items = [0, False, None, ""]
            assert any(items)
        """
    )
    result = testdir.runpytest("-v")
    result.stdout.fnmatch_lines([
        "*AssertionError: any() failed: no true items found*"
    ])
    assert result.ret == 1


def test_any_passes(testdir):
    """Test that any() passes when at least one item is truthy."""
    testdir.makepyfile(
        """
        def test_any_has_odd():
            numbers = [2, 4, 5, 6]
            assert any(x % 2 == 1 for x in numbers)
        """
    )
    result = testdir.runpytest("-v")
    assert result.ret == 0


def test_all_empty_iterable(testdir):
    """Test that all() with empty iterable returns True."""
    testdir.makepyfile(
        """
        def test_all_empty():
            assert all([])
            assert all(x > 0 for x in [])
        """
    )
    result = testdir.runpytest("-v")
    assert result.ret == 0


def test_any_empty_iterable(testdir):
    """Test that any() with empty iterable returns False."""
    testdir.makepyfile(
        """
        def test_any_empty():
            assert not any([])
            assert not any(x > 0 for x in [])
        """
    )
    result = testdir.runpytest("-v")
    assert result.ret == 0


def test_nested_all_any(testdir):
    """Test that nested all/any calls work correctly."""
    testdir.makepyfile(
        """
        def test_nested():
            matrix = [[1, 2], [3, 0], [5, 6]]
            assert all(any(x > 0 for x in row) for row in matrix)
        """
    )
    result = testdir.runpytest("-v")
    assert result.ret == 0


def test_all_with_custom_message(testdir):
    """Test that all() works with custom assertion messages."""
    testdir.makepyfile(
        """
        def test_all_with_msg():
            numbers = [2, 4, 5, 6]
            assert all(x % 2 == 0 for x in numbers), "Not all numbers are even"
        """
    )
    result = testdir.runpytest("-v")
    result.stdout.fnmatch_lines([
        "*AssertionError: Not all numbers are even*",
        "*all() failed at item: False*"
    ])
    assert result.ret == 1


def test_any_with_custom_message(testdir):
    """Test that any() works with custom assertion messages."""
    testdir.makepyfile(
        """
        def test_any_with_msg():
            numbers = [2, 4, 6, 8]
            assert any(x % 2 == 1 for x in numbers), "No odd numbers found"
        """
    )
    result = testdir.runpytest("-v")
    result.stdout.fnmatch_lines([
        "*AssertionError: No odd numbers found*",
        "*any() failed: no true items found*"
    ])
    assert result.ret == 1


def test_all_any_not_rewritten_in_non_assert(testdir):
    """Test that all/any are not rewritten outside of assert statements."""
    testdir.makepyfile(
        """
        def test_normal_all_any():
            numbers = [1, 2, 3, 4]
            result1 = all(x > 0 for x in numbers)
            result2 = any(x > 5 for x in numbers)
            assert result1 is True
            assert result2 is False
        """
    )
    result = testdir.runpytest("-v")
    assert result.ret == 0


def test_all_with_string_items(testdir):
    """Test that all() works with string items and shows them properly."""
    testdir.makepyfile(
        """
        def test_all_strings():
            words = ["hello", "world", "", "test"]
            assert all(words)
        """
    )
    result = testdir.runpytest("-v")
    result.stdout.fnmatch_lines([
        "*AssertionError: all() failed at item: ''*"
    ])
    assert result.ret == 1
