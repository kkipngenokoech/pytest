import pytest

def test_issue_reproduction():
    """Test that demonstrates confusing byte string assertion rewriting.
    
    The current implementation shows ASCII ordinals (like 52 for '4') 
    when comparing byte strings, which is confusing to users.
    """
    with pytest.raises(AssertionError) as excinfo:
        assert b"" == b"42"
    
    # The assertion message should not contain confusing ASCII ordinals
    # Currently it shows something like "52" (ASCII ordinal of '4')
    # which is confusing to users
    error_msg = str(excinfo.value)
    
    # This test will fail because the current implementation produces
    # confusing output with ASCII ordinals instead of clear byte representation
    assert "52" not in error_msg, f"Confusing ASCII ordinal found in error message: {error_msg}"
    
    # Test another example from the issue
    with pytest.raises(AssertionError) as excinfo2:
        assert b"" == b"1"
    
    error_msg2 = str(excinfo2.value)
    # ASCII ordinal of '1' is 49
    assert "49" not in error_msg2, f"Confusing ASCII ordinal found in error message: {error_msg2}"