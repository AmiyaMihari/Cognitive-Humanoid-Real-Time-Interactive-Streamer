"""Qwen3-TTS model configuration for the voice effector (internal).

Qwen3-TTS model weights are not vendored in this repository. The
``qwen_tts``/Hugging Face stack downloads them lazily on first use and reuses
the normal Hugging Face cache afterwards.
"""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
DEFAULT_LANGUAGE = "Spanish"
DEFAULT_VOICE_DESCRIPTION = (
    "Cute, soft anime femboy voice; youthful, gentle, and clear. Native Latin "
    "American Spanish pronunciation with no English or Spanglish accent. Calm, "
    "conversational delivery at a medium pace and controlled volume. Dry, "
    "cynical, carefree tsundere wit; lightly sharp-tongued and intellectual, "
    "but not angry. No swearing, no shouting, and avoid dramatic rising "
    "intonation at sentence endings."
)


def get_model_id() -> str:
    """Return the Qwen3-TTS model id or local path to load."""
    return os.environ.get("CHRIS_VOICE_MODEL") or DEFAULT_MODEL_ID


def get_cache_dir() -> Path | None:
    """Return the optional Hugging Face cache override for voice models."""
    cache_dir = os.environ.get("CHRIS_VOICE_CACHE")
    return Path(cache_dir).expanduser() if cache_dir else None
