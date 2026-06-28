# `effectors.effector_voice._models` (internal)

Source: [`effectors/effector_voice/_models.py`](../../../../effectors/effector_voice/_models.py)

> **Internal module.** No stable public API; it only ensures the Kokoro model
> files are present. Callers use [`effector_voice`](README.md), never this directly.

## What it does

The Kokoro acoustic model (`kokoro-v1.0.onnx`, ~310 MB) and voice pack
(`voices-v1.0.bin`, ~27 MB) are too large to vendor in the repo. This module
downloads them once to a user cache directory and reuses them thereafter — the
same approach faster-whisper uses for its weights.

The assets are pinned to the **Kokoro v1.0** release (Apache-2.0), so the voice
never changes underneath the project.

## Cache location

| | |
| --- | --- |
| Default | `~/.cache/chris/voice/` |
| Override | set the `CHRIS_VOICE_CACHE` environment variable |

## API (internal)

### `ensure_model_files() -> tuple[Path, Path]`

Return `(model_path, voices_path)`, downloading any missing file first.

- **Idempotent** — existing files are reused; only missing ones are fetched.
- **Atomic** — each file downloads to a `.part` temp file and is renamed into
  place only once complete, so an interrupted download never leaves a corrupt
  model behind.
- **Return order** matches `kokoro_onnx.Kokoro(model, voices)`.

Called by `Voice.engine` on first model load.

## Related pages

- [synthesizer.md](synthesizer.md) — uses these files to build the engine.
- [README.md](README.md) — the module's public API.
