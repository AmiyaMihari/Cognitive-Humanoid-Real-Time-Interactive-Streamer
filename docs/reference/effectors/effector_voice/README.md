# `effectors.effector_voice` — text-to-speech

Source: [`effectors/effector_voice/__init__.py`](../../../../effectors/effector_voice/__init__.py)

The **speaking** effector. Its entire contract is:

> **text in → voice audio file out.**

It is the spoken counterpart of [`mind`](../../mind/README.md): where `mind`
turns text into a reply, this effector turns that reply into sound. Backed by
Kokoro (a small, fast, local, free TTS model) running on CPU, with a youthful
Spanish female voice by default.

---

## Quick start

```python
from effectors.effector_voice import speak

path = speak("Hola, soy Chris.")   # -> pathlib.Path to a WAV file
```

That single call:

1. Lazily builds a shared `Voice` the first time it runs (loads the Kokoro model
   and downloads its files on first ever use). This is the slow part and happens
   **once** per process.
2. Synthesizes the text with the default Spanish female voice.
3. Writes a WAV file and returns its `Path`.

---

## Public API

The module exports three names (`__all__`):

| Name | Kind | Summary |
| --- | --- | --- |
| [`speak(text)`](#speaktext---path) | function | One-shot convenience: text → audio file using a shared voice. |
| [`get_voice()`](#get_voice---voice) | function | Returns the process-wide shared `Voice`. |
| [`Voice`](#class-voice) | class | Configurable engine; use for a different voice, language or speed. |

### `speak(text) -> Path`

Synthesize a piece of text and return the path to the generated WAV file.

- **Parameter** — `text`: the text to speak (e.g. `mind`'s reply).
- **Returns** — `pathlib.Path` to a `.wav` file (24 kHz, mono). A new uniquely
  named file is written per call.

```python
from effectors.effector_voice import speak

path = speak("¿En qué puedo ayudarte?")
print(path)        # /tmp/chris_voice/reply_<hex>.wav
```

### `get_voice() -> Voice`

Return the **shared, process-wide** `Voice` (created on first call, reused
after). Use it when you want the singleton but also need the object — e.g. to
synthesize in-memory audio:

```python
from effectors.effector_voice import get_voice

samples, sample_rate = get_voice().synthesize("Hola")
```

### class `Voice`

The configurable engine. Construct your own instance for a different voice,
language, speaking rate or output directory. Full details in
[synthesizer.md](synthesizer.md). Constructor summary:

```python
Voice(
    voice="ef_dora",   # youthful Spanish female; see synthesizer.md for others
    lang="es",         # phonemization language
    speed=1.0,         # 1.0 = natural; >1 faster, <1 slower
    output_dir=None,   # where WAVs are written (defaults to a temp dir)
)
```

Methods: `Voice.speak(text, path=None) -> Path` (write a file) and
`Voice.synthesize(text) -> (np.ndarray, int)` (raw audio in memory).

---

## What it returns

- `speak()` / `Voice.speak()` → **`pathlib.Path`** to a WAV file (24 kHz mono).
- `Voice.synthesize()` → **`(numpy.ndarray, int)`**: float32 samples and the
  sample rate, for callers that want the audio without touching disk.

---

## Behaviour notes

- **Low latency by design.** Kokoro runs on **CPU** through onnxruntime (no
  PyTorch), synthesizing several times faster than real time. This deliberately
  keeps the GPU free for [`sense_ear`](../../senses/sense_ear/README.md) and
  [`mind`](../../mind/README.md).
- **Model loads once.** The first call (or `Voice.engine` access) loads the
  model and, on first ever run, downloads the Kokoro files (~340 MB) to a cache
  directory. Subsequent calls are fast.
- **Default voice** is `ef_dora` (Spanish, female, youthful). Pass a different
  `voice`/`lang` to `Voice` for other voices or languages.
- **No secrets required.** Kokoro is fully local and free; there is no API key.

---

## Model files & cache

The Kokoro model (`kokoro-v1.0.onnx`) and voice pack (`voices-v1.0.bin`) are
downloaded once to `~/.cache/chris/voice/` (override with the
`CHRIS_VOICE_CACHE` environment variable) and reused thereafter. See
[models.md](models.md).

---

## Related pages

- [synthesizer.md](synthesizer.md) — the `Voice` class in full.
- [models.md](models.md) — how the model files are fetched and cached (internal).
- [mind/](../../mind/README.md) — produces the text that this effector speaks.
- [architecture.md](../../../architecture.md) — where this module fits and why.
