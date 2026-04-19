import pytest

def test_issue_reproduction():
    """Test that demonstrates poor error reporting for all() and any() calls."""
    # This should fail with a non-informative error message
    # showing that all() doesn't tell us which element failed
    even_stevens = list(range(1, 10, 2))  # [1, 3, 5, 7, 9] - all odd numbers
    
    # This assertion will fail but won't tell us which number is not even
    with pytest.raises(AssertionError) as exc_info:
        assert all(x % 2 == 0 for x in even_stevens)
    
    # The error message should be uninformative (just "assert False")
    # rather than telling us which specific number failed the even test
    error_msg = str(exc_info.value)
    
    # This assertion will fail because the current implementation doesn't
    # provide detailed information about which element caused all() to fail
    assert "1 % 2 == 0" in error_msg or "3 % 2 == 0" in error_msg, f"Expected detailed failure info, got: {error_msg}"