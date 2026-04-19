import sys
import tempfile
from pathlib import Path
from textwrap import dedent

import pytest

from _pytest.pathlib import import_path, ImportMode


def test_issue_reproduction():
    """Test that modules are not imported twice under import-mode=importlib."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create a module with a class that has a class variable
        module_file = tmp_path / "test_module.py"
        module_file.write_text(dedent("""
            class Logger:
                store = None
                
            def initialize():
                Logger.store = "initialized"
        """))
        
        # Create a test file that imports the module
        test_file = tmp_path / "test_commands.py"
        test_file.write_text(dedent("""
            from test_module import Logger, initialize
            
            def test_something():
                initialize()
                assert Logger.store == "initialized"
        """))
        
        # Import the module first time using importlib mode
        mod1 = import_path(module_file, mode=ImportMode.importlib, root=tmp_path)
        
        # Initialize the Logger.store
        mod1.initialize()
        assert mod1.Logger.store == "initialized"
        
        # Import the test file which imports the same module
        test_mod = import_path(test_file, mode=ImportMode.importlib, root=tmp_path)
        
        # The bug: test_mod.Logger should be the same as mod1.Logger
        # but they are different instances, so the initialization is lost
        assert test_mod.Logger.store == "initialized", (
            f"Module imported twice: mod1.Logger.store={mod1.Logger.store}, "
            f"test_mod.Logger.store={test_mod.Logger.store}. "
            f"They should be the same object: {mod1.Logger is test_mod.Logger}"
        )