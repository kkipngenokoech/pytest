import sys
import tempfile
from pathlib import Path
from _pytest.pathlib import import_path, ImportMode


def test_issue_reproduction():
    """Test that modules are not imported twice under importlib mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create a test module with a class that has a class variable
        test_module_path = tmpdir_path / "test_module.py"
        test_module_path.write_text(
            "class TestClass:\n"
            "    class_var = 'initial'"
        )
        
        # Import the module first time
        mod1 = import_path(test_module_path, mode=ImportMode.importlib, root=tmpdir_path)
        
        # Modify the class variable
        mod1.TestClass.class_var = 'modified'
        
        # Import the same module again
        mod2 = import_path(test_module_path, mode=ImportMode.importlib, root=tmpdir_path)
        
        # They should be the same module object
        assert mod1 is mod2, "Module imported twice - different objects in memory"
        
        # The class variable should retain the modified value
        assert mod2.TestClass.class_var == 'modified', "Module state not preserved - module imported twice"