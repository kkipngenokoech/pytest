import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

from _pytest.pathlib import import_path, ImportMode


def test_issue_reproduction():
    """Test that importlib mode doesn't create duplicate module instances."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create a module with a global state that can be modified
        module_content = textwrap.dedent("""
            class Logger:
                store = None
            
            def initialize():
                Logger.store = "initialized"
        """)
        
        # Create the module file
        module_path = tmpdir / "mymodule.py"
        module_path.write_text(module_content)
        
        # Import the module using importlib mode
        mod1 = import_path(module_path, mode=ImportMode.importlib, root=tmpdir)
        
        # Initialize the state
        mod1.initialize()
        assert mod1.Logger.store == "initialized"
        
        # Import the same module again with a different path context
        # This simulates what happens in the issue where the same module
        # gets imported under different names
        subdir = tmpdir / "subdir"
        subdir.mkdir()
        
        # Create a test file that imports the module
        test_content = textwrap.dedent("""
            import sys
            from pathlib import Path
            
            # Add parent to path to import mymodule
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            import mymodule
            
            def test_function():
                # This should see the initialized state
                assert mymodule.Logger.store == "initialized"
        """)
        
        test_path = subdir / "test_mymodule.py"
        test_path.write_text(test_content)
        
        # Import the test module using importlib mode
        test_mod = import_path(test_path, mode=ImportMode.importlib, root=tmpdir)
        
        # The bug: the mymodule imported by test_mod should be the same instance
        # as mod1, but with the current implementation it might not be
        # This causes the initialization to be lost
        
        # Get the mymodule from the test module's namespace
        test_mymodule = test_mod.mymodule
        
        # This assertion should pass but fails due to the bug
        # The test module gets a fresh copy of mymodule without the initialization
        assert test_mymodule.Logger.store == "initialized", f"Expected 'initialized' but got {test_mymodule.Logger.store}. Module instances: mod1.mymodule id={id(mod1)} vs test_mymodule id={id(test_mymodule)}"
