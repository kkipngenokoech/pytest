def test_issue_reproduction():
    # Test that demonstrates poor error reporting with all() function
    items = [1, 2, 3, 4, 5]
    
    # This assertion will fail but won't show which item failed the condition
    assert all(item > 3 for item in items)
    
    # The current pytest will show something like:
    # assert False
    # which doesn't tell us that items 1, 2, 3 failed the condition item > 3