import pytest

def test_issue_reproduction():
    class SomeClass:
        def __getattribute__(self, attr):
            raise Exception("broken __getattribute__")
    
    obj = SomeClass()
    
    # This should trigger the INTERNALERROR when pytest tries to display the object
    # in a test failure or assertion error
    with pytest.raises(AssertionError):
        assert obj == "something"
    
    # The test will fail with INTERNALERROR instead of handling the repr gracefully