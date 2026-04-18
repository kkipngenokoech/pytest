import pytest
import sys
from io import StringIO
from _pytest.config import get_config
from _pytest.fixtures import fixture


def test_issue_reproduction(testdir):
    """Test that --fixtures should display fixture scopes but currently doesn't."""
    
    # Create a test file with fixtures of different scopes
    testdir.makepyfile(
        """
        import pytest
        
        @pytest.fixture(scope="session")
        def session_fixture():
            return "session"
            
        @pytest.fixture(scope="module")
        def module_fixture():
            return "module"
            
        @pytest.fixture(scope="class")
        def class_fixture():
            return "class"
            
        @pytest.fixture(scope="function")
        def function_fixture():
            return "function"
            
        @pytest.fixture  # default scope is function
        def default_fixture():
            return "default"
            
        def test_dummy():
            pass
        """
    )
    
    # Run pytest --fixtures and capture output
    result = testdir.runpytest("--fixtures")
    output = result.stdout.str()
    
    # The test should fail because scope information is missing
    # Check that fixture names are present but scope info is missing
    assert "session_fixture" in output
    assert "module_fixture" in output
    assert "class_fixture" in output
    assert "function_fixture" in output
    assert "default_fixture" in output
    
    # This assertion should fail on current code - scope info should be shown but isn't
    assert "scope: session" in output or "(session)" in output or "session scope" in output, \
        "Fixture scope information should be displayed with --fixtures but is missing"
    assert "scope: module" in output or "(module)" in output or "module scope" in output, \
        "Fixture scope information should be displayed with --fixtures but is missing"
    assert "scope: class" in output or "(class)" in output or "class scope" in output, \
        "Fixture scope information should be displayed with --fixtures but is missing"
    assert "scope: function" in output or "(function)" in output or "function scope" in output, \
        "Fixture scope information should be displayed with --fixtures but is missing"