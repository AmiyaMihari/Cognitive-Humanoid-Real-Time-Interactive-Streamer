"""sense_ear -- the hearing sense.

Public contract is deliberately tiny: give it audio, get back text.

    >>> from senses.sense_ear import transcribe
    >>> text = transcribe(audio_bytes)

The model is loaded once and cached, so repeated calls are cheap. For explicit
control over the model/device use the :class:`Transcriber` class directly.
"""

from __future__ import annotations

import os

from .transcriber import AudioInput, Transcriber

__all__ = ["transcribe", "Transcriber", "AudioInput", "get_transcriber"]


def _load_secrets() -> None:
    """Load secrets (e.g. HF_TOKEN) from a git-ignored .env file.

    Values already present in the real environment win, so this never clobbers
    an explicitly exported token. Entirely optional: the public large-v3
    weights need no token at all.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    # Project root is three levels up: senses/sense_ear/__init__.py -> root.
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    load_dotenv(os.path.join(root, ".env"), override=False)
    load_dotenv(override=False)  # also honour a .env in the current directory


_load_secrets()

# Process-wide singleton so the (heavy) model is only built once.
_default: Transcriber | None = None


def get_transcriber() -> Transcriber:
    """Return the shared default Transcriber, creating it on first use."""
    global _default
    if _default is None:
        _default = Transcriber()
    return _default


def transcribe(audio: AudioInput) -> str:
    """Transcribe a short audio clip to text using the shared transcriber."""
    return get_transcriber().transcribe(audio)
