"""Qwen3-TTS model configuration for the voice effector (internal).

Qwen3-TTS model weights are not vendored in this repository. The
``qwen_tts``/Hugging Face stack downloads them lazily on first use and reuses
the normal Hugging Face cache afterwards.
"""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
DEFAULT_LANGUAGE = "Auto"
DEFAULT_VOICE_DESCRIPTION = (
    "Speak in sassy, cute, and soft tones, like a female in her 20s"
    "into our voice. Cute anime soft femboy voice."
)


def get_model_id() -> str:
    """Return the Qwen3-TTS model id or local path to load."""
    return os.environ.get("CHRIS_VOICE_MODEL") or DEFAULT_MODEL_ID


def get_cache_dir() -> Path | None:
    """Return the optional Hugging Face cache override for voice models."""
    cache_dir = os.environ.get("CHRIS_VOICE_CACHE")
    return Path(cache_dir).expanduser() if cache_dir else None
