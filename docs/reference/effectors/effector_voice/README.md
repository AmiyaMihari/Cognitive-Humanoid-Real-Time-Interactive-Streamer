# `effectors.effector_voice` - text-to-speech

Source: [`effectors/effector_voice/__init__.py`](../../../../effectors/effector_voice/__init__.py)

The **speaking** effector. Its entire contract is:

> **text in -> voice audio file out.**

It is the spoken counterpart of [`mind`](../../mind/README.md): where `mind`
turns text into a reply, this effector turns that reply into sound. It keeps the
rest of the app isolated from model loading, device choice and the voice
identity.

The voice follows a **design-once -> clone** pattern: the identity is frozen
*once* into a reference clip with the VoiceDesign model (offline, see
[baking-the-voice.md](baking-the-voice.md)), and every runtime call only
*clones* that clip with the cheaper, more stable Base model. This stops the
voice identity from drifting 10-20% between generations, which is what happened
when the old code re-designed the voice from a text description on every call.

---

## Quick start

```python
from effectors.effector_voice import speak

path = speak("Hola, soy Chris.")   # -> pathlib.Path to a WAV file
```

That single call:

1. Lazily builds a shared `Voice` the first time it runs.
2. Loads the Qwen3-TTS **Base** model, downloading weights on first use.
3. Builds a clone prompt from the baked `neutral` reference clip.
4. Clones the text in Spanish and writes a WAV, returning its `Path`.

> ⚠️ The first call (or `warmup()`) fails with a clear, actionable error if the
> `neutral` voice has not been baked yet. Bake it once with
> `python scripts/bake_voice.py --emotion neutral --n 6` — see
> [baking-the-voice.md](baking-the-voice.md).

---

## Public API

The module exports six names (`__all__`):

| Name | Kind | Summary |
| --- | --- | --- |
| [`speak(text, emotion=None)`](#speaktext-emotionnone---path) | function | One-shot convenience: text -> audio file using a shared voice. |
| [`get_voice()`](#get_voice---voice) | function | Returns the process-wide shared `Voice`. |
| [`warmup()`](#warmup---none) | function | Loads the model and primes CUDA kernels so the first real sentence is fast. |
| [`synthesize_stream(text, emotion=None, prefetch=1)`](#synthesize_streamtext-emotionnone-prefetch1) | function | Yields `(samples, sample_rate)` sentence by sentence with prefetch. |
| [`speak_stream(text, emotion=None, prefetch=1)`](#speak_streamtext-emotionnone-prefetch1) | function | Yields a WAV `Path` per sentence. |
| [`Voice`](#class-voice) | class | Configurable engine; use for a different emotion, language, model or output directory. |

### `speak(text, emotion=None) -> Path`

Synthesize a piece of text and return the path to the generated WAV file.

- **`text`** - the text to speak (for example, `mind`'s reply).
- **`emotion`** - one of `neutral`, `happy`, `sad`, `angry`, `fear`, `shame`.
  Defaults to `neutral`. If the requested emotion is not baked yet, it falls back
  to `neutral` and warns once.
- **Returns** - `pathlib.Path` to a `.wav` file. A new uniquely named file is
  written per call.

```python
from effectors.effector_voice import speak

path = speak("¿En qué puedo ayudarte?")
print(path)                       # /tmp/chris_voice/reply_<hex>.wav
speak("¡No me molestes!", emotion="angry")   # falls back to neutral until baked
```

### `get_voice() -> Voice`

Return the **shared, process-wide** `Voice` (created on first call, reused
after). Use it when you want the singleton but also need the object, for example
to synthesize in-memory audio:

```python
from effectors.effector_voice import get_voice

samples, sample_rate = get_voice().synthesize("Hola")
```

### `warmup() -> None`

Build the model, construct the clone prompts for every baked emotion, and run a
short dummy synthesis to compile CUDA kernels — all at boot, so the first *real*
sentence is fast instead of paying that cost mid-conversation. Idempotent.
Calls `get_voice().warmup()`.

```python
import effectors.effector_voice as voice
voice.warmup()   # call once at app startup
```

`app.py` runs this for you when `CHRIS_VOICE_WARMUP=1`.

### `synthesize_stream(text, emotion=None, prefetch=1)`

Yield `(samples, sample_rate)` one sentence at a time, **in order**, while a
worker thread synthesizes the next sentence ahead of the consumer. Returns an
iterator. See [streaming.md](streaming.md).

### `speak_stream(text, emotion=None, prefetch=1)`

Same as `synthesize_stream`, but writes each sentence to a WAV and yields its
`Path`. Returns an iterator.

### class `Voice`

The configurable engine. See [synthesizer.md](synthesizer.md) for the full
constructor, methods and behaviour.

---

## Behaviour notes

- **Module isolation.** The public surface stays `text -> audio file`; Qwen3-TTS
  details do not leak into `app.py`, `mind` or other modules.
- **Model loads once.** The first call (or `Voice.engine` access) downloads and
  loads the model. Subsequent calls reuse the same in-process engine.
- **Runtime model (clone).** `Qwen/Qwen3-TTS-12Hz-1.7B-Base` by default. The
  smaller `Qwen/Qwen3-TTS-12Hz-0.6B-Base` is noticeably faster; select it with
  `CHRIS_VOICE_MODEL`.
- **Default language.** `Spanish`, which keeps the Spanish accent more stable
  than `Auto` for mixed text, formulas and occasional English terms.
- **Emotion bank.** `neutral` is baked first; `happy`, `sad`, `angry`, `fear`
  and `shame` are slots that fall back to `neutral` until baked. The
  [manifest](baking-the-voice.md#the-manifest) is the source of truth for what
  exists.
- **flash-attention 2 by default**, with a safe fallback: if `flash-attn` is not
  installed or fails to load, the module warns and falls back to the default
  attention implementation instead of crashing.
- **cuDNN enabled by default.** Set `CHRIS_VOICE_DISABLE_CUDNN=1` to disable it
  (required on this Blackwell box — see [synthesizer.md](synthesizer.md)).
- **Lazy model load by default.** Qwen3-TTS loads on first speech so Streamlit
  opens with low VRAM use. Set `CHRIS_VOICE_WARMUP=1` to load it at app startup.

---

## Environment overrides

| Variable | Purpose |
| --- | --- |
| `CHRIS_VOICE_MODEL` | Runtime (clone/Base) model id or local path. Defaults to `Qwen/Qwen3-TTS-12Hz-1.7B-Base`. |
| `CHRIS_VOICE_DESIGN_MODEL` | Baking-only (VoiceDesign) model id. Defaults to `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`. |
| `CHRIS_VOICE_CACHE` | Optional Hugging Face cache directory for Qwen3-TTS weights. |
| `CHRIS_VOICE_LANGUAGE` | Language passed to Qwen3-TTS. Defaults to `Spanish`; set `Auto` to restore automatic language detection. |
| `CHRIS_VOICE_DEVICE` | Device map, for example `cuda:0` or `cpu`. Defaults to CUDA when available. |
| `CHRIS_VOICE_DTYPE` | `auto`, `bfloat16`, `float16` or `float32`. Defaults to `auto` (bf16 on CUDA). |
| `CHRIS_VOICE_ATTN` | Attention implementation. Empty defaults to `flash_attention_2` with a safe fallback. |
| `CHRIS_VOICE_DISABLE_CUDNN` | Defaults to `0` (cuDNN ON). Set `1` to disable cuDNN, needed on the local Blackwell stack to avoid `CUDNN_STATUS_SUBLIBRARY_VERSION_MISMATCH`. |
| `CHRIS_VOICE_IDENTITY_DIR` | Directory holding the baked identity bank. Defaults to `effectors/effector_voice/identity/`. |
| `CHRIS_VOICE_MAX_NEW_TOKENS` | Generation cap for the audio codes. Defaults to `2048`; lower is faster but can cut long answers. |
| `CHRIS_VOICE_WARMUP` | App-level option. Set `1` to warm up Qwen3-TTS when Streamlit starts; default `0` loads it on first speech. |

---

## Related pages

- [baking-the-voice.md](baking-the-voice.md) - **how to bake or change Chris's
  voice** (the `neutral` clip and the emotion bank).
- [synthesizer.md](synthesizer.md) - the `Voice` class in full.
- [streaming.md](streaming.md) - sentence-level streaming helpers.
- [models.md](models.md) - Qwen3-TTS model/cache/identity configuration (internal).
- [scripts/bake_voice.md](../../scripts/bake_voice.md) - the baking CLI reference.
- [mind/](../../mind/README.md) - produces the text that this effector speaks.
- [architecture.md](../../../architecture.md) - where this module fits and why.
