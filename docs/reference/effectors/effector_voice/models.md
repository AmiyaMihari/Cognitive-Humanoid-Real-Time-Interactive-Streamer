# `effectors.effector_voice._models` (internal)

Source: [`effectors/effector_voice/_models.py`](../../../../effectors/effector_voice/_models.py)

> **Internal module.** No stable public API; it only centralizes Qwen3-TTS model
> defaults and cache configuration. Callers use [`effector_voice`](README.md),
> never this directly.

## What it does

The Qwen3-TTS VoiceDesign weights are too large to vendor in the repo. The
`qwen_tts`/Hugging Face loader downloads them lazily on first use and stores
them in the normal Hugging Face cache, or in `CHRIS_VOICE_CACHE` if set.

## Defaults

| Setting | Value |
| --- | --- |
| Model | `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` |
| Language | `Spanish` |
| Voice description | Cute, soft anime femboy voice; native Latin American Spanish pronunciation; calm medium-paced delivery; controlled volume; dry tsundere wit; no shouting. |

## API (internal)

### `get_model_id() -> str`

Return `CHRIS_VOICE_MODEL` when set, otherwise the default VoiceDesign model id.

### `get_cache_dir() -> Path | None`

Return `CHRIS_VOICE_CACHE` as a `Path` when set. Returning `None` lets Hugging
Face use its standard cache directory.

## Related pages

- [synthesizer.md](synthesizer.md) - uses these defaults to build the engine.
- [README.md](README.md) - the module's public API.
