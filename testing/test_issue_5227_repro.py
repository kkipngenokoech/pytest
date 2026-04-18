import logging
from _pytest.logging import DEFAULT_LOG_FORMAT

def test_issue_reproduction():
    """Test that DEFAULT_LOG_FORMAT includes module name (%(name)s)."""
    # The issue requests that %(name)s should be included in the default log format
    # to show the module name instead of just the filename
    assert "%(name)s" in DEFAULT_LOG_FORMAT, f"Expected %(name)s in format, got: {DEFAULT_LOG_FORMAT}"