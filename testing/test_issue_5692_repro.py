import socket
import datetime
import pytest
from _pytest.junitxml import LogXML
from _pytest.config import Config
import py


def test_issue_reproduction(testdir):
    """Test that JUnit XML includes hostname and timestamp attributes in testsuite element."""
    # Create a simple test file
    testdir.makepyfile("""
        def test_example():
            assert True
    """)
    
    # Run pytest with JUnit XML output
    result = testdir.runpytest("--junitxml=junit.xml")
    
    # Read the generated XML
    xml_path = testdir.tmpdir.join("junit.xml")
    xml_content = xml_path.read()
    
    # Parse the XML to check for hostname and timestamp attributes
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_content)
    
    # The testsuite element should have hostname and timestamp attributes
    testsuite = root if root.tag == 'testsuite' else root.find('testsuite')
    assert testsuite is not None, "testsuite element not found"
    
    # Check for hostname attribute
    hostname = testsuite.get('hostname')
    assert hostname is not None, "hostname attribute missing from testsuite element"
    assert hostname == socket.gethostname(), f"hostname should be {socket.gethostname()}, got {hostname}"
    
    # Check for timestamp attribute  
    timestamp = testsuite.get('timestamp')
    assert timestamp is not None, "timestamp attribute missing from testsuite element"
    
    # Verify timestamp format (should be ISO format)
    try:
        datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except ValueError:
        pytest.fail(f"timestamp '{timestamp}' is not in valid ISO format")