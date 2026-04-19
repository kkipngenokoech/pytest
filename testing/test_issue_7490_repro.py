import pytest

def test_issue_reproduction():
    """Test that dynamically added xfail marker should ignore test failure."""
    
    def test_dynamic_xfail(request):
        # Dynamically add xfail marker during test execution
        mark = pytest.mark.xfail(reason="dynamically added xfail")
        request.node.add_marker(mark)
        
        # This should fail but be treated as xfail due to the dynamic marker
        assert False, "This failure should be ignored due to dynamic xfail marker"
    
    # Create a mock request object with a node that can store markers
    class MockNode:
        def __init__(self):
            self.own_markers = []
            self.config = pytest.Config.fromdictargs({}, [])
            self._store = {}
        
        def add_marker(self, mark):
            self.own_markers.append(mark)
        
        def iter_markers(self, name=None):
            for marker in self.own_markers:
                if name is None or marker.name == name:
                    yield marker
    
    class MockRequest:
        def __init__(self):
            self.node = MockNode()
    
    request = MockRequest()
    
    # This should not raise an AssertionError when the xfail marker is properly handled
    # In the buggy version, the dynamic marker is ignored and the test fails
    try:
        test_dynamic_xfail(request)
        # If we get here, the test passed unexpectedly
        assert False, "Test should have been marked as xfail, not passed"
    except AssertionError as e:
        # In the buggy version, this assertion error will be raised
        # In the fixed version, it should be caught and handled as xfail
        if "This failure should be ignored" in str(e):
            # This means the dynamic xfail marker was not properly processed
            pytest.fail("Dynamic xfail marker was not processed - bug reproduced")
        else:
            # Re-raise other assertion errors
            raise