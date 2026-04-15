def test_issue_reproduction():
    # Test that demonstrates poor error reporting for all() calls
    # This should fail and show which element caused the failure, but currently doesn't
    items = [1, 2, 3, 4, 5]
    assert all(x < 4 for x in items), "Expected all items to be less than 4"
    
    # Test for any() as well
    items2 = [1, 2, 3]
    assert any(x > 5 for x in items2), "Expected at least one item to be greater than 5"