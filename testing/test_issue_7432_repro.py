import pytest
from _pytest.pytester import Pytester


def test_issue_reproduction(pytester: Pytester):
    """Test that --runxfail doesn't break skip location reporting."""
    # Create a test file with a skipped test
    pytester.makepyfile(
        test_skip_location="""
        import pytest
        
        @pytest.mark.skip(reason="unconditional skip")
        def test_skipped():
            pass
        """
    )
    
    # Run without --runxfail - this should show correct location
    result_normal = pytester.runpytest("-rs")
    normal_output = result_normal.stdout.str()
    
    # Run with --runxfail - this should also show correct location but currently doesn't
    result_runxfail = pytester.runpytest("-rs", "--runxfail")
    runxfail_output = result_runxfail.stdout.str()
    
    # Both should report the same location (test_skip_location.py:3)
    # But with the bug, --runxfail shows src/_pytest/skipping.py:238
    assert "test_skip_location.py:3" in normal_output
    assert "test_skip_location.py:3" in runxfail_output, f"Expected test location in output, got: {runxfail_output}"
    assert "skipping.py" not in runxfail_output, f"Should not show skipping.py location, got: {runxfail_output}"