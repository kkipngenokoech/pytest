import pytest

def test_issue_reproduction():
    """Test that all() and any() calls provide detailed failure information."""
    
    # Test case that should provide detailed failure info but currently doesn't
    items = [1, 2, 3, 4, 5]
    
    # This should fail and show which specific item(s) failed the condition
    # Currently it just shows "assert False" without details about which items
    with pytest.raises(AssertionError) as exc_info:
        assert all(x < 3 for x in items)
    
    # The error message should contain information about the failing items (4, 5)
    # but currently it doesn't - it just shows generic "assert False"
    error_msg = str(exc_info.value)
    
    # This assertion will fail because the current implementation doesn't
    # provide detailed information about which items failed
    assert "4" in error_msg or "5" in error_msg, f"Expected detailed failure info, got: {error_msg}"
    
    # Test any() as well
    items2 = [2, 4, 6, 8]
    with pytest.raises(AssertionError) as exc_info2:
        assert any(x % 2 == 1 for x in items2)  # all are even, so this fails
    
    error_msg2 = str(exc_info2.value)
    # Should show details about the items that were checked
    assert "2" in error_msg2 or "even" in error_msg2, f"Expected detailed failure info, got: {error_msg2}"