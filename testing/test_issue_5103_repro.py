import pytest

def test_issue_reproduction():
    """Test that all() calls should provide detailed failure information."""
    # This should fail and show which specific element caused the failure
    # Currently pytest doesn't unroll the iterable in all() calls
    numbers = [2, 4, 5, 8, 10]
    
    # This assertion will fail because 5 is odd, but pytest won't tell us
    # which specific number caused the failure - it will just say the all() call failed
    assert all(x % 2 == 0 for x in numbers), "All numbers should be even"
    
    # Similarly for any() - this should also provide better failure info
    # but currently doesn't
    other_numbers = [1, 3, 5, 7]
    assert any(x % 2 == 0 for x in other_numbers), "At least one number should be even"