# `senses.sense_ear._cuda` (internal)

Source: [`senses/sense_ear/_cuda.py`](../../../../senses/sense_ear/_cuda.py)

> **Internal module.** It has no stable public API and exists only so the GPU
> path works on this machine. Callers never need to touch it.

## The problem it solves

CTranslate2 4.8 (the engine behind faster-whisper) is compiled against **CUDA
12**. The first time it runs a model on the GPU it `dlopen`s `libcublas.so.12`
and `libcudnn.so.9`. On a system whose toolkit is a different major version
(here: **CUDA 13**), those exact sonames are not on the loader path and the GPU
call fails:

```
RuntimeError: Library libcublas.so.12 is not found or cannot be loaded
```

The `nvidia-cublas-cu12` / `nvidia-cudnn-cu12` wheels ship those libraries
inside the virtual environment (versions 12.9 / 9.23, which include kernels for
Blackwell / RTX 50-series, `sm_120`). This module makes them resolvable.

## How it works

`preload_cuda_libraries()` finds the libraries inside the installed
`nvidia-*-cu12` wheels and loads them into the process with `RTLD_GLOBAL`
**before** CTranslate2 needs them. Once resident under the expected soname,
CTranslate2's own `dlopen` resolves to them.

Libraries are loaded in dependency order:

1. `libcublasLt.so.12`
2. `libcublas.so.12`
3. `libcudnn.so.9` (pulls its sub-libraries in via rpath)

### `preload_cuda_libraries() -> bool`

- Called automatically by `Transcriber._load_model()` before the GPU is touched.
- **Idempotent**: safe to call repeatedly; only acts once.
- **Best-effort**: failures are swallowed, so CPU-only use (or a correctly
  configured system) is never blocked.
- **Returns** `True` if the expected libraries were located and loaded.

## Why this approach

Keeping the fix inside the module means it is **self-contained**: no
`LD_LIBRARY_PATH` exports, no system CUDA toolkit, no wrapper scripts. Installing
the requirements and importing the module is enough for the GPU to work.

See [architecture.md](../../../architecture.md#the-blackwell--cuda-12-quirk) for
the broader context.
