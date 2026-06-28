"""mind -- the thinking faculty.

Public contract is deliberately tiny: give it text, get back a reply.

    >>> from mind import think
    >>> reply = think("Hola, ¿cómo estás?")

Backed by an OpenAI chat model wired through a minimal LangGraph graph. The
model is built once and cached, so repeated calls are cheap.
"""

from __future__ import annotations

import os

from .agent import Mind

__all__ = ["think", "Mind", "get_mind"]


def _load_secrets() -> None:
    """Load OPENAI_API_KEY (and friends) from a git-ignored .env file.

    Values already present in the real environment win, so an explicitly
    exported key is never clobbered.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    # Project root is two levels up: mind/__init__.py -> root.
    root = os.path.dirname(os.path.dirname(__file__))
    load_dotenv(os.path.join(root, ".env"), override=False)
    load_dotenv(override=False)  # also honour a .env in the current directory


_load_secrets()

# Process-wide singleton so the model client is only built once.
_default: Mind | None = None


def get_mind() -> Mind:
    """Return the shared default Mind, creating it on first use."""
    global _default
    if _default is None:
        _default = Mind()
    return _default


def think(text: str) -> str:
    """Send text to the shared Mind and return its reply."""
    return get_mind().think(text)
