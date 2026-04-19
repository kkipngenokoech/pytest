import logging
from _pytest.logging import DEFAULT_LOG_FORMAT

def test_issue_reproduction():
    """Test that DEFAULT_LOG_FORMAT includes module name for better log identification."""
    # The current format should include %(name)s to show module names
    # This test will fail until the format is updated to include %(name)s
    assert "%(name)s" in DEFAULT_LOG_FORMAT, f"DEFAULT_LOG_FORMAT should include %(name)s for module identification, got: {DEFAULT_LOG_FORMAT}"
    
    # Also verify the format produces the expected output with module names
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    record = logging.LogRecord(
        name="django.db.backends",
        level=logging.DEBUG,
        pathname="/path/to/utils.py", 
        lineno=114,
        msg="test message",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    # Should contain the module name when %(name)s is in format
    assert "django.db.backends" in formatted, f"Formatted log should contain module name, got: {formatted}"