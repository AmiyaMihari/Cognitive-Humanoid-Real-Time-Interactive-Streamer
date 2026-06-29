# `effectors.effector_voice.synthesizer`

Source: [`effectors/effector_voice/synthesizer.py`](../../../../effectors/effector_voice/synthesizer.py)

The engine behind the module: a thin wrapper around Qwen3-TTS. Text in ->
spoken-audio file out. At runtime it **clones** a baked reference clip with the
Base model (design-once -> clone); it never re-designs the voice per call.

## class `Voice`

Turns text into spoken-audio files by cloning a baked voice identity.

### Constructor

```python
Voice(
    lang: str = "Spanish",
    emotion: str = "neutral",
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
| `lang` | `"Spanish"` | Language sent to Qwen3-TTS. `Spanish` keeps the accent stable; set `CHRIS_VOICE_LANGUAGE=Auto` to restore automatic detection. |
| `emotion` | `"neutral"` | Default emotion to clone. One of `neutral`, `happy`, `sad`, `angry`, `fear`, `shame`. Unbaked emotions fall back to `neutral`. |
| `speed` | `1.0` | Optional post-generation time stretch. `>1.0` faster, `<1.0` slower (needs `librosa`). |
| `output_dir` | `None` | Directory for generated WAVs. Defaults to `<tempdir>/chris_voice`. |
| `model` | `None` | Runtime (clone/Base) model id or local path. Defaults to `CHRIS_VOICE_MODEL` or `Qwen/Qwen3-TTS-12Hz-1.7B-Base`. |
| `device` | `None` | Device map. Defaults to `CHRIS_VOICE_DEVICE`, then `cuda:0` if available, otherwise `cpu`. |
| `dtype` | `None` | `auto`, `bfloat16`, `float16` or `float32`. Defaults to `CHRIS_VOICE_DTYPE` or `auto` (bf16 on CUDA). |
| `attn_implementation` | `None` | Attention implementation. Defaults to `CHRIS_VOICE_ATTN`, then `flash_attention_2` with a safe fallback. |

`CHRIS_VOICE_MAX_NEW_TOKENS` defaults to `2048`. Lower values generate faster but
can cut long answers; higher values may need more VRAM.

> The constructor is cheap: the model is **not** loaded until first use (lazy).

#### flash-attention 2 fallback

The loader requests `attn_implementation="flash_attention_2"` by default. If
`flash-attn` is not installed or fails to load (it is delicate on Blackwell), the
build emits a `RuntimeWarning` and retries with the default attention
implementation instead of crashing.

#### cuDNN

cuDNN is **enabled by default**. Set `CHRIS_VOICE_DISABLE_CUDNN=1` to disable it.
On the local PyTorch/Blackwell stack, Qwen3-TTS audio decoding otherwise fails
with `CUDNN_STATUS_SUBLIBRARY_VERSION_MISMATCH`, so this box must run with cuDNN
disabled. CUDA itself is still used; only cuDNN-backed kernels are avoided.

### Properties

| Property | Type | Description |
| --- | --- | --- |
| `engine` | `qwen_tts.Qwen3TTSModel` | The underlying Qwen3-TTS engine. Accessing it triggers model load and first-use download. |

### Methods

#### `warmup() -> None`

Build the engine, construct a clone prompt for **every baked emotion**, and run
one short dummy synthesis to compile CUDA kernels. Doing this at boot makes the
first real sentence fast. Idempotent. Raises a clear error if `neutral` is not
baked.

#### `synthesize(text: str, emotion: str | None = None) -> tuple[numpy.ndarray, int]`

Clone `text` and return `(samples, sample_rate)` in memory. `emotion` falls back
to `neutral` (warning once) when not baked. Use this for raw audio; most callers
want `speak`.

#### `speak(text: str, emotion: str | None = None, path: str | Path | None = None) -> Path`

Clone `text` to a WAV file and return its path.

- **`text`** - the text to speak.
- **`emotion`** - optional emotion; defaults to the instance's `emotion`.
- **`path`** - optional destination. If omitted, a uniquely named file is written
  under `output_dir`.
- **Returns** - `pathlib.Path` to the written WAV.

#### `synthesize_stream(text, emotion=None, prefetch=1) -> Iterator[tuple[np.ndarray, int]]`

Yield `(samples, sample_rate)` per sentence, in order, while the next sentence is
synthesized one step ahead in a worker thread. See [streaming.md](streaming.md).

#### `speak_stream(text, emotion=None, prefetch=1) -> Iterator[Path]`

Like `synthesize_stream`, but writes each sentence to a WAV and yields its
`Path`.

#### `clear_cuda_cache() -> None`

Release temporary PyTorch CUDA allocations after synthesis. Does not unload the
weights.

#### `unload() -> None`

Drop the Qwen3-TTS engine and cached clone prompts from memory and clear the CUDA
cache. `app.py` uses this before microphone transcription so Whisper and
Qwen3-TTS are not held in VRAM at the same time.

### Internal / maintainers only

- `_load_identity()` reads the [manifest](baking-the-voice.md#the-manifest) and
  builds one `create_voice_clone_prompt(...)` per baked emotion, caching them in
  `self._prompts`. It fails loud and early if `neutral` is missing, pointing at
  the bake script.
- `_resolve_prompt(emotion)` returns the cached prompt, falling back to `neutral`
  with a one-time warning.
- `_build_engine(...)` implements the flash-attn fallback described above.
- `_env_flag(name, default)` parses boolean environment variables.

## Examples

```python
from effectors.effector_voice import Voice

v = Voice()
v.warmup()                          # optional: prime kernels at boot
path = v.speak("¡Hola! ¿Cómo te va?")

# Raw audio instead of a file
samples, sr = v.synthesize("Texto de prueba")

# A different default emotion (falls back to neutral until baked)
sad = Voice(emotion="sad")
sad.speak("No tengo ganas de nada hoy...")
```

## Related pages

- [README.md](README.md) - the module's public API.
- [baking-the-voice.md](baking-the-voice.md) - how the reference clips are made.
- [streaming.md](streaming.md) - the sentence-streaming helpers.
- [models.md](models.md) - model/cache/identity configuration used by `engine`.
