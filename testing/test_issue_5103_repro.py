import pytest

def test_issue_reproduction():
    """Test that all() calls don't provide useful failure information."""
    # This should fail but only show "assert False" instead of showing
    # which specific element in the list caused the all() to return False
    items = [1, 2, 3, 0, 5]  # 0 will make all(x > 0 for x in items) False
    
    # This assertion will fail, but won't show which item (0) caused the failure
    assert all(x > 0 for x in items)
    
    # For comparison, if we used a for loop, pytest would show exactly
    # which iteration failed, but all() doesn't provide that detail