"""Runtime preloading of the CUDA 12 libraries used by CTranslate2.

CTranslate2 4.8 (the engine behind faster-whisper) is compiled against CUDA 12
and looks for cuBLAS / cuDNN the first time it runs a model on the GPU. On a
machine whose system toolkit is a different major version (e.g. CUDA 13), those
exact library versions are not on the loader path and the GPU call fails with::

    RuntimeError: Library libcublas.so.12 is not found or cannot be loaded

The ``nvidia-cublas-cu12`` / ``nvidia-cudnn-cu12`` wheels ship those libraries
inside the virtual environment. We locate them and load them into the process
*before* CTranslate2 needs them, so its own load resolves to them. This keeps
the module self-contained: no environment variables, no LD_LIBRARY_PATH / PATH
editing required.

Cross-platform: on Linux the libraries are ``lib*.so.*`` under ``.../lib`` and
are preloaded with ``RTLD_GLOBAL``; on Windows they are ``*64_*.dll`` under
``.../bin`` and the directory is registered with ``os.add_dll_directory`` so the
DLLs (and their dependencies) resolve. Everything is best-effort: if it fails,
``Transcriber`` still falls back to CPU.
"""

from __future__ import annotations

import ctypes
import glob
import os

_IS_WINDOWS = os.name == "nt"

# Where each wheel keeps its shared libraries, and the primary files to preload
# in dependency order (cublasLt before cublas; the main cuDNN lib pulls the rest).
if _IS_WINDOWS:
    _LIB_SUBDIR = "bin"
    _PRELOAD_ORDER = (
        ("cublas", "cublasLt64_12.dll"),
        ("cublas", "cublas64_12.dll"),
        ("cudnn", "cudnn64_9.dll"),
    )
else:
    _LIB_SUBDIR = "lib"
    _PRELOAD_ORDER = (
        ("cublas", "libcublasLt.so.12"),
        ("cublas", "libcublas.so.12"),
        ("cudnn", "libcudnn.so.9"),
    )

_done = False
# Keep os.add_dll_directory cookies alive for the process lifetime (Windows):
# letting them be garbage-collected would un-register the directory.
_dll_dir_cookies: list = []


def _nvidia_lib_dirs() -> dict[str, str]:
    """Return {package_name: lib_dir} for the installed nvidia-*-cu12 wheels."""
    try:
        import nvidia  # namespace package created by the nvidia-*-cu12 wheels
    except ImportError:
        return {}

    dirs: dict[str, str] = {}
    for root in nvidia.__path__:  # may be several entries for a namespace pkg
        for name in ("cublas", "cudnn"):
            lib_dir = os.path.join(root, name, _LIB_SUBDIR)
            if os.path.isdir(lib_dir):
                dirs.setdefault(name, lib_dir)
    return dirs


def _glob_pattern(soname: str) -> str:
    """A wildcard that matches versioned variants of a library file name."""
    if soname.endswith(".dll"):
        return soname.split(".dll")[0] + "*.dll"
    return soname.split(".so")[0] + ".so*"


def _load(path: str) -> bool:
    """Load one shared library into the process. Returns True on success."""
    try:
        if _IS_WINDOWS:
            ctypes.CDLL(path)
        else:
            ctypes.CDLL(path, mode=ctypes.RTLD_GLOBAL)
        return True
    except OSError:
        return False


def preload_cuda_libraries() -> bool:
    """Preload the CUDA 12 libs so CTranslate2 can find them on the GPU.

    Idempotent and best-effort: failures are swallowed so that CPU-only use
    (or a correctly configured system) is never blocked. Returns True if the
    expected libraries were located and loaded.
    """
    global _done
    if _done:
        return True

    lib_dirs = _nvidia_lib_dirs()
    if not lib_dirs:
        return False

    # On Windows, register the lib directories so dependent DLLs also resolve.
    if _IS_WINDOWS:
        for lib_dir in dict.fromkeys(lib_dirs.values()):
            try:
                _dll_dir_cookies.append(os.add_dll_directory(lib_dir))
            except (OSError, AttributeError):
                pass

    loaded_any = False
    for pkg, soname in _PRELOAD_ORDER:
        lib_dir = lib_dirs.get(pkg)
        if not lib_dir:
            continue
        # Try the exact file name, then any matching versioned variant.
        candidates = [os.path.join(lib_dir, soname)]
        candidates += sorted(glob.glob(os.path.join(lib_dir, _glob_pattern(soname))))
        for path in candidates:
            if os.path.exists(path) and _load(path):
                loaded_any = True
                break

    _done = loaded_any
    return loaded_any
