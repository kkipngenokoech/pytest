import sys
import pytest
from _pytest._code.source import Source, getstatementrange_ast


def test_assertion_line_number_with_decorator():
    """Test that assertion failures don't include extra lines like decorators in Python 3.9+."""
    source_code = '''
@pytest.fixture
def some_fixture():
    return 42

def test_right_statement():
    assert 1 == 2
    assert 3 == 4
'''
    
    source = Source(source_code)
    # The assertion is on line 6 (0-indexed: line 5)
    assertion_lineno = 5
    
    # Get the statement range for the assertion
    ast_node, start, end = getstatementrange_ast(assertion_lineno, source, assertion=True)
    
    # The statement should only include the assertion line, not the decorator
    statement_lines = source[start:end]
    
    # Should only contain the assertion line
    assert len(statement_lines.lines) == 1
    assert "assert 1 == 2" in str(statement_lines)
    assert "@pytest.fixture" not in str(statement_lines)
    assert "def some_fixture" not in str(statement_lines)


def test_multiline_assertion_boundary():
    """Test that multiline assertions are handled correctly."""
    source_code = '''
@property
def some_prop(self):
    return True

def test_multiline():
    assert (1 == 2 and
            3 == 4)
    print("after assertion")
'''
    
    source = Source(source_code)
    # The assertion starts on line 6 (0-indexed: line 5)
    assertion_lineno = 5
    
    ast_node, start, end = getstatementrange_ast(assertion_lineno, source, assertion=True)
    statement_lines = source[start:end]
    
    # Should include both lines of the assertion but not the decorator or print
    statement_str = str(statement_lines)
    assert "assert (1 == 2 and" in statement_str
    assert "3 == 4)" in statement_str
    assert "@property" not in statement_str
    assert "print(" not in statement_str


def test_assertion_with_preceding_decorator():
    """Test specific case from the bug report."""
    source_code = '''
from pytest import fixture

@fixture
def t():
    return 42

def test_right_statement():
    assert 1 == 2
    assert 3 == 4
'''
    
    source = Source(source_code)
    # The first assertion is on line 8 (0-indexed: line 7)
    assertion_lineno = 7
    
    ast_node, start, end = getstatementrange_ast(assertion_lineno, source, assertion=True)
    statement_lines = source[start:end]
    
    # Should only contain the assertion, not the fixture decorator
    statement_str = str(statement_lines)
    assert "assert 1 == 2" in statement_str
    assert "@fixture" not in statement_str
    assert "def t()" not in statement_str
    
    # Verify we get exactly one line
    assert len(statement_lines.lines) == 1


@pytest.mark.skipif(sys.version_info < (3, 9), reason="Test specific to Python 3.9+ behavior")
def test_python39_specific_line_handling():
    """Test that Python 3.9+ specific AST changes are handled correctly."""
    source_code = '''
@pytest.fixture
def fixture_func():
    pass

def test_func():
    x = 1
    assert x == 2  # This should be isolated
    y = 3
'''
    
    source = Source(source_code)
    # The assertion is on line 7 (0-indexed: line 6)
    assertion_lineno = 6
    
    ast_node, start, end = getstatementrange_ast(assertion_lineno, source, assertion=True)
    statement_lines = source[start:end]
    
    # Should only contain the assertion line
    assert len(statement_lines.lines) == 1
    assert "assert x == 2" in str(statement_lines)
    assert "@pytest.fixture" not in str(statement_lines)
    assert "x = 1" not in str(statement_lines)
    assert "y = 3" not in str(statement_lines)
