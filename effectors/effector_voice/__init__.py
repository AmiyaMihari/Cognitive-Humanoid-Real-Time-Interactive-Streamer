"""effector_voice -- the speaking effector.

Public contract is deliberately tiny: give it text, get back an audio file.

    >>> from effectors.effector_voice import speak
    >>> path = speak("Hola, soy Chris.")   # -> Path to a WAV file

It is the spoken counterpart of `mind`: where `mind` turns text into a reply,
this effector turns that reply into sound. Backed by Qwen3-TTS VoiceDesign, with
a custom voice instruction by default. The model is built once and cached, so
repeated calls are cheap.
"""

from __future__ import annotations

import os
from pathlib import Path

from .synthesizer import Voice

__all__ = ["speak", "Voice", "get_voice"]


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


def speak(text: str) -> Path:
    """Synthesize text with the shared Voice and return the audio file path."""
    return get_voice().speak(text)
