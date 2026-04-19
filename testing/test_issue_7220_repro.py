import os
import tempfile
import pytest
from _pytest.pytester import Pytester


def test_issue_reproduction(pytester: Pytester):
    """Test that file paths are shown relative to original directory when working directory is changed in fixture."""
    
    # Create a test file that changes directory in a fixture and then fails
    pytester.makepyfile(
        test_path_error="""
import os
import tempfile
import pytest

@pytest.fixture
def change_dir():
    original_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    yield
    os.chdir(original_dir)

def test_failure_after_chdir(change_dir):
    assert False, "This should fail"
"""
    )
    
    # Run the test and capture the output
    result = pytester.runpytest("-v")
    
    # The issue is that the path should be shown as "test_path_error.py" 
    # but instead shows as "../test_path_error.py" due to the directory change
    output = result.stdout.str()
    
    # This assertion will FAIL on the current buggy code because
    # the path will be shown as "../test_path_error.py" instead of "test_path_error.py"
    assert "test_path_error.py::test_failure_after_chdir FAILED" in output
    assert "../test_path_error.py" not in output, "File path should not be relative to changed directory"