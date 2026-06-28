# `effectors.effector_voice.synthesizer`

Source: [`effectors/effector_voice/synthesizer.py`](../../../../effectors/effector_voice/synthesizer.py)

The engine behind the module: a thin wrapper around Qwen3-TTS VoiceDesign. Text
in -> spoken-audio file out.

## class `Voice`

Turns text into spoken-audio files using Qwen3-TTS.

### Constructor

```python
Voice(
    voice: str = DEFAULT_VOICE_DESCRIPTION,
    lang: str = "Auto",
    speed: float = 1.0,
    output_dir: str | Path | None = None,
    model: str | None = None,
    device: str | None = None,
    dtype: str | None = None,
    attn_implementation: str | None = None,
)
```

| Parameter | Default | Description |
| --- | --- | --- |
| `voice` | project voice description | Natural-language voice/style instruction sent to `generate_voice_design`. |
| `lang` | `"Auto"` | Language sent to Qwen3-TTS. `Auto` lets the model adapt to the input text. |
| `speed` | `1.0` | Optional post-generation time stretch. `>1.0` is faster, `<1.0` slower. |
| `output_dir` | `None` | Directory for generated WAVs. Defaults to `<tempdir>/chris_voice`. |
| `model` | `None` | Hugging Face model id or local path. Defaults to `CHRIS_VOICE_MODEL` or `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`. |
| `device` | `None` | Device map. Defaults to `CHRIS_VOICE_DEVICE`, then `cuda:0` if CUDA is available, otherwise `cpu`. |
| `dtype` | `None` | `auto`, `bfloat16`, `float16` or `float32`. Defaults to `CHRIS_VOICE_DTYPE` or `auto`. |
| `attn_implementation` | `None` | Optional Transformers attention implementation. |

By default the loader sets `torch.backends.cudnn.enabled = False` for the
Qwen3-TTS process path. On the local PyTorch cu130/Blackwell stack, Qwen3-TTS
audio decoding otherwise fails with `CUDNN_STATUS_SUBLIBRARY_VERSION_MISMATCH`.
Set `CHRIS_VOICE_DISABLE_CUDNN=0` to try cuDNN again after upgrading PyTorch or
the CUDA/cuDNN wheels.

> The constructor is cheap: the model is **not** loaded until first use (lazy).

### Properties

| Property | Type | Description |
| --- | --- | --- |
| `engine` | `qwen_tts.Qwen3TTSModel` | The underlying Qwen3-TTS engine. Accessing it triggers model load and first-use download. |

### Methods

#### `synthesize(text: str) -> tuple[numpy.ndarray, int]`

Synthesize `text` and return `(samples, sample_rate)` in memory. Use this when
you want the raw audio (for example to stream); most callers want `speak`.

#### `speak(text: str, path: str | Path | None = None) -> Path`

Synthesize `text` to a WAV file and return its path.

- **`text`** - the text to speak (for example, `mind`'s reply).
- **`path`** - optional destination. If omitted, a uniquely named file is written
  under `output_dir`.
- **Returns** - `pathlib.Path` to the written WAV.

## Examples

```python
from effectors.effector_voice import Voice

v = Voice()
path = v.speak("¡Hola! ¿Cómo te va?")

# Raw audio instead of a file
samples, sr = v.synthesize("Texto de prueba")

# A different voice-design instruction
dramatic = Voice(voice="Speak softly, nervously, and very close to tears.")
dramatic.speak("No puede ser...")
```

## Related pages

- [README.md](README.md) - the module's public API.
- [models.md](models.md) - model/cache configuration used by `engine`.
