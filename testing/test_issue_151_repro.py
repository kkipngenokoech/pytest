import pytest
from _pytest.config import get_config


def test_issue_reproduction():
    """Test that --collect-only has a short option available."""
    # Try to create a config with a short option for collect-only
    # This should fail because no short option exists yet
    
    # First, let's verify --collect-only works
    config = get_config(["-h"])
    parser = config._parser
    
    # Look for collect-only option in the collect group
    collect_group = None
    for group in parser._groups:
        if group.name == "collect":
            collect_group = group
            break
    
    assert collect_group is not None, "collect group should exist"
    
    # Find the collect-only option
    collect_only_option = None
    for option in collect_group.options:
        if "--collect-only" in option._long_opts:
            collect_only_option = option
            break
    
    assert collect_only_option is not None, "--collect-only option should exist"
    
    # This should fail - there should be a short option available
    # Currently there are no short options for --collect-only
    assert len(collect_only_option._short_opts) > 0, "--collect-only should have a short option available"