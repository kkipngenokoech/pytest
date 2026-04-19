import atexit
import contextlib
import fnmatch
import itertools
import os
import shutil
import sys
import uuid
import warnings
from functools import partial
from os.path import expanduser
from os.path import expandvars
from os.path import isabs
from os.path import sep
from pathlib import Path
from pathlib import PurePath
from types import ModuleType
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

import py

from _pytest.compat import assert_never
from _pytest.outcomes import skip
from _pytest.warning_types import PytestUnraisableExceptionWarning

if sys.version_info[:2] >= (3, 6):
    from pathlib import os as path_os
else:
    path_os = os


SKIP_REASON = "cannot import 'pathlib'"

try:
    from pathlib import PurePath
except ImportError:
    PurePath = None


def get_lock_path(path: Union[str, "os.PathLike[str]"]):
    return Path(path).with_suffix(".lock")


def ensure_reset_dir(path: Path) -> None:
    """
    Ensure the given path is an empty directory.
    """
    if path.exists():
        rm_rf(path)
    path.mkdir()


def on_rm_rf_error(func, path: str, exc, *, start_path: Path) -> bool:
    """Handle known read-only errors during rmtree.

    The returned value is used only by our own tests.
    """
    exctype, excvalue = exc[:2]

    # another process removed the file in the middle of the "rm_rf" (xdist for example)
    # more context: https://github.com/pytest-dev/pytest/issues/5974#issuecomment-543799018
    if isinstance(excvalue, FileNotFoundError):
        return False

    if not isinstance(excvalue, PermissionError):
        warnings.warn(
            PytestUnraisableExceptionWarning(f"(rm_rf) error removing {path}"),
            stacklevel=5,
        )
        return False

    if func not in (os.rmdir, os.remove, os.unlink):
        if func not in (os.open,):
            warnings.warn(
                PytestUnraisableExceptionWarning(
                    f"(rm_rf) unknown function {func} when removing {path}"
                ),
                stacklevel=5,
            )
        return False

    # Chmod + retry.
    import stat

    def chmod_rw(p: str) -> None:
        mode = os.stat(p).st_mode
        os.chmod(p, mode | stat.S_IRUSR | stat.S_IWUSR)

    # For files, we need to recursively go upwards in the directories to
    # ensure they all are also writable.
    p = Path(path)
    if p.is_file():
        for parent in p.parents:
            chmod_rw(str(parent))
            # Stop when we reach the original path passed to rm_rf.
            if parent == start_path:
                break
    chmod_rw(str(path))

    func(path)
    return True


def rm_rf(path: Path) -> None:
    """Remove the path contents recursively, even if some elements
    are read-only.
    """
    path = ensure_extended_length_path(path)
    onerror = partial(on_rm_rf_error, start_path=path)
    if sys.version_info >= (3, 12):
        shutil.rmtree(str(path), onexc=onerror)
    else:
        shutil.rmtree(str(path), onerror=onerror)


def find_prefixed(root: Path, prefix: str) -> Iterator[Path]:
    """Find all elements in root that begin with the prefix, case insensitive."""
    l_prefix = prefix.lower()
    for x in root.iterdir():
        if x.name.lower().startswith(l_prefix):
            yield x


def extract_suffixes(iter: Iterable[PurePath], prefix: str) -> Iterator[str]:
    """
    :param iter: iterator over path names
    :param prefix: expected prefix of the path names
    :returns: the parts of the paths following the prefix
    """
    p_len = len(prefix)
    for p in iter:
        yield p.name[p_len:]


def find_suffixes(root: Path, prefix: str) -> Iterator[str]:
    """combine find_prefixed and extract_suffixes"""
    return extract_suffixes(find_prefixed(root, prefix), prefix)


def parse_num(maybe_num) -> int:
    """parses number path suffixes, returns -1 on error"""
    try:
        return int(maybe_num)
    except ValueError:
        return -1


def _force_symlink(
    root: Path, target: Union[str, PurePath], link_to: Union[str, PurePath]
) -> None:
    """helper to create the current symlink

    it's full of race conditions that are reasonably ok to ignore
    for the context of best effort linking to the latest test run

    the presumption being that in case of much parallelism
    the inaccuracy is going to be acceptable
    """
    current_symlink = root.joinpath(target)
    try:
        current_symlink.unlink()
    except OSError:
        pass
    try:
        current_symlink.symlink_to(link_to)
    except OSError:
        pass


def make_numbered_dir(root: Path, prefix: str, mode: int = 0o700) -> Path:
    """create a directory with an increased number as suffix for the given prefix"""
    for i in range(10):
        # try up to 10 times to create the folder
        max_existing = max(map(parse_num, find_suffixes(root, prefix)), default=-1)
        new_number = max_existing + 1
        new_path = root.joinpath(f"{prefix}{new_number}")
        try:
            new_path.mkdir(mode=mode)
        except Exception:
            pass
        else:
            _force_symlink(root, prefix + "current", new_path.name)
            return new_path
    else:
        raise OSError(
            f"could not create numbered dir with prefix {prefix} in {root} after 10 tries"
        )


