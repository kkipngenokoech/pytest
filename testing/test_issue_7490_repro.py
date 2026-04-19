import pytest

def test_issue_reproduction(request):
    """Test that dynamically adding xfail marker should ignore test failure."""
    # Dynamically add xfail marker during test execution
    request.node.add_marker(pytest.mark.xfail(reason="dynamically added xfail"))
    
    # This should cause the test to be marked as xfailed, not failed
    assert False, "This failure should be ignored due to dynamic xfail marker"