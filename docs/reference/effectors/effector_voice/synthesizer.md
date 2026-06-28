# `effectors.effector_voice.synthesizer`

Source: [`effectors/effector_voice/synthesizer.py`](../../../../effectors/effector_voice/synthesizer.py)

The engine behind the module: a thin wrapper around Kokoro (an 82M-parameter
ONNX TTS model), tuned for low latency. Text in → spoken-audio file out.

## class `Voice`

Turns text into spoken-audio files using Kokoro.

### Constructor

```python
Voice(
    voice: str = "ef_dora",
    lang: str = "es",
    speed: float = 1.0,
    output_dir: str | Path | None = None,
)
```

| Parameter | Default | Description |
| --- | --- | --- |
| `voice` | `"ef_dora"` | Kokoro voice id. `ef_dora` is the Spanish **female** voice; `em_alex` / `em_santa` are Spanish male voices. Many English and other-language voices also exist in the pack. |
| `lang` | `"es"` | Language used for phonemization. |
| `speed` | `1.0` | Speaking rate. `>1.0` is faster, `<1.0` slower. |
| `output_dir` | `None` | Directory for generated WAVs. Defaults to `<tempdir>/chris_voice`. |

> The constructor is cheap: the model is **not** loaded until first use (lazy).

### Properties

| Property | Type | Description |
| --- | --- | --- |
| `engine` | `kokoro_onnx.Kokoro` | The underlying Kokoro engine. Accessing it triggers the lazy model load (and a one-time download of the model files). |

### Methods

#### `synthesize(text: str) -> tuple[numpy.ndarray, int]`

Synthesize `text` and return `(samples, sample_rate)` in memory (float32 samples,
24000 Hz). Use this when you want the raw audio (e.g. to stream); most callers
want `speak`.

#### `speak(text: str, path: str | Path | None = None) -> Path`

Synthesize `text` to a WAV file and return its path.

- **`text`** — the text to speak (e.g. `mind`'s reply).
- **`path`** — optional destination. If omitted, a uniquely named file is written
  under `output_dir`.
- **Returns** — `pathlib.Path` to the written WAV (24 kHz, mono).

## Performance

Kokoro runs on **CPU** via onnxruntime. On this project's hardware it synthesizes
roughly **7× faster than real time** (a typical sentence is ready in ~0.3 s),
which is why TTS is kept off the GPU: the GPU stays free for speech-to-text and
the LLM, and latency is still low.

## Examples

```python
from voice import Voice

# A faster, slightly higher-pitched delivery
v = Voice(speed=1.1)
path = v.speak("¡Hola! ¿Cómo te va?")

# Raw audio instead of a file (e.g. to post-process or stream)
samples, sr = v.synthesize("Texto de prueba")
```

## Related pages

- [README.md](README.md) — the module's public API.
- [models.md](models.md) — model-file download/caching used by `engine`.
