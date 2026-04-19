import socket
import pytest
from _pytest.junitxml import LogXML
from _pytest.config import Config
import py
import tempfile
import os


def test_issue_reproduction():
    """Test that JUnit XML includes hostname and timestamp attributes in testsuite element."""
    # Create a temporary file for XML output
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        xml_file = f.name
    
    try:
        # Create a LogXML instance
        xml_logger = LogXML(
            logfile=xml_file,
            prefix=None,
            suite_name="test_suite",
            logging="no",
            report_duration="total",
            family="xunit1",
            log_passing_tests=True
        )
        
        # Simulate the pytest_sessionfinish hook behavior
        xml_logger.pytest_sessionfinish()
        
        # Read the generated XML
        with open(xml_file, 'r') as f:
            xml_content = f.read()
        
        # Check that hostname and timestamp attributes are present
        assert 'hostname=' in xml_content, "hostname attribute missing from testsuite element"
        assert 'timestamp=' in xml_content, "timestamp attribute missing from testsuite element"
        
        # Verify the hostname value is correct
        expected_hostname = socket.gethostname()
        assert f'hostname="{expected_hostname}"' in xml_content, f"Expected hostname '{expected_hostname}' not found"
        
        # Verify timestamp format (ISO format with T separator)
        import re
        timestamp_pattern = r'timestamp="\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"'
        assert re.search(timestamp_pattern, xml_content), "timestamp not in expected ISO format"
        
    finally:
        # Clean up
        if os.path.exists(xml_file):
            os.unlink(xml_file)