# How to bake or change Chris's voice

A **how-to guide** (task recipe). For the API see [README.md](README.md); for the
CLI flags see [scripts/bake_voice.md](../../scripts/bake_voice.md); for *why* it
works this way see [architecture.md](../../../architecture.md#the-voice-effector-speaking).

The voice uses a **design-once -> clone** pattern. You bake an identity once with
the VoiceDesign model into a fixed reference clip; from then on the runtime only
*clones* that clip with the Base model, so the voice stays stable across replies.
This page is how you create or replace those clips.

> ⚠️ Until you bake `neutral`, `speak()` and `warmup()` fail with a clear error
> telling you to run the bake script. This is intentional — it fails early, not
> mid-conversation.

## Bake the neutral voice (required, do this once)

```bash
# 1. Generate candidates to audition.
python scripts/bake_voice.py --emotion neutral --n 6
#    -> effectors/effector_voice/identity/neutral/candidates/cand_01.wav ... cand_06.wav

# 2. Listen to them, then promote the one you like to the reference clip.
python scripts/bake_voice.py --emotion neutral --choose cand_03
```

Step 2 copies `cand_03.wav` to `identity/neutral/reference.wav`, writes
`reference.txt` and `meta.json`, and records the clip in
[`manifest.json`](#the-manifest). That is it — `speak("Hola")` now works.

> Note: `--choose` does **not** load the model or generate audio; it only
> promotes a file, so it is instant and uses no GPU. The candidates are **not**
> deleted, so you can re-run `--choose cand_05` any day to switch. (A new
> `--n` run **overwrites** the candidate files — copy them elsewhere first if you
> want to keep them.)

## Add an emotion (later, optional)

The same recipe works for `happy`, `sad`, `angry`, `fear` and `shame`. The bake
script composes the persona description with the per-emotion modifier from
`EMOTION_INSTRUCTS` automatically:

```bash
python scripts/bake_voice.py --emotion happy --n 6
python scripts/bake_voice.py --emotion happy --choose cand_02
```

Until an emotion is baked, requesting it (`speak("...", emotion="happy")`) falls
back to `neutral` and warns once.

## The identity bank on disk

```
effectors/effector_voice/identity/
├── manifest.json          # source of truth: which emotions are baked
├── neutral/
│   ├── reference.wav      # the frozen clip the runtime clones
│   ├── reference.txt      # == the ref_text used for ICL cloning
│   ├── meta.json          # full provenance for this clip
│   └── candidates/        # auditioned candidates (cand_01.wav ...)
└── happy/ sad/ angry/ fear/ shame/   # empty slots until baked
```

Override the location with `CHRIS_VOICE_IDENTITY_DIR`.

### The manifest

`manifest.json` is what the runtime reads at boot to know which emotions exist.
Each entry records enough to version and reproduce the clip:

```json
{
  "version": 1,
  "emotions": {
    "neutral": {
      "reference": "neutral/reference.wav",
      "ref_text": "Ah, ya volviste. No, no estaba esperándote ...",
      "instruct": "Cute, soft anime femboy voice; ...",
      "language": "Spanish",
      "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
      "created_at": "2026-06-29T06:50:39+00:00",
      "sha256": "6b5e0639...d24f9"
    }
  }
}
```

## Speed it up at runtime

Baking uses the 1.7B VoiceDesign model, but the **runtime** clone model is
independent — you can clone the same reference with a smaller, faster Base model
without re-baking. The 0.6B Base is noticeably quicker:

```ini
# .env
CHRIS_VOICE_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B-Base
```

## Related pages

- [scripts/bake_voice.md](../../scripts/bake_voice.md) - every flag of the CLI.
- [README.md](README.md) - the module's public API and environment overrides.
- [models.md](models.md) - the constants and paths used here.
- [architecture.md](../../../architecture.md#the-voice-effector-speaking) - why
  design-once -> clone.
