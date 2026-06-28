# `senses.sense_ear` — speech-to-text

Source: [`senses/sense_ear/__init__.py`](../../../../senses/sense_ear/__init__.py)

The **hearing** sense. Its entire contract is:

> **audio in → text out.**

It wraps faster-whisper (Spanish `large-v3` on the GPU) behind a tiny API and
hides all model, CUDA and lifecycle handling.

---

## Quick start

```python
from senses.sense_ear import transcribe

text = transcribe(audio)   # -> str
```

That single call:

1. Lazily builds a shared `Transcriber` the first time it runs (loads the model
   on the GPU; this is the slow part and happens **once** per process).
2. Transcribes the clip.
3. Returns the recognised text as a plain `str`.

---

## Public API

The module exports exactly four names (`__all__`):

| Name | Kind | Summary |
| --- | --- | --- |
| [`transcribe(audio)`](#transcribeaudio---str) | function | One-shot convenience: audio → text using a shared transcriber. |
| [`get_transcriber()`](#get_transcriber---transcriber) | function | Returns the process-wide shared `Transcriber`. |
| [`Transcriber`](#class-transcriber) | class | Configurable engine; use when you need non-default options. |
| `AudioInput` | type alias | The set of accepted audio input types (see below). |

### `transcribe(audio) -> str`

Transcribe a single short audio clip using the shared default transcriber.

- **Parameter** — `audio`: the clip to transcribe (see
  [Accepted audio inputs](#accepted-audio-inputs)).
- **Returns** — `str`: the recognised text, whitespace-trimmed. Returns an
  **empty string `""`** when no speech is detected (silence/noise). Never returns
  `None`.

```python
from senses.sense_ear import transcribe

print(transcribe("hello.wav"))      # from a file path
print(transcribe(wav_bytes))        # from raw WAV bytes (e.g. a browser mic)
```

### `get_transcriber() -> Transcriber`

Return the **shared, process-wide** `Transcriber` (created on first call, reused
after). Use this when you want the convenience of the singleton but also need
the object — for example to inspect which device is active:

```python
from senses.sense_ear import get_transcriber

tr = get_transcriber()
print(tr.device)            # 'cuda' or 'cpu'
text = tr.transcribe(audio)
```

### class `Transcriber`

The configurable engine. Construct your own instance when you need
non-default settings (a different model, forced CPU, another language, etc.).
Full details in [transcriber.md](transcriber.md). Constructor summary:

```python
Transcriber(
    model_size="large-v3",   # Whisper model name
    device="cuda",           # "cuda" or "cpu"
    compute_type="float16",  # e.g. "float16", "int8"
    language="es",           # ISO language code
    beam_size=5,             # decoding beam width
    cpu_fallback=True,       # auto-fall back to CPU if CUDA fails
)
```

Main method — `Transcriber.transcribe(audio) -> str` — same input/return
contract as the module-level `transcribe()`.

---

## Accepted audio inputs

`transcribe()` accepts any of these (`AudioInput`):

| Input type | Example | Notes |
| --- | --- | --- |
| `str` path | `"clip.wav"` | Any format ffmpeg can decode (WAV, MP3, …). |
| `bytes` / `bytearray` | WAV blob from a mic | Decoded in-memory; what the Streamlit app sends. |
| file-like (`BinaryIO`) | `open("clip.wav", "rb")` | Any readable binary stream. |
| numpy array | `np.ndarray`, float32 | Mono PCM samples at **16 kHz**. |

Internally, `bytes`/`bytearray` are wrapped in a `BytesIO`; everything else is
passed straight to faster-whisper.

---

## What it returns

- Type: **`str`** — always.
- Content: the transcribed speech, trimmed of surrounding whitespace; multiple
  internal segments are joined with single spaces.
- Empty input / silence → **`""`** (empty string), not an error and not `None`.

---

## Behaviour notes

- **Tuned for short, real-time clips.** Each call is transcribed independently
  (`condition_on_previous_text=False`) with light VAD silence trimming. This
  differs from the long-audio notebook it was derived from.
- **Model loads once.** The first call (or `Transcriber.model` access) loads the
  model; it stays resident for the process lifetime. Subsequent calls are fast.
- **GPU by default, CPU fallback.** Runs on `cuda`/`float16`; if CUDA fails to
  initialize and `cpu_fallback=True`, it switches to `cpu`/`int8`. Check the
  result with `Transcriber.device`.
- **Spanish by default** (`language="es"`). Construct a `Transcriber` with a
  different `language` for other languages.

---

## Secrets handling

On import, the module loads a git-ignored `.env` (via `python-dotenv`) so an
optional `HF_TOKEN` is picked up automatically. Existing environment variables
take precedence over `.env` values.

`HF_TOKEN` is **not required** — the `large-v3` weights are public. Provide one
only to lift anonymous download rate limits or to use a gated model. See
[getting-started.md](../../../getting-started.md#3-optional-configure-a-hugging-face-token).

---

## Related pages

- [transcriber.md](transcriber.md) — the `Transcriber` class in full.
- [cuda.md](cuda.md) — how the CUDA 12 libraries are made loadable on Blackwell.
- [architecture.md](../../../architecture.md) — where this module fits and why.
