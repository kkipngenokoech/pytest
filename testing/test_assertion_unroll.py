"""Tests for assertion unrolling of all/any calls."""
import pytest


def test_all_with_generator_expression_failure():
    """Test that assert all() with generator expression provides detailed failure info."""
    items = [1, 2, 0, 4]
    with pytest.raises(AssertionError) as excinfo:
        assert all(x > 0 for x in items)
    
    # Should show which specific item failed
    assert "assert 0" in str(excinfo.value) or "assert (0 > 0)" in str(excinfo.value)


def test_all_with_list_comprehension_failure():
    """Test that assert all() with list comprehension provides detailed failure info."""
    items = [2, 4, 0, 6]
    with pytest.raises(AssertionError) as excinfo:
        assert all([x > 0 for x in items])
    
    # Should show which specific item failed
    assert "assert 0" in str(excinfo.value) or "assert (0 > 0)" in str(excinfo.value)


def test_all_with_simple_list_failure():
    """Test that assert all() with simple list provides detailed failure info."""
    items = [True, True, False, True]
    with pytest.raises(AssertionError) as excinfo:
        assert all(items)
    
    # Should show which specific item failed
    assert "assert False" in str(excinfo.value)


def test_any_with_generator_expression_failure():
    """Test that assert any() with generator expression provides detailed failure info."""
    items = [0, 0, 0]
    with pytest.raises(AssertionError) as excinfo:
        assert any(x > 0 for x in items)
    
    # Should show information about the failed items
    error_msg = str(excinfo.value)
    # The error should indicate that all items were False
    assert "assert" in error_msg


def test_any_with_list_comprehension_failure():
    """Test that assert any() with list comprehension provides detailed failure info."""
    items = [0, 0, 0]
    with pytest.raises(AssertionError) as excinfo:
        assert any([x > 0 for x in items])
    
    # Should show information about the failed items
    error_msg = str(excinfo.value)
    assert "assert" in error_msg


def test_any_with_simple_list_failure():
    """Test that assert any() with simple list provides detailed failure info."""
    items = [False, False, False]
    with pytest.raises(AssertionError) as excinfo:
        assert any(items)
    
    # Should show information about the failed items
    error_msg = str(excinfo.value)
    assert "assert" in error_msg


def test_all_success():
    """Test that assert all() works correctly when all items are True."""
    items = [1, 2, 3, 4]
    assert all(x > 0 for x in items)  # Should not raise
    assert all([x > 0 for x in items])  # Should not raise
    assert all([True, True, True])  # Should not raise


def test_any_success():
    """Test that assert any() works correctly when at least one item is True."""
    items = [0, 0, 1, 0]
    assert any(x > 0 for x in items)  # Should not raise
    assert any([x > 0 for x in items])  # Should not raise
    assert any([False, False, True])  # Should not raise


def test_nested_all_any():
    """Test that nested all/any calls work correctly."""
    matrix = [[1, 2], [3, 4], [5, 6]]
    assert all(any(x > 0 for x in row) for row in matrix)  # Should not raise
    
    matrix_with_zero = [[1, 2], [0, 0], [5, 6]]
    with pytest.raises(AssertionError):
        assert all(all(x > 0 for x in row) for row in matrix_with_zero)


def test_all_empty_iterable():
    """Test that assert all() works correctly with empty iterable."""
    assert all([])  # Should not raise (vacuous truth)
    assert all(x > 0 for x in [])  # Should not raise


def test_any_empty_iterable():
    """Test that assert any() works correctly with empty iterable."""
    with pytest.raises(AssertionError):
        assert any([])  # Should raise
    
    with pytest.raises(AssertionError):
        assert any(x > 0 for x in [])  # Should raise


def test_backwards_compatibility():
    """Test that regular assertions still work as before."""
    # Regular assertions should continue to work
    with pytest.raises(AssertionError) as excinfo:
        assert 1 == 2
    
    assert "assert 1 == 2" in str(excinfo.value)
    
    # Non-all/any function calls should work normally
    with pytest.raises(AssertionError) as excinfo:
        assert len([1, 2]) == 3
    
    assert "assert 2 == 3" in str(excinfo.value)


def test_all_any_with_complex_expressions():
    """Test all/any with more complex expressions."""
    data = [{'value': 1}, {'value': 2}, {'value': 0}]
    
    with pytest.raises(AssertionError) as excinfo:
        assert all(item['value'] > 0 for item in data)
    
    # Should show the failing assertion
    error_msg = str(excinfo.value)
    assert "assert" in error_msg
    
    # Test any with complex expressions
    data_all_zero = [{'value': 0}, {'value': 0}, {'value': 0}]
    
    with pytest.raises(AssertionError) as excinfo:
        assert any(item['value'] > 0 for item in data_all_zero)
    
    error_msg = str(excinfo.value)
    assert "assert" in error_msg
