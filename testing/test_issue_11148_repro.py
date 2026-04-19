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
        
        # Create a package structure
        pkg_dir = tmp_path / "mypackage"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        
        # Create a module with a class that has a class variable
        logging_module = pkg_dir / "logging.py"
        logging_module.write_text(dedent("""
            class Logger:
                store = None
                
            def set_store(value):
                Logger.store = value
        """))
        
        # Create a test module that imports the logging module
        tests_dir = tmp_path / "tests" / "unit"
        tests_dir.mkdir(parents=True)
        (tests_dir / "__init__.py").write_text("")
        
        test_commands = tests_dir / "test_commands.py"
        test_commands.write_text(dedent("""
            from mypackage import logging
            
            def test_something():
                # This should see the same Logger.store value set by core.initialize()
                assert logging.Logger.store is not None
        """))
        
        # Create a core module that initializes the logger
        core_module = pkg_dir / "core.py"
        core_module.write_text(dedent("""
            from mypackage.logging import set_store
            
            def initialize():
                set_store("initialized")
        """))
        
        # Clear any existing modules to ensure clean state
        modules_to_remove = [k for k in sys.modules.keys() if k.startswith('mypackage')]
        for mod in modules_to_remove:
            del sys.modules[mod]
        
        try:
            # Import and run core.initialize() using importlib mode
            core_mod = import_path(core_module, mode=ImportMode.importlib, root=tmp_path)
            core_mod.initialize()
            
            # Import the test module using importlib mode
            test_mod = import_path(test_commands, mode=ImportMode.importlib, root=tmp_path)
            
            # Import logging module directly to check the state
            logging_mod = import_path(logging_module, mode=ImportMode.importlib, root=tmp_path)
            
            # The bug: Logger.store should be "initialized" but it's None
            # because the logging module was imported twice under different names
            assert logging_mod.Logger.store == "initialized", f"Expected 'initialized', got {logging_mod.Logger.store}"
            
        finally:
            # Clean up sys.modules
            modules_to_remove = [k for k in sys.modules.keys() if k.startswith('mypackage')]
            for mod in modules_to_remove:
                del sys.modules[mod]