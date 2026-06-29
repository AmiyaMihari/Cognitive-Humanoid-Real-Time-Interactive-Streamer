"""effector_voice -- the speaking effector.

Public contract is deliberately tiny: give it text, get back an audio file.

    >>> from effectors.effector_voice import speak
    >>> path = speak("Hola, soy Chris.")   # -> Path to a WAV file

It is the spoken counterpart of `mind`: where `mind` turns text into a reply,
this effector turns that reply into sound. Backed by Qwen3-TTS: the voice
identity is baked once into reference clips (design-once) and cloned at runtime
(see `scripts/bake_voice.py`), which keeps the voice stable across calls. The
model is built once and cached, so repeated calls are cheap.

Call :func:`warmup` at app startup to load the model and prime CUDA kernels so
the first real sentence is fast. For low-latency playback, stream sentence by
sentence with :func:`synthesize_stream` / :func:`speak_stream`.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import numpy as np

from .synthesizer import Voice

__all__ = [
    "speak",
    "Voice",
    "get_voice",
    "warmup",
    "synthesize_stream",
    "speak_stream",
]


def _load_settings() -> None:
    """Load optional voice settings from the project .env file."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    load_dotenv(os.path.join(root, ".env"), override=False)
    load_dotenv(override=False)


_load_settings()

# Process-wide singleton so the model is only built once.
_default: Voice | None = None


def get_voice() -> Voice:
    """Return the shared default Voice, creating it on first use."""
    global _default
    if _default is None:
        _default = Voice()
    return _default


def speak(text: str, emotion: str | None = None) -> Path:
    """Synthesize text with the shared Voice and return the audio file path."""
    return get_voice().speak(text, emotion=emotion)


def warmup() -> None:
    """Build the model and prime kernels so the first real sentence is fast."""
    get_voice().warmup()


def synthesize_stream(
    text: str, emotion: str | None = None, prefetch: int = 1
) -> Iterator[tuple[np.ndarray, int]]:
    """Stream (samples, sample_rate) sentence by sentence with prefetch."""
    return get_voice().synthesize_stream(text, emotion=emotion, prefetch=prefetch)


def speak_stream(
    text: str, emotion: str | None = None, prefetch: int = 1
) -> Iterator[Path]:
    """Stream per-sentence WAV file paths with prefetch."""
    return get_voice().speak_stream(text, emotion=emotion, prefetch=prefetch)
