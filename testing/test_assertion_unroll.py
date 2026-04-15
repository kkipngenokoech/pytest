"""Tests for assertion unrolling of all() and any() calls."""
import pytest


def test_all_with_list_passes():
    """Test that all() with a list of truthy values passes."""
    assert all([1, 2, 3, "hello", True])


def test_all_with_list_fails():
    """Test that all() with a list containing falsy values fails with detailed info."""
    with pytest.raises(AssertionError) as excinfo:
        assert all([1, 2, 0, 3])
    # The unrolled assertion should fail on the third element (0)
    assert "assert 0" in str(excinfo.value)


def test_all_with_generator_fails():
    """Test that all() with a generator expression fails with detailed info."""
    with pytest.raises(AssertionError) as excinfo:
        assert all(x > 0 for x in [1, 2, -1, 3])
    # Should show the specific comparison that failed
    assert "assert (-1 > 0)" in str(excinfo.value)


def test_all_with_empty_iterable():
    """Test that all() with empty iterable returns True (vacuous truth)."""
    assert all([])
    assert all(x for x in [])


def test_any_with_list_passes():
    """Test that any() with a list containing truthy values passes."""
    assert any([0, False, None, 1])


def test_any_with_list_fails():
    """Test that any() with a list of all falsy values fails."""
    with pytest.raises(AssertionError) as excinfo:
        assert any([0, False, None, ""])
    # Should indicate that no truthy value was found
    assert "assert False" in str(excinfo.value)


def test_any_with_generator_passes():
    """Test that any() with generator expression passes when condition is met."""
    assert any(x > 2 for x in [1, 2, 3, 4])


def test_any_with_generator_fails():
    """Test that any() with generator expression fails when no condition is met."""
    with pytest.raises(AssertionError) as excinfo:
        assert any(x > 10 for x in [1, 2, 3, 4])
    assert "assert False" in str(excinfo.value)


def test_any_with_empty_iterable():
    """Test that any() with empty iterable returns False."""
    with pytest.raises(AssertionError) as excinfo:
        assert any([])
    assert "assert False" in str(excinfo.value)


def test_all_with_complex_expression():
    """Test all() with more complex expressions."""
    data = [{"value": 1}, {"value": 2}, {"value": 0}]
    with pytest.raises(AssertionError) as excinfo:
        assert all(item["value"] > 0 for item in data)
    # Should show the failing comparison
    assert "assert (0 > 0)" in str(excinfo.value)


def test_any_with_complex_expression():
    """Test any() with more complex expressions."""
    data = [{"value": -1}, {"value": -2}, {"value": 5}]
    assert any(item["value"] > 0 for item in data)


def test_nested_all_any():
    """Test that nested all/any calls work correctly."""
    # This should not be unrolled since it's nested
    matrix = [[1, 2], [3, 0], [5, 6]]
    with pytest.raises(AssertionError):
        assert all(all(cell > 0 for cell in row) for row in matrix)


def test_all_any_with_message():
    """Test that custom assertion messages work with unrolled all/any."""
    with pytest.raises(AssertionError) as excinfo:
        assert all([1, 2, 0, 3]), "All values should be positive"
    assert "All values should be positive" in str(excinfo.value)
    assert "assert 0" in str(excinfo.value)


def test_regular_assertions_still_work():
    """Test that regular assertions without all/any still work normally."""
    with pytest.raises(AssertionError) as excinfo:
        assert 1 == 2
    assert "assert (1 == 2)" in str(excinfo.value)


def test_all_any_not_builtin():
    """Test that calls to non-builtin all/any functions are not unrolled."""
    def all(iterable):
        return "custom_all"
    
    def any(iterable):
        return "custom_any"
    
    # These should not be unrolled since they're not the builtin functions
    assert all([1, 2, 3]) == "custom_all"
    assert any([1, 2, 3]) == "custom_any"


def test_all_with_method_call():
    """Test all() with method calls in the iterable."""
    class Item:
        def __init__(self, value):
            self.value = value
        
        def is_positive(self):
            return self.value > 0
    
    items = [Item(1), Item(2), Item(-1)]
    with pytest.raises(AssertionError) as excinfo:
        assert all(item.is_positive() for item in items)
    assert "assert False" in str(excinfo.value)


def test_any_early_termination():
    """Test that any() stops at first truthy value."""
    def side_effect_func(x):
        # This would raise an exception if called with x=3
        if x == 3:
            raise ValueError("Should not be called")
        return x == 2
    
    # Should not raise ValueError because any() should stop at x=2
    assert any(side_effect_func(x) for x in [1, 2, 3])
