import sys
import tempfile
from pathlib import Path
from _pytest.pathlib import import_path, ImportMode


def test_issue_reproduction():
    """Test that modules are not imported twice under importlib mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create a test module with state that can be modified
        test_module_content = '''
class Logger:
    store = None

def set_store(value):
    Logger.store = value

def get_store():
    return Logger.store
'''
        
        # Create the module file
        module_path = tmpdir_path / "test_logging.py"
        module_path.write_text(test_module_content)
        
        # Import the module using importlib mode
        mod1 = import_path(module_path, mode=ImportMode.importlib, root=tmpdir_path)
        
        # Set some state in the first import
        mod1.set_store("test_value")
        
        # Import the same module again using importlib mode
        mod2 = import_path(module_path, mode=ImportMode.importlib, root=tmpdir_path)
        
        # The bug: mod2 should see the state set by mod1, but it doesn't
        # because they are different module instances
        assert mod1.get_store() == "test_value", "First module should have the set value"
        assert mod2.get_store() == "test_value", "Second module should see the same state (this fails due to the bug)"
        
        # They should be the same module object
        assert mod1 is mod2, "Both imports should return the same module object"
        
        # Check that there's only one entry in sys.modules for this module
        module_entries = [name for name in sys.modules.keys() if 'test_logging' in name]
        assert len(module_entries) == 1, f"Should have only one module entry, but found: {module_entries}"