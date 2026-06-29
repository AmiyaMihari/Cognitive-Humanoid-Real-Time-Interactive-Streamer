# `effectors.effector_voice._models` (internal)

Source: [`effectors/effector_voice/_models.py`](../../../../effectors/effector_voice/_models.py)

> **Internal module.** No stable public API; it centralizes Qwen3-TTS model
> defaults, cache configuration and the identity-bank layout. Callers use
> [`effector_voice`](README.md), never this directly.

## What it does

The Qwen3-TTS weights are too large to vendor in the repo. The `qwen_tts`/Hugging
Face loader downloads them lazily on first use and stores them in the normal
Hugging Face cache, or in `CHRIS_VOICE_CACHE` if set.

There are **two** models: a runtime *clone* model (Base) and a baking-only
*design* model (VoiceDesign). The Base model ignores emotion `instruct`, so
emotion is frozen into each reference clip at bake time; the runtime only clones.

## Defaults

| Setting | Value |
| --- | --- |
| Clone (runtime) model | `Qwen/Qwen3-TTS-12Hz-1.7B-Base` |
| Design (baking) model | `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` |
| Language | `Spanish` |
| Default emotion | `neutral` |
| Emotions | `neutral`, `happy`, `sad`, `angry`, `fear`, `shame` |
| Identity dir | `effectors/effector_voice/identity/` |

## Constants

| Name | Description |
| --- | --- |
| `CLONE_MODEL_ID` | Runtime Base model id. |
| `DESIGN_MODEL_ID` | Baking VoiceDesign model id. |
| `DEFAULT_LANGUAGE` | `"Spanish"`. |
| `DEFAULT_VOICE_DESCRIPTION` | The persona `instruct` used when baking `neutral`. |
| `DEFAULT_REF_TEXT` | Exact transcription of the neutral clip, used as `ref_text` for ICL cloning. |
| `EMOTIONS` | The list of supported emotions. |
| `DEFAULT_EMOTION` | `"neutral"`. |
| `EMOTION_INSTRUCTS` | Per-emotion `instruct` modifiers composed on top of `DEFAULT_VOICE_DESCRIPTION` by the bake script (marked `TODO(v2)`). |

## API (internal)

### `get_model_id() -> str`

Return `CHRIS_VOICE_MODEL` when set, otherwise `CLONE_MODEL_ID` (the Base model).

### `get_design_model_id() -> str`

Return `CHRIS_VOICE_DESIGN_MODEL` when set, otherwise `DESIGN_MODEL_ID`.

### `get_cache_dir() -> Path | None`

Return `CHRIS_VOICE_CACHE` as a `Path` when set. `None` lets Hugging Face use its
standard cache.

### `get_identity_dir() -> Path`

Return the identity bank directory: `CHRIS_VOICE_IDENTITY_DIR` if set, otherwise
`effectors/effector_voice/identity/`.

### `get_manifest_path() -> Path`

Return `<identity dir>/manifest.json`, the source of truth for which emotions are
baked.

## Related pages

- [synthesizer.md](synthesizer.md) - uses these defaults to build the engine.
- [baking-the-voice.md](baking-the-voice.md) - how the identity bank is populated.
- [README.md](README.md) - the module's public API.