def create_cleanup_lock(p: Path) -> Path:
    """crates a lock to prevent premature folder cleanup"""
    lock_path = get_lock_path(p)
    try:
        fd = os.open(str(lock_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as e:
        raise OSError(f"cannot create lockfile in {p}") from e
    else:
        pid = os.getpid()
        spid = str(pid).encode()
        os.write(fd, spid)
        os.close(fd)
        if not lock_path.is_file():
            raise OSError("lock path got renamed after successful creation")
        return lock_path


def register_cleanup_lock_removal(lock_path: Path, register=atexit.register):
    """registers a cleanup function for removing a lock, by default on atexit"""
    pid = os.getpid()

    def cleanup_on_exit(lock_path: Path = lock_path, original_pid: int = pid) -> None:
        current_pid = os.getpid()
        if current_pid != original_pid:
            # fork
            return
        try:
            lock_path.unlink()
        except OSError:
            pass

    return register(cleanup_on_exit)


def maybe_delete_a_numbered_dir(path: Path) -> None:
    """removes a numbered directory if its lock can be obtained and it does not seem to be in use"""
    path = ensure_extended_length_path(path)
    lock_path = None
    try:
        lock_path = create_cleanup_lock(path)
        parent = path.parent

        garbage = parent.joinpath(f"garbage-{uuid.uuid4()}")
        path.rename(garbage)
        rm_rf(garbage)
    except OSError:
        #  known races:
        #  * other process did a cleanup at the same time
        #  * deletable folder was found
        #  * process cwd (Windows)
        return
    finally:
        # if we created the lock, ensure we remove it even if we failed
        # to properly remove the numbered dir
        if lock_path is not None:
            try:
                lock_path.unlink()
            except OSError:
                pass


def ensure_deletable(path: Path, consider_lock_dead_if_created_before: float) -> bool:
    """checks if a lock exists and breaks it if its considered dead"""
    if path.is_symlink():
        return False
    if not path.exists():
        return False
    if path.is_file():
        return False
    lock = get_lock_path(path)
    try:
        if not lock.exists():
            return True
    except OSError:
        # we might not have access to the lock file at all, in this case assume
        # we don't have access to the entire directory (#7491).
        return False
    try:
        lock_time = lock.stat().st_mtime
    except OSError:
        return False
    else:
        if lock_time < consider_lock_dead_if_created_before:
            # We want to ignore any errors while trying to remove the lock such as:
            # - PermissionDenied, like the file permissions have changed since the lock creation
            # - FileNotFoundError, in case another pytest process got here first.
            # and any other cause of failure.
            with contextlib.suppress(OSError):
                lock.unlink()
            return True
        else:
            return False


def try_cleanup(path: Path, consider_lock_dead_if_created_before: float) -> None:
    """tries to cleanup a folder if we can ensure it's deletable"""
    if ensure_deletable(path, consider_lock_dead_if_created_before):
        maybe_delete_a_numbered_dir(path)


def cleanup_candidates(root: Path, prefix: str, keep: int) -> Iterator[Path]:
    """lists candidates for numbered directories to be removed - follows py.path"""
    max_existing = max(map(parse_num, find_suffixes(root, prefix)), default=-1)
    max_delete = max_existing - keep
    paths = find_prefixed(root, prefix)
    paths = map(root.joinpath, extract_suffixes(paths, prefix))
    paths = filter(lambda path: parse_num(path.name[len(prefix) :]) <= max_delete, paths)
    return paths


def cleanup_numbered_dir(
    root: Path, prefix: str, keep: int, consider_lock_dead_if_created_before: float
) -> None:
    """cleanup for lock driven numbered directories"""
    for path in cleanup_candidates(root, prefix, keep):
        try_cleanup(path, consider_lock_dead_if_created_before)


def make_numbered_dir_with_cleanup(
    root: Path,
    prefix: str,
    keep: int,
    lock_timeout: float,
    mode: int,
) -> Path:
    """creates a numbered dir with a cleanup lock and removes old ones"""
    e = OSError("could not create numbered dir")
    for i in range(10):
        try:
            p = make_numbered_dir(root, prefix, mode)
            # Only lock the current dir when keep is not 0
            if keep != 0:
                lock_path = create_cleanup_lock(p)
                register_cleanup_lock_removal(lock_path)
        except Exception as exc:
            e = exc
        else:
            consider_lock_dead_if_created_before = p.stat().st_mtime - lock_timeout
            # Register a cleanup for program exit
            atexit.register(
                cleanup_numbered_dir,
                root,
                prefix,
                keep,
                consider_lock_dead_if_created_before,
            )
            return p
    raise e


def resolve_from_str(input_str: str, rootpath: Path) -> Path:
    input_str = expandvars(input_str)
    input_str = expanduser(input_str)
    if isabs(input_str):
        return Path(input_str)
    else:
        return rootpath.joinpath(input_str)


def fnmatch_lines(lines2: List[str], lines1: List[str]) -> None:
    """Check that lines2 matches lines1 using glob-style wildcards.

    The comparison is case-insensitive.

    Asserts if lines2 does not match lines1.
    """
    __tracebackhide__ = True
    if len(lines2) < len(lines1):
        raise AssertionError(
            "lines2 must be longer than lines1.\n"
            f"lines1 ({len(lines1)}): {lines1!r}\n"
            f"lines2 ({len(lines2)}): {lines2!r}"
        )
    for i, pat in enumerate(lines1):
        if not fnmatch.fnmatch(lines2[i].lower(), pat.lower()):
            raise AssertionError(
                f"line {i+1} doesn't match pattern {pat!r}.\n"
                f"expected: {pat!r}\n"
                f"actual: {lines2[i]!r}"
            )


def import_path(
    p: Union[str, "os.PathLike[str]"],
    *,
    mode: Union[str, "importlib.machinery.ModuleSpec"] = "prepend",
) -> ModuleType:
    """Import and return a module from the given path, which can be a file (a module) or
    a directory (a package).

    The import mechanism used is controlled by the `mode` parameter:

    * `mode="prepend"`: the directory containing the module (or package) will be inserted
      at the beginning of `sys.path` before being imported with `importlib.import_module`.

    * `mode="append"`: same as `prepend`, but the directory will be appended to the end
      of `sys.path`, if not already in it.

    * `mode=importlib.machinery.ModuleSpec`: advanced mode where you provide a custom
      `ModuleSpec` for the module. Useful when you need full control over how the
      module is imported.

    :param p: path to the module or package to import
    :param mode: import mode
    :return: the imported module
    """
    import importlib.machinery
    import importlib.util
    import sys

    path = Path(p)

    if isinstance(mode, str):
        if mode not in ("prepend", "append"):
            raise ValueError(
                f"mode must be either 'prepend' or 'append', got: {mode!r}"
            )

        if path.is_dir():
            pkg_path = path
            module_name = path.name
        else:
            pkg_path = path.parent
            module_name = path.stem

        if mode == "prepend":
            if str(pkg_path) != sys.path[0]:
                sys.path.insert(0, str(pkg_path))
        elif mode == "append":
            if str(pkg_path) not in sys.path:
                sys.path.append(str(pkg_path))

        importlib.import_module(module_name)
        return sys.modules[module_name]
    else:
        # Assume mode is a ModuleSpec.
        spec = mode
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module


def ensure_extended_length_path(path: Path) -> Path:
    """Get the extended-length version of a path (Windows).

    On Windows, by default, the maximum length of a path (MAX_PATH) is 260
    characters, and operations on paths longer than that fail. But it is possible
    to overcome this by converting the path to "extended-length" form before
    performing the operation:
    https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file#maximum-path-length-limitation

    On Windows, this function returns the extended-length absolute version of path.
    On other platforms, it returns path unchanged.
    """
    if sys.platform.startswith("win32"):
        path = path.resolve()
        path = Path(get_extended_length_path_str(str(path)))
    return path


def get_extended_length_path_str(path: str) -> str:
    """Convert to extended-length path as a string."""
    long_path_prefix = "\\\\?\\"
    unc_long_path_prefix = "\\\\?\\UNC\\"
    if path.startswith((long_path_prefix, unc_long_path_prefix)):
        return path
    # UNC
    if path.startswith("\\\\"):
        return unc_long_path_prefix + path[2:]
    return long_path_prefix + path


def bestrelpath(directory: Path, target: Path) -> str:
    """Return a string which is a relative path from directory to target such that
    directory/bestrelpath == target.

    The paths must be either both absolute or both relative.

    If no such path can be determined, returns target unchanged.
    """
    if directory.is_absolute() != target.is_absolute():
        return str(target)
    try:
        return str(target.relative_to(directory))
    except ValueError:
        # path not relative, return the target path unchanged
        return str(target)


def commonpath(path1: Path, path2: Path) -> Optional[Path]:
    """Return the common part shared by path1 and path2, without trailing
    separators.

    If there is no common part, returns None.
    """
    try:
        return Path(os.path.commonpath((str(path1), str(path2))))
    except ValueError:
        return None


def visit(
    path: Union[str, "os.PathLike[str]"], recurse: Callable[["os.DirEntry[str]"], bool]
) -> Iterator["os.DirEntry[str]"]:
    """Walk a directory tree, yielding all file entries.

    :param path: Starting path to walk from.
    :param recurse: Function called with a ``os.DirEntry`` object for
        each directory encountered, should return True if the directory
        should be recursed into.
    """
    entries = []
    try:
        entries = list(os.scandir(path))
    except OSError:
        return
    
    entries.sort(key=lambda entry: entry.name)
    
    yield from entries
    
    for entry in entries:
        if entry.is_dir() and recurse(entry):
            yield from visit(entry.path, recurse)