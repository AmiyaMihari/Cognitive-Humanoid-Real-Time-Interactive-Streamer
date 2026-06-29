"""Qwen3-TTS model configuration for the voice effector (internal).

Qwen3-TTS model weights are not vendored in this repository. The
``qwen_tts``/Hugging Face stack downloads them lazily on first use and reuses
the normal Hugging Face cache afterwards.

The voice follows a "design-once -> clone" pattern: identity (and, later,
emotion) is frozen once into reference clips with the VoiceDesign model (see
``scripts/bake_voice.py``), and runtime synthesis only *clones* from those
clips with the cheaper, more stable Base model. This keeps the voice identity
from drifting between generations.
"""

from __future__ import annotations

import os
from pathlib import Path

# Runtime model: clones from a fixed reference clip (stable identity).
CLONE_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
# Baking-only model: designs a voice from a text description (used offline).
DESIGN_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"

DEFAULT_LANGUAGE = "Spanish"
DEFAULT_VOICE_DESCRIPTION = (
    "Cute, soft anime femboy voice; youthful, gentle, and clear. Native Latin "
    "American Spanish pronunciation with no English or Spanglish accent. Calm, "
    "conversational delivery at a medium pace and controlled volume. Dry, "
    "cynical, carefree tsundere wit; lightly sharp-tongued and intellectual, "
    "but not angry. No swearing, no shouting, and avoid dramatic rising "
    "intonation at sentence endings."
)

# Exact transcription of the neutral reference clip. Used as ``ref_text`` for
# ICL voice cloning, and as the default text spoken when baking the neutral clip.
DEFAULT_REF_TEXT = (
    "Ah, ya volviste. No, no estaba esperándote ni nada de eso... simplemente "
    "no tenía nada mejor que hacer. En fin, ¿en qué andas? Cuéntame, que para "
    "algo encendí todo esto."
)

# The emotion bank. ``neutral`` is baked first (v1); the rest are slots that the
# runtime falls back away from until they are baked (v2).
EMOTIONS = ["neutral", "happy", "sad", "angry", "fear", "shame"]
DEFAULT_EMOTION = "neutral"

# Per-emotion modifiers composed on top of DEFAULT_VOICE_DESCRIPTION by the bake
# script. These are the ``instruct`` deltas, NOT runtime instructions (the Base
# clone model ignores ``instruct``; emotion is frozen into each reference clip).
EMOTION_INSTRUCTS: dict[str, str] = {
    # TODO(v2): refine wording when baking the emotion bank.
    "happy": "Brighter, more agile and lightly smiling tone; still no shouting.",
    "sad": "Slower and lower, low energy, slightly dimmed.",
    "angry": (
        "Tense and sharp-edged and firm (NOT shouting; keep the no-shout "
        "persona rule)."
    ),
    "fear": "Slightly trembling, shorter breath, a touch higher pitched.",
    "shame": "Quieter, hesitant, turned inward.",
}


def get_model_id() -> str:
    """Return the runtime (clone/Base) Qwen3-TTS model id or local path."""
    return os.environ.get("CHRIS_VOICE_MODEL") or CLONE_MODEL_ID


def get_design_model_id() -> str:
    """Return the baking-only (VoiceDesign) model id or local path."""
    return os.environ.get("CHRIS_VOICE_DESIGN_MODEL") or DESIGN_MODEL_ID


def get_cache_dir() -> Path | None:
    """Return the optional Hugging Face cache override for voice models."""
    cache_dir = os.environ.get("CHRIS_VOICE_CACHE")
    return Path(cache_dir).expanduser() if cache_dir else None


def get_identity_dir() -> Path:
    """Return the directory holding baked voice identity (the emotion bank)."""
    override = os.environ.get("CHRIS_VOICE_IDENTITY_DIR")
    if override:
        return Path(override).expanduser()
    return Path(__file__).resolve().parent / "identity"


def get_manifest_path() -> Path:
    """Return the path to the identity manifest (source of truth for the bank)."""
    return get_identity_dir() / "manifest.json"
