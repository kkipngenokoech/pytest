def test_issue_reproduction():
    """Test that all() assertions provide poor error reporting."""
    even_stevens = list(range(1, 10, 2))  # [1, 3, 5, 7, 9] - all odd numbers
    
    # This assertion will fail because none of the numbers are even
    # The current implementation will show a useless error message
    # like "assert False" instead of showing which number failed
    assert all(x % 2 == 0 for x in even_stevens)