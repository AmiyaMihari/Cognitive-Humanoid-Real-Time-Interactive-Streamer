# `scripts/bake_voice.py` — voice baking CLI

Source: [`scripts/bake_voice.py`](../../../scripts/bake_voice.py)

Offline tool that **creates** the reference clips the runtime clones from
(design-once -> clone). It loads the VoiceDesign model, generates audition
candidates, and promotes a chosen candidate to an emotion's reference clip,
updating the [manifest](../effectors/effector_voice/baking-the-voice.md#the-manifest).

For the task recipe, see
[baking-the-voice.md](../effectors/effector_voice/baking-the-voice.md).

## Usage

```bash
# Generate candidates:
python scripts/bake_voice.py --emotion neutral --n 6

# Promote one to the reference clip:
python scripts/bake_voice.py --emotion neutral --choose cand_03
```

The script has two modes: **generate** (default) and **choose** (when `--choose`
is given). `--choose` only promotes a file; it does not load the model.

## Flags

| Flag | Default | Description |
| --- | --- | --- |
| `--emotion {neutral,happy,sad,angry,fear,shame}` | `neutral` | Which emotion clip to bake. |
| `--n INT` | `6` | Number of audition candidates to generate (`candidates/cand_01.wav` ...). |
| `--ref-text STR` | `DEFAULT_REF_TEXT` | Text spoken in the reference clip. |
| `--language STR` | `Spanish` | Synthesis language. |
| `--instruct STR` | persona | VoiceDesign instruct. Defaults to `DEFAULT_VOICE_DESCRIPTION` for `neutral`, composed with `EMOTION_INSTRUCTS[emotion]` for the others. |
| `--choose cand_NN` | — | Promote this candidate to `reference.wav` and update the manifest. |
| `--unload` | off | Free VRAM when finished. |

## What `--choose` writes

For the chosen emotion it writes, under `identity/<emotion>/`:

- `reference.wav` — a copy of the chosen candidate (the clip the runtime clones).
- `reference.txt` — the `ref_text`.
- `meta.json` — full provenance: emotion, reference path, ref_text, instruct,
  language, model, source candidate, `created_at`, and the wav `sha256`.

It then adds/updates the emotion's entry in `identity/manifest.json`.

## Models

- Generation uses the **design** model (`get_design_model_id()`,
  `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` by default; override with
  `CHRIS_VOICE_DESIGN_MODEL`).
- It reuses [`Voice`](../effectors/effector_voice/synthesizer.md)'s engine builder
  (dtype/device/cuDNN/flash-attn fallback), so the same `CHRIS_VOICE_*`
  environment overrides apply, including `CHRIS_VOICE_DISABLE_CUDNN`.

## Related pages

- [baking-the-voice.md](../effectors/effector_voice/baking-the-voice.md) - the recipe.
- [effector_voice/README.md](../effectors/effector_voice/README.md) - the module it feeds.
- [effector_voice/models.md](../effectors/effector_voice/models.md) - the constants it uses.
