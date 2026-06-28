"""Runtime preloading of the CUDA 12 libraries used by CTranslate2.

CTranslate2 4.8 (the engine behind faster-whisper) is compiled against CUDA 12
and looks for ``libcublas.so.12`` / ``libcudnn.so.9`` via ``dlopen`` the first
time it runs a model on the GPU. On a machine whose system toolkit is a
different major version (e.g. CUDA 13), those exact sonames are not on the
loader path and the GPU call fails with::

    RuntimeError: Library libcublas.so.12 is not found or cannot be loaded

The ``nvidia-cublas-cu12`` / ``nvidia-cudnn-cu12`` wheels ship those libraries
inside the virtual environment. We locate them and load them into the process
with ``RTLD_GLOBAL`` *before* CTranslate2 needs them. Because they are then
already resident under the expected soname, CTranslate2's own ``dlopen``
resolves to them. This keeps the module self-contained: no environment
variables and no LD_LIBRARY_PATH editing required.
"""

from __future__ import annotations

import ctypes
import glob
import os

# Primary libraries to preload, in dependency order (cublasLt before cublas).
# Loading the main cuDNN library pulls its sub-libraries in via rpath.
_PRELOAD_ORDER = (
    ("cublas", "libcublasLt.so.12"),
    ("cublas", "libcublas.so.12"),
    ("cudnn", "libcudnn.so.9"),
)

_done = False


def _nvidia_lib_dirs() -> dict[str, str]:
    """Return {package_name: lib_dir} for the installed nvidia-*-cu12 wheels."""
    try:
        import nvidia  # namespace package created by the nvidia-*-cu12 wheels
    except ImportError:
        return {}

    dirs: dict[str, str] = {}
    for root in nvidia.__path__:  # may be several entries for a namespace pkg
        for name in ("cublas", "cudnn"):
            lib_dir = os.path.join(root, name, "lib")
            if os.path.isdir(lib_dir):
                dirs.setdefault(name, lib_dir)
    return dirs


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

    loaded_any = False
    for pkg, soname in _PRELOAD_ORDER:
        lib_dir = lib_dirs.get(pkg)
        if not lib_dir:
            continue
        # Match the exact soname, or fall back to any matching versioned file.
        candidates = [os.path.join(lib_dir, soname)]
        candidates += sorted(glob.glob(os.path.join(lib_dir, soname.split(".so")[0] + ".so*")))
        for path in candidates:
            if not os.path.exists(path):
                continue
            try:
                ctypes.CDLL(path, mode=ctypes.RTLD_GLOBAL)
                loaded_any = True
                break
            except OSError:
                continue

    _done = loaded_any
    return loaded_any
