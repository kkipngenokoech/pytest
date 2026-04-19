import sys
import tempfile
from pathlib import Path
from _pytest.pathlib import import_path, ImportMode

def test_issue_reproduction():
    """Test that modules are not imported twice under importlib mode."""
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create a test module with a class that has state
        test_module_path = tmpdir_path / "test_module.py"
        test_module_path.write_text("""
class StateHolder:
    value = None

def set_state(val):
    StateHolder.value = val

def get_state():
    return StateHolder.value
""")
        
        # Create a subdirectory and another module that imports the first
        subdir = tmpdir_path / "subdir"
        subdir.mkdir()
        
        importing_module_path = subdir / "importing_module.py"
        importing_module_path.write_text("""
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from test_module import StateHolder, set_state, get_state

def check_state():
    return get_state()

def modify_state():
    set_state("modified")
""")
        
        # Clear any existing modules that might interfere
        modules_to_clear = [name for name in sys.modules.keys() 
                           if 'test_module' in name or 'importing_module' in name]
        for name in modules_to_clear:
            del sys.modules[name]
        
        # Import the first module using importlib mode
        mod1 = import_path(test_module_path, mode=ImportMode.importlib, root=tmpdir_path)
        
        # Set state in the first module
        mod1.set_state("original")
        assert mod1.get_state() == "original"
        
        # Import the second module which imports the first module
        mod2 = import_path(importing_module_path, mode=ImportMode.importlib, root=tmpdir_path)
        
        # The state should be visible in the second module since it imports the same module
        # This will fail if the module was imported twice, creating separate instances
        assert mod2.check_state() == "original", f"Expected 'original' but got {mod2.check_state()}"
        
        # Modify state through the second module
        mod2.modify_state()
        
        # The change should be visible in the first module
        # This will also fail if there are separate module instances
        assert mod1.get_state() == "modified", f"Expected 'modified' but got {mod1.get_state()}"
        
        # Verify both modules reference the same StateHolder class
        # This is the core issue - they should be the same object
        assert mod1.StateHolder is mod2.check_state.__globals__['StateHolder'], "StateHolder classes should be the same object"