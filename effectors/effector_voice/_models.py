"""Model-file management for the Kokoro voice (internal).

The Kokoro ONNX model and its voice pack are a few hundred MB, so they are not
vendored in the repo. They are downloaded once to a user cache directory and
reused forever after — the same pattern faster-whisper uses for its weights.
"""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path

# Kokoro v1.0 ONNX assets (Apache-2.0). Pinned to a specific release so the
# voice never changes underneath us.
_BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
_FILES = {
    "kokoro-v1.0.onnx": f"{_BASE}/kokoro-v1.0.onnx",  # ~310 MB, the acoustic model
    "voices-v1.0.bin": f"{_BASE}/voices-v1.0.bin",    # ~27 MB, the voice embeddings
}

# Cache location: override with CHRIS_VOICE_CACHE, else ~/.cache/chris/voice.
_CACHE_DIR = Path(
    os.environ.get("CHRIS_VOICE_CACHE", Path.home() / ".cache" / "chris" / "voice")
)


def _download(url: str, dest: Path) -> None:
    """Download ``url`` to ``dest`` atomically (via a .part temp file)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url) as response, open(tmp, "wb") as out:
        while chunk := response.read(1 << 20):  # 1 MiB at a time
            out.write(chunk)
    tmp.replace(dest)


def ensure_model_files() -> tuple[Path, Path]:
    """Return (model_path, voices_path), downloading them on first use.

    Idempotent: existing files are reused. Returns the paths in the order
    expected by ``kokoro_onnx.Kokoro(model, voices)``.
    """
    paths: dict[str, Path] = {}
    for name, url in _FILES.items():
        dest = _CACHE_DIR / name
        if not dest.exists():
            _download(url, dest)
        paths[name] = dest
    return paths["kokoro-v1.0.onnx"], paths["voices-v1.0.bin"]
