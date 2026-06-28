# Architecture & design decisions

This page explains *how* the project is put together and *why* the key choices
were made. For exact APIs, see [reference/](reference/).

## High-level picture

```
                    ┌────────────────────────────┐
   microphone /     │            app.py          │   Streamlit UI:
   typed text   ──► │  (Streamlit chat frontend) │   text box + mic button
                    └─────────────┬──────────────┘
                                  │ audio bytes
                                  ▼
                    ┌────────────────────────────┐
                    │   senses.sense_ear          │   "hearing" sense
                    │   transcribe(audio) -> str  │   (isolated module)
                    └─────────────┬──────────────┘
                                  │
              ┌───────────────────┴───────────────────┐
              ▼                                        ▼
   ┌─────────────────────┐                 ┌────────────────────────┐
   │  transcriber.py     │                 │   _cuda.py             │
   │  faster-whisper /   │  uses           │   preloads CUDA 12     │
   │  CTranslate2 on GPU │ ◄────────────── │   libs for Blackwell   │
   └─────────────────────┘                 └────────────────────────┘
```

The golden rule: **all speech logic lives inside `senses/sense_ear/`.** The app
(or any other caller) only ever sees `audio in -> text out`. You can swap the UI,
or call the module from a script, without touching the model code.

## Project layout

```
C.H.R.I.S./
├── app.py                  # Streamlit demo (UI only; no Whisper code here)
├── senses/                 # perception modules, one sub-package per sense
│   ├── __init__.py
│   └── sense_ear/          # hearing: speech-to-text
│       ├── __init__.py     # public API: transcribe(), get_transcriber(), Transcriber
│       ├── transcriber.py  # the engine (faster-whisper wrapper)
│       └── _cuda.py        # internal: CUDA 12 library preloading
├── requirements.txt        # pinned, tested dependency versions
├── .env.example            # template for the optional HF_TOKEN secret
├── txt_interviews.ipynb    # original notebook this module was derived from
└── docs/                   # you are here
```

## Key design decisions

### The module is isolated

`sense_ear` exposes a tiny contract (`transcribe(audio) -> str`) and hides
faster-whisper, CTranslate2, CUDA handling and model lifecycle behind it.
Benefits: the UI stays trivial, the engine is unit-testable in isolation, and
future senses (vision, etc.) slot in next to it under `senses/`.

### Tuned for short, real-time audio

The original notebook (`txt_interviews.ipynb`) processed long interview files.
This module instead targets **short, live utterances**: lighter VAD silence
thresholds and `condition_on_previous_text=False` so each clip is transcribed
independently, avoiding cross-clip hallucinations and repetition loops. The
model itself is unchanged: Spanish `large-v3`.

### GPU first, with a transparent CPU fallback

Default is `cuda` + `float16`. If CUDA initialization fails, the `Transcriber`
silently falls back to CPU (`int8`) so the app still works. The actual device in
use is exposed via `Transcriber.device`.

### The Blackwell / CUDA 12 quirk

The GPU is an **RTX 5070 Ti (Blackwell, sm_120)**. CTranslate2 4.8 is compiled
against **CUDA 12** and `dlopen`s `libcublas.so.12` / `libcudnn.so.9` at GPU
time. The system, however, ships **CUDA 13**, so those exact sonames are not on
the loader path and GPU calls fail.

The fix lives entirely inside the module: the `nvidia-cublas-cu12` /
`nvidia-cudnn-cu12` wheels (versions 12.9 / 9.23, which include Blackwell
kernels) provide the libraries, and [`_cuda.py`](reference/senses/sense_ear/cuda.md)
preloads them into the process with `RTLD_GLOBAL` before CTranslate2 needs them.
No `LD_LIBRARY_PATH` editing required — the module is self-contained.

### Why Python 3.12 via uv

The system Python is 3.14, which is too new for parts of the ML ecosystem
(notably PyTorch/pyannote, needed if speaker diarization is added later). The ML
community consensus is **Python 3.11–3.12**. We standardized on **3.12**,
installed with **`uv`** because it needs no `sudo` and produces a self-contained
interpreter and venv.

### Secrets via .env

`HF_TOKEN` is optional (the `large-v3` weights are public). When present, it is
read from a git-ignored `.env` file through `python-dotenv`, loaded
automatically when the module is imported. Real environment variables always win
over `.env` values.

## Dependency overview

| Dependency | Role |
| --- | --- |
| `faster-whisper` + `ctranslate2` | Whisper inference engine (no PyTorch needed) |
| `nvidia-cublas-cu12`, `nvidia-cudnn-cu12` | CUDA 12 libs with Blackwell support |
| `python-dotenv` | Loads the `HF_TOKEN` secret from `.env` |
| `streamlit`, `streamlit-mic-recorder` | Demo UI and in-browser microphone capture |
