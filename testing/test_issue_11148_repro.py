import sys
import tempfile
from pathlib import Path
from textwrap import dedent

import pytest

from _pytest.pathlib import import_path, ImportMode


def test_issue_reproduction():
    """Test that modules are not imported twice under importlib mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create a test module with a class that has a modifiable class variable
        test_module_path = tmpdir_path / "test_module.py"
        test_module_path.write_text(dedent("""
            class TestClass:
                shared_value = None
                
            def set_shared_value(value):
                TestClass.shared_value = value
                
            def get_shared_value():
                return TestClass.shared_value
        """))
        
        # Import the module twice using importlib mode with different roots
        # This simulates the scenario described in the issue
        mod1 = import_path(test_module_path, mode=ImportMode.importlib, root=tmpdir_path)
        mod2 = import_path(test_module_path, mode=ImportMode.importlib, root=tmpdir_path / "subdir")
        
        # Set a value using the first module
        mod1.set_shared_value("test_value")
        
        # The second module should see the same value since it should be the same module instance
        # This will fail if modules are imported twice, demonstrating the bug
        assert mod2.get_shared_value() == "test_value", f"Module imported twice: mod1.TestClass is {mod1.TestClass}, mod2.TestClass is {mod2.TestClass}"
        
        # Additional check: the class objects should be identical
        assert mod1.TestClass is mod2.TestClass, "Different module instances created"
        
        # Check that both modules are actually the same object
        assert mod1 is mod2, "Different module objects created for the same file"