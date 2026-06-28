# `senses.sense_ear.transcriber`

Source: [`senses/sense_ear/transcriber.py`](../../../../senses/sense_ear/transcriber.py)

The engine behind the module: a thin, opinionated wrapper around
faster-whisper's `WhisperModel`, tuned for short real-time utterances.

## `AudioInput`

```python
AudioInput = Union[str, bytes, bytearray, BinaryIO, object]
```

Type alias for everything `transcribe()` accepts. See
[Accepted audio inputs](README.md#accepted-audio-inputs).

## class `Transcriber`

Loads a Whisper model once and turns audio into text.

### Constructor

```python
Transcriber(
    model_size: str = "large-v3",
    device: str = "cuda",
    compute_type: str = "float16",
    language: str = "es",
    beam_size: int = 5,
    cpu_fallback: bool = True,
)
```

| Parameter | Default | Description |
| --- | --- | --- |
| `model_size` | `"large-v3"` | faster-whisper model name. Smaller models (`"tiny"`, `"base"`, …) trade accuracy for speed. |
| `device` | `"cuda"` | `"cuda"` for GPU, `"cpu"` for CPU. |
| `compute_type` | `"float16"` | Numeric precision (e.g. `"float16"` on GPU, `"int8"` on CPU). |
| `language` | `"es"` | ISO 639-1 language code forced during decoding. |
| `beam_size` | `5` | Beam search width. Lower → faster, slightly less accurate. |
| `cpu_fallback` | `True` | If `True`, fall back to CPU/`int8` when CUDA initialization fails. |

> The constructor is cheap: the model is **not** loaded until first use (lazy).

### Properties

| Property | Type | Description |
| --- | --- | --- |
| `model` | `WhisperModel` | The underlying model. Accessing it triggers the lazy load (and any CPU fallback). |
| `device` | `str` | The device actually in use (`"cuda"` or `"cpu"`) **after** any fallback. |

### Methods

#### `transcribe(audio: AudioInput) -> str`

Transcribe one short utterance and return the recognised text.

- **`audio`** — a path, encoded bytes, a binary file-like object, or a 16 kHz
  float32 numpy array.
- **Returns** — `str`, whitespace-trimmed; `""` when no speech is detected.

Decoding is configured for short, independent clips:

| Setting | Value | Why |
| --- | --- | --- |
| `task` | `"transcribe"` | Transcribe, never translate. |
| `vad_filter` | `True` | Trim leading/trailing silence from the clip. |
| `vad_parameters` | `min_silence_duration_ms=300` | Light silence threshold suited to short audio. |
| `condition_on_previous_text` | `False` | Each clip is independent → avoids cross-clip hallucinations/repetition. |

## Internal members (maintainers only)

These are implementation details and may change without notice:

- `_load_model()` — builds the `WhisperModel`, preloads CUDA libs (see
  [cuda.md](cuda.md)), passes `HF_TOKEN` if set, and performs the CPU fallback.
- `_coerce_audio(audio)` — normalizes inputs (wraps `bytes` in `BytesIO`;
  passes paths, file-likes and numpy arrays through unchanged).

## Examples

```python
from senses.sense_ear import Transcriber

# Force CPU (no GPU available)
tr = Transcriber(device="cpu", compute_type="int8")

# Faster, lower-accuracy English transcription
tr = Transcriber(model_size="base", language="en", beam_size=1)

text = tr.transcribe("clip.wav")
print(tr.device, "->", text)
```
