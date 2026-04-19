"""Tests for assertion unrolling of all() and any() calls."""
import pytest


class TestAllAnyUnrolling:
    """Test that all() and any() calls are unrolled for better error messages."""

    def test_all_with_failing_item(self):
        """Test that all() shows which specific item failed."""
        with pytest.raises(AssertionError) as excinfo:
            numbers = [2, 4, 6, 7, 8]
            assert all(x % 2 == 0 for x in numbers)
        
        # The error should show information about the failing item (7)
        assert "7" in str(excinfo.value)

    def test_all_with_list_comprehension(self):
        """Test all() with a list comprehension."""
        with pytest.raises(AssertionError) as excinfo:
            numbers = [1, 3, 5, 6, 7]
            assert all([x % 2 == 1 for x in numbers])
        
        # Should show information about the failing item
        assert "False" in str(excinfo.value)

    def test_all_with_simple_list(self):
        """Test all() with a simple list of booleans."""
        with pytest.raises(AssertionError) as excinfo:
            values = [True, True, False, True]
            assert all(values)
        
        assert "False" in str(excinfo.value)

    def test_any_with_all_false(self):
        """Test that any() shows information when all items are False."""
        with pytest.raises(AssertionError) as excinfo:
            numbers = [2, 4, 6, 8]
            assert any(x % 2 == 1 for x in numbers)
        
        # Should indicate that no item was True
        assert "assert False" in str(excinfo.value) or "AssertionError" in str(excinfo.value)

    def test_any_with_simple_list_all_false(self):
        """Test any() with a simple list of all False values."""
        with pytest.raises(AssertionError) as excinfo:
            values = [False, False, False]
            assert any(values)
        
        assert "assert False" in str(excinfo.value) or "AssertionError" in str(excinfo.value)

    def test_all_passes_when_all_true(self):
        """Test that all() passes when all items are True."""
        numbers = [2, 4, 6, 8]
        assert all(x % 2 == 0 for x in numbers)
        
        values = [True, True, True]
        assert all(values)

    def test_any_passes_when_at_least_one_true(self):
        """Test that any() passes when at least one item is True."""
        numbers = [1, 2, 4, 6]
        assert any(x % 2 == 1 for x in numbers)
        
        values = [False, True, False]
        assert any(values)

    def test_all_with_empty_iterable(self):
        """Test all() with empty iterable (should pass)."""
        assert all([])
        assert all(x > 0 for x in [])

    def test_any_with_empty_iterable(self):
        """Test any() with empty iterable (should fail)."""
        with pytest.raises(AssertionError):
            assert any([])
        
        with pytest.raises(AssertionError):
            assert any(x > 0 for x in [])

    def test_nested_all_any_calls(self):
        """Test nested all/any calls."""
        data = [[True, True], [True, False], [True, True]]
        
        with pytest.raises(AssertionError):
            assert all(all(row) for row in data)

    def test_all_any_with_custom_message(self):
        """Test all/any with custom assertion messages."""
        with pytest.raises(AssertionError) as excinfo:
            numbers = [1, 2, 3, 4]
            assert all(x % 2 == 0 for x in numbers), "Not all numbers are even"
        
        # Custom message should still be preserved
        assert "Not all numbers are even" in str(excinfo.value)

    def test_complex_generator_expression(self):
        """Test with more complex generator expressions."""
        with pytest.raises(AssertionError):
            data = [{'value': 1}, {'value': 2}, {'value': 3}]
            assert all(item['value'] % 2 == 0 for item in data)

    def test_all_with_string_iterable(self):
        """Test all() with string characters."""
        with pytest.raises(AssertionError):
            text = "hello"
            assert all(c.isupper() for c in text)

    def test_any_with_string_iterable(self):
        """Test any() with string characters."""
        text = "hello"
        assert any(c == 'e' for c in text)
        
        with pytest.raises(AssertionError):
            assert any(c.isupper() for c in text)

    def test_all_any_not_rewritten_in_other_contexts(self):
        """Test that all/any are only rewritten in assert statements."""
        # These should work normally without rewriting
        numbers = [1, 2, 3, 4]
        result1 = all(x > 0 for x in numbers)
        result2 = any(x % 2 == 0 for x in numbers)
        
        assert result1 is True
        assert result2 is True
        
        # In if statements, should also work normally
        if all(x > 0 for x in numbers):
            pass
        else:
            pytest.fail("Should not reach here")

    def test_builtin_all_any_still_work(self):
        """Test that builtin all/any functions still work in non-assert contexts."""
        # Test that we didn't break the builtin functions
        assert all([True, True, True]) is True
        assert all([True, False, True]) is False
        assert any([False, False, False]) is False
        assert any([False, True, False]) is True
        
        # Test with generators
        assert all(x > 0 for x in [1, 2, 3]) is True
        assert any(x < 0 for x in [1, 2, 3]) is False
