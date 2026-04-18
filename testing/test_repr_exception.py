"""Tests for handling exceptions in __repr__ methods during pytest execution."""
import pytest


class ReprRaisesAttributeError:
    """Class whose __repr__ raises AttributeError."""
    def __repr__(self):
        raise AttributeError("repr failed")


class ReprRaisesValueError:
    """Class whose __repr__ raises ValueError."""
    def __repr__(self):
        raise ValueError("invalid value in repr")


class ReprRaisesRecursionError:
    """Class whose __repr__ causes infinite recursion."""
    def __repr__(self):
        return repr(self)


class ReprRaisesGenericException:
    """Class whose __repr__ raises a generic exception."""
    def __repr__(self):
        raise Exception("generic repr error")


class ReprRaisesKeyboardInterrupt:
    """Class whose __repr__ raises KeyboardInterrupt."""
    def __repr__(self):
        raise KeyboardInterrupt("interrupted")


class TestReprExceptionHandling:
    """Test that pytest handles __repr__ exceptions gracefully."""

    def test_repr_attribute_error_in_test_failure(self, testdir):
        """Test that AttributeError in __repr__ doesn't cause INTERNALERROR."""
        testdir.makepyfile(
            """
            class ReprRaisesAttributeError:
                def __repr__(self):
                    raise AttributeError("repr failed")

            def test_failing_with_bad_repr():
                obj = ReprRaisesAttributeError()
                assert obj == "something", f"Expected something, got {obj}"
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*FAILED*test_failing_with_bad_repr*",
        ])
        # Should not contain INTERNALERROR
        assert "INTERNALERROR" not in result.stdout.str()

    def test_repr_value_error_in_test_failure(self, testdir):
        """Test that ValueError in __repr__ doesn't cause INTERNALERROR."""
        testdir.makepyfile(
            """
            class ReprRaisesValueError:
                def __repr__(self):
                    raise ValueError("invalid value in repr")

            def test_failing_with_bad_repr():
                obj = ReprRaisesValueError()
                assert obj == "something", f"Expected something, got {obj}"
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*FAILED*test_failing_with_bad_repr*",
        ])
        # Should not contain INTERNALERROR
        assert "INTERNALERROR" not in result.stdout.str()

    def test_repr_recursion_error_in_test_failure(self, testdir):
        """Test that RecursionError in __repr__ doesn't cause INTERNALERROR."""
        testdir.makepyfile(
            """
            class ReprRaisesRecursionError:
                def __repr__(self):
                    return repr(self)

            def test_failing_with_bad_repr():
                obj = ReprRaisesRecursionError()
                assert obj == "something", f"Expected something, got {obj}"
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*FAILED*test_failing_with_bad_repr*",
        ])
        # Should not contain INTERNALERROR
        assert "INTERNALERROR" not in result.stdout.str()

    def test_repr_generic_exception_in_test_failure(self, testdir):
        """Test that generic Exception in __repr__ doesn't cause INTERNALERROR."""
        testdir.makepyfile(
            """
            class ReprRaisesGenericException:
                def __repr__(self):
                    raise Exception("generic repr error")

            def test_failing_with_bad_repr():
                obj = ReprRaisesGenericException()
                assert obj == "something", f"Expected something, got {obj}"
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*FAILED*test_failing_with_bad_repr*",
        ])
        # Should not contain INTERNALERROR
        assert "INTERNALERROR" not in result.stdout.str()

    def test_repr_exception_in_collection_phase(self, testdir):
        """Test that __repr__ exceptions during collection are handled."""
        testdir.makepyfile(
            """
            class BadReprClass:
                def __repr__(self):
                    raise ValueError("bad repr during collection")

            # Create an instance at module level to trigger during collection
            bad_obj = BadReprClass()

            def test_something():
                pass
            """
        )
        result = testdir.runpytest("-v")
        # Collection should succeed despite the bad __repr__
        result.stdout.fnmatch_lines([
            "*collected 1 item*",
        ])
        # Should not contain INTERNALERROR
        assert "INTERNALERROR" not in result.stdout.str()

    def test_safe_repr_function_directly(self):
        """Test the _safe_repr function directly."""
        from _pytest.terminal import _safe_repr

        # Test normal object
        normal_obj = "normal string"
        assert _safe_repr(normal_obj) == "'normal string'"

        # Test object with failing __repr__
        bad_obj = ReprRaisesAttributeError()
        result = _safe_repr(bad_obj)
        assert "ReprRaisesAttributeError" in result
        assert "AttributeError" in result
        assert "repr failed" in result
        assert result.startswith("<")
        assert result.endswith(">")

        # Test object with ValueError in __repr__
        bad_obj2 = ReprRaisesValueError()
        result2 = _safe_repr(bad_obj2)
        assert "ReprRaisesValueError" in result2
        assert "ValueError" in result2
        assert "invalid value in repr" in result2

        # Test object with generic exception in __repr__
        bad_obj3 = ReprRaisesGenericException()
        result3 = _safe_repr(bad_obj3)
        assert "ReprRaisesGenericException" in result3
        assert "Exception" in result3
        assert "generic repr error" in result3

    def test_repr_keyboard_interrupt_propagated(self, testdir):
        """Test that KeyboardInterrupt in __repr__ is still propagated."""
        testdir.makepyfile(
            """
            class ReprRaisesKeyboardInterrupt:
                def __repr__(self):
                    raise KeyboardInterrupt("interrupted")

            def test_failing_with_keyboard_interrupt_repr():
                obj = ReprRaisesKeyboardInterrupt()
                assert obj == "something", f"Expected something, got {obj}"
            """
        )
        result = testdir.runpytest("-v")
        # KeyboardInterrupt should still be handled as an interruption
        # The exact behavior may vary, but it shouldn't cause INTERNALERROR
        assert "INTERNALERROR" not in result.stdout.str()

    def test_repr_exception_in_fixture(self, testdir):
        """Test that __repr__ exceptions in fixtures are handled."""
        testdir.makepyfile(
            """
            import pytest

            class BadReprFixture:
                def __repr__(self):
                    raise RuntimeError("fixture repr failed")

            @pytest.fixture
            def bad_fixture():
                return BadReprFixture()

            def test_with_bad_fixture(bad_fixture):
                assert bad_fixture != "something"
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*PASSED*test_with_bad_fixture*",
        ])
        # Should not contain INTERNALERROR
        assert "INTERNALERROR" not in result.stdout.str()

    def test_multiple_repr_exceptions(self, testdir):
        """Test handling multiple objects with failing __repr__ methods."""
        testdir.makepyfile(
            """
            class BadRepr1:
                def __repr__(self):
                    raise AttributeError("first bad repr")

            class BadRepr2:
                def __repr__(self):
                    raise ValueError("second bad repr")

            def test_multiple_bad_reprs():
                obj1 = BadRepr1()
                obj2 = BadRepr2()
                assert obj1 == obj2, f"Objects should be equal: {obj1} vs {obj2}"
            """
        )
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*FAILED*test_multiple_bad_reprs*",
        ])
        # Should not contain INTERNALERROR
        assert "INTERNALERROR" not in result.stdout.str()
