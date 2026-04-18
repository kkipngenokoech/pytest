import pytest

def test_issue_reproduction():
    class SomeClass:
        def __getattribute__(self, attr):
            raise Exception("Error in __getattribute__")
    
    obj = SomeClass()
    
    # This should trigger pytest's internal error handling when it tries to repr the object
    # during test failure reporting
    with pytest.raises(Exception, match="Error in __getattribute__"):
        # Force pytest to try to display the object by making an assertion fail
        # The object will be included in the failure message, triggering __repr__
        assert obj == "something", f"Object is: {obj}"