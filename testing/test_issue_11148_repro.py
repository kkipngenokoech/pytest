import sys
import tempfile
from pathlib import Path
from textwrap import dedent

from _pytest.pathlib import ImportMode, import_path


def test_issue_reproduction():
    """Test that modules are not imported twice under importlib mode."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create a package structure
        pkg_dir = tmp_path / "testpkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        
        # Create a module with a class that tracks instances
        module_content = dedent("""
            class TestClass:
                instances = []
                
                def __init__(self):
                    TestClass.instances.append(self)
        """)
        
        module_path = pkg_dir / "testmodule.py"
        module_path.write_text(module_content)
        
        # Import the module twice using importlib mode
        mod1 = import_path(module_path, mode=ImportMode.importlib, root=tmp_path)
        mod2 = import_path(module_path, mode=ImportMode.importlib, root=tmp_path)
        
        # They should be the same module object
        assert mod1 is mod2, "Module imported twice - different objects in memory"
        
        # Create instances from both module references
        instance1 = mod1.TestClass()
        instance2 = mod2.TestClass()
        
        # Both instances should be tracked in the same class
        # This will fail if modules are imported separately
        assert len(mod1.TestClass.instances) == 2, f"Expected 2 instances, got {len(mod1.TestClass.instances)}"
        assert len(mod2.TestClass.instances) == 2, f"Expected 2 instances, got {len(mod2.TestClass.instances)}"
        assert mod1.TestClass.instances is mod2.TestClass.instances, "Class attributes are different - modules imported separately"