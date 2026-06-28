# `effectors.effector_voice` - text-to-speech

Source: [`effectors/effector_voice/__init__.py`](../../../../effectors/effector_voice/__init__.py)

The **speaking** effector. Its entire contract is:

> **text in -> voice audio file out.**

It is the spoken counterpart of [`mind`](../../mind/README.md): where `mind`
turns text into a reply, this effector turns that reply into sound. Backed by
Qwen3-TTS VoiceDesign, it keeps the rest of the app isolated from model loading,
device choice and voice-design prompts.

---

## Quick start

```python
from effectors.effector_voice import speak

path = speak("Hola, soy Chris.")   # -> pathlib.Path to a WAV file
```

That single call:

1. Lazily builds a shared `Voice` the first time it runs.
2. Loads the Qwen3-TTS VoiceDesign model, downloading weights on first use.
3. Synthesizes the text with language set to `Spanish` and the default custom voice
   description.
4. Writes a WAV file and returns its `Path`.

---

## Public API

The module exports three names (`__all__`):

| Name | Kind | Summary |
| --- | --- | --- |
| [`speak(text)`](#speaktext---path) | function | One-shot convenience: text -> audio file using a shared voice. |
| [`get_voice()`](#get_voice---voice) | function | Returns the process-wide shared `Voice`. |
| [`Voice`](#class-voice) | class | Configurable engine; use for a different instruction, language, model or output directory. |

### `speak(text) -> Path`

Synthesize a piece of text and return the path to the generated WAV file.

- **Parameter** - `text`: the text to speak (for example, `mind`'s reply).
- **Returns** - `pathlib.Path` to a `.wav` file. A new uniquely named file is
  written per call.

```python
from effectors.effector_voice import speak

path = speak("¿En qué puedo ayudarte?")
print(path)        # /tmp/chris_voice/reply_<hex>.wav
```

### `get_voice() -> Voice`

Return the **shared, process-wide** `Voice` (created on first call, reused
after). Use it when you want the singleton but also need the object, for example
to synthesize in-memory audio:

```python
from effectors.effector_voice import get_voice

samples, sample_rate = get_voice().synthesize("Hola")
```

### class `Voice`

The configurable engine. Constructor summary:

```python
Voice(
    voice="Cute, soft anime femboy voice; youthful, gentle, and clear. "
          "Native Latin American Spanish pronunciation. Calm, conversational "
          "delivery at a medium pace...",
    lang="Spanish",
    speed=1.0,
    output_dir=None,
    model=None,
    device=None,
    dtype=None,
    attn_implementation=None,
)
```

Methods: `Voice.speak(text, path=None) -> Path` (write a file) and
`Voice.synthesize(text) -> (np.ndarray, int)` (raw audio in memory).

---

## Behaviour notes

- **Module isolation.** The public surface stays `text -> audio file`; Qwen3-TTS
  details do not leak into `app.py`, `mind` or other modules.
- **Model loads once.** The first call (or `Voice.engine` access) downloads and
  loads the model. Subsequent calls reuse the same in-process engine.
- **Default model.** `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`.
- **Default language.** `Spanish`, which keeps the Spanish accent more stable
  than `Auto` for mixed text, formulas and occasional English terms.
- **Default voice instruction.** A compact vocal direction: cute soft anime
  femboy timbre, native Latin American Spanish pronunciation, calm medium-paced
  delivery, controlled volume, dry tsundere wit, no shouting.
- **One WAV per answer in the app.** `app.py` streams the assistant text, then
  calls this module once for the full reply. That avoids Qwen3-TTS redesigning a
  different voice for each paragraph.
- **Lazy model load by default.** Qwen3-TTS loads on first speech so Streamlit
  opens with low VRAM use. Set `CHRIS_VOICE_WARMUP=1` to load it at app startup.

---

## Environment overrides

| Variable | Purpose |
| --- | --- |
| `CHRIS_VOICE_MODEL` | Hugging Face model id or local model directory. |
| `CHRIS_VOICE_CACHE` | Optional Hugging Face cache directory for Qwen3-TTS weights. |
| `CHRIS_VOICE_LANGUAGE` | Language passed to Qwen3-TTS. Defaults to `Spanish`; set `Auto` to restore automatic language detection. |
| `CHRIS_VOICE_DEVICE` | Device map passed to Qwen3-TTS, for example `cuda:0` or `cpu`. Defaults to CUDA when available. |
| `CHRIS_VOICE_DTYPE` | `auto`, `bfloat16`, `float16` or `float32`. Defaults to `auto`. |
| `CHRIS_VOICE_ATTN` | Optional Transformers attention implementation, for example `flash_attention_2` if installed. |
| `CHRIS_VOICE_DISABLE_CUDNN` | Defaults to `1`. Disables cuDNN only for Qwen3-TTS to avoid a local PyTorch cu130/Blackwell decode mismatch. Set `0` to try cuDNN again after upgrading the stack. |
| `CHRIS_VOICE_MAX_NEW_TOKENS` | Generation cap for the audio codes. Defaults to `2048`; lower values are faster but can cut long answers. |
| `CHRIS_VOICE_WARMUP` | App-level option. Set `1` to load Qwen-TTS when Streamlit starts; default `0` loads it on first speech to keep VRAM free. |

---

## Related pages

- [synthesizer.md](synthesizer.md) - the `Voice` class in full.
- [models.md](models.md) - Qwen3-TTS model/cache configuration (internal).
- [mind/](../../mind/README.md) - produces the text that this effector speaks.
- [architecture.md](../../../architecture.md) - where this module fits and why.
