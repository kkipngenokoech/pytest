import sys
import tempfile
from pathlib import Path
from _pytest.pathlib import import_path, ImportMode

def test_issue_reproduction():
    """Test that modules are not imported twice under importlib mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create a test module with state
        test_module_path = tmpdir_path / "test_module.py"
        test_module_path.write_text("""
class StateHolder:
    value = None

def set_state(val):
    StateHolder.value = val

def get_state():
    return StateHolder.value
""")
        
        # Create a subdirectory structure to trigger the issue
        subdir = tmpdir_path / "subdir"
        subdir.mkdir()
        
        # Import the module twice with different paths but same content
        # This simulates the scenario described in the issue
        mod1 = import_path(test_module_path, mode=ImportMode.importlib, root=tmpdir_path)
        
        # Set state in first module
        mod1.set_state("test_value")
        
        # Import again - this should be the same module instance
        mod2 = import_path(test_module_path, mode=ImportMode.importlib, root=tmpdir_path)
        
        # The state should be consistent between both imports
        # This will fail if modules are imported twice
        assert mod1.get_state() == mod2.get_state(), "Module imported twice - state inconsistency detected"
        assert mod1 is mod2, "Different module objects returned for same path"
        
        # Verify they reference the same class
        assert mod1.StateHolder is mod2.StateHolder, "Different StateHolder classes - module duplication detected"