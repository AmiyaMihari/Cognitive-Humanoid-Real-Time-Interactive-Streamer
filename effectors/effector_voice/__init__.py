"""effector_voice -- the speaking effector.

Public contract is deliberately tiny: give it text, get back an audio file.

    >>> from effectors.effector_voice import speak
    >>> path = speak("Hola, soy Chris.")   # -> Path to a WAV file

It is the spoken counterpart of `mind`: where `mind` turns text into a reply,
this effector turns that reply into sound. Backed by Kokoro (a small, fast,
local, free TTS model) running on CPU, with a youthful Spanish female voice by
default. The model is built once and cached, so repeated calls are cheap.
"""

from __future__ import annotations

from pathlib import Path

from .synthesizer import Voice

__all__ = ["speak", "Voice", "get_voice"]

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
