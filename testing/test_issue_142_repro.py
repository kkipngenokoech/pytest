import pytest
import subprocess
import sys
import tempfile
import os

def test_issue_reproduction():
    """Test that fixture scope is displayed with pytest --fixtures."""
    # Create a temporary test file with fixtures of different scopes
    test_content = '''
import pytest

@pytest.fixture(scope="session")
def session_fixture():
    return "session"

@pytest.fixture(scope="module")
def module_fixture():
    return "module"

@pytest.fixture(scope="function")
def function_fixture():
    return "function"

def test_dummy():
    pass
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        f.flush()
        
        try:
            # Run pytest --fixtures on the temporary file
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', '--fixtures', f.name],
                capture_output=True,
                text=True
            )
            
            output = result.stdout + result.stderr
            
            # Check that scope information is displayed for each fixture
            # This should fail on current code since scope is not shown
            assert 'session_fixture' in output
            assert 'scope: session' in output or '(session)' in output
            assert 'module_fixture' in output  
            assert 'scope: module' in output or '(module)' in output
            assert 'function_fixture' in output
            assert 'scope: function' in output or '(function)' in output
            
        finally:
            os.unlink(f.name)