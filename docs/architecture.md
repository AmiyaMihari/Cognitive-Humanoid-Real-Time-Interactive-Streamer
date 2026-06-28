# Architecture & design decisions

This page explains *how* the project is put together and *why* the key choices
were made. For exact APIs, see [reference/](reference/).

## High-level picture

```
                  ┌────────────────────────────┐
 microphone /     │            app.py          │   Streamlit UI:
 typed text   ──► │  (Streamlit chat frontend) │   text box + mic button
                  └──┬──────────────▲───────┬──┘
                     │ audio bytes  │ reply │ reply text → speak()
                     ▼              │ text  ▼
     ┌───────────────────────────┐  │  ┌─────────────────────────────┐
     │  senses.sense_ear         │  │  │  effectors.effector_voice   │
     │  transcribe(audio) → str  │  │  │  speak(text) → audio file   │
     └────────────┬──────────────┘  │  └─────────────────────────────┘
                  │ recognised text │       "speaking" effector
                  ▼                 │
     ┌───────────────────────────┐  │
     │  mind                     │ ─┘       "thinking" faculty
     │  think(text) → str        │
     └───────────────────────────┘
```

The pipeline is **audio → text → reply → speech**: `sense_ear` hears
(audio → text), `mind` thinks (text → reply), `effector_voice` speaks (reply →
audio file), and `app.py` only wires them together and to the UI. Each module is
expanded independently below.

### Inside `sense_ear`

```
   ┌─────────────────────┐                 ┌────────────────────────┐
   │  transcriber.py     │                 │   _cuda.py             │
   │  faster-whisper /   │  uses           │   preloads CUDA 12     │
   │  CTranslate2 on GPU │ ◄────────────── │   libs for Blackwell   │
   └─────────────────────┘                 └────────────────────────┘
```

### Inside `mind`

```
   ┌──────────────────────────────────────┐
   │  agent.py: Mind                       │
   │  minimal LangGraph graph (START →     │  uses
   │  respond) over a ChatOpenAI model     │ ◄──── OPENAI_API_KEY (.env)
   └──────────────────────────────────────┘
```

### Inside `effector_voice`

```
   ┌─────────────────────────┐         ┌────────────────────────┐
   │  synthesizer.py: Voice  │  uses   │  _models.py            │
   │  Qwen3-TTS VoiceDesign  │ ◄────── │  model defaults &      │
   │  via qwen_tts/PyTorch   │         │  cache configuration   │
   └─────────────────────────┘         └────────────────────────┘
```

The golden rule: **each module hides its implementation behind a tiny
contract.** `sense_ear` exposes only `audio in → text out`; `mind` exposes only
`text in → reply out`; `effector_voice` exposes only `text in → audio file out`.
You can swap the UI, or call any module from a script, without touching the
engine code.

## Project layout

```
C.H.R.I.S./
├── app.py                  # Streamlit demo (UI only; no engine code here)
├── senses/                 # perception modules, one sub-package per sense
│   ├── __init__.py
│   └── sense_ear/          # hearing: speech-to-text
│       ├── __init__.py     # public API: transcribe(), get_transcriber(), Transcriber
│       ├── transcriber.py  # the engine (faster-whisper wrapper)
│       └── _cuda.py        # internal: CUDA 12 library preloading
├── effectors/              # action modules, one sub-package per effector
│   ├── __init__.py
│   └── effector_voice/     # speaking: text-to-speech
│       ├── __init__.py     # public API: speak(), get_voice(), Voice
│       ├── synthesizer.py  # the engine (Qwen3-TTS VoiceDesign wrapper)
│       └── _models.py      # internal: Qwen3-TTS defaults & cache config
├── mind/                   # thinking: text-to-reply
│   ├── __init__.py         # public API: think(), get_mind(), Mind
│   └── agent.py            # the engine (LangGraph graph over ChatOpenAI)
├── requirements.txt        # pinned, tested dependency versions
├── .env.example            # template for the HF_TOKEN and OPENAI_API_KEY secrets
├── txt_interviews.ipynb    # original notebook sense_ear was derived from
└── docs/                   # you are here
```

## Key design decisions

### The module is isolated

`sense_ear` exposes a tiny contract (`transcribe(audio) -> str`) and hides
faster-whisper, CTranslate2, CUDA handling and model lifecycle behind it.
`mind` does the same with `think(text) -> str`, hiding the LLM client and graph.
`effector_voice` does the same with `speak(text) -> Path`, hiding the Qwen3-TTS
model and voice-design instruction.
Benefits: the UI stays trivial, each engine is unit-testable in isolation, and
new modules (future senses under `senses/`, richer thinking in `mind/`) slot in
without changing callers.

### The mind module (thinking)

`mind` is the counterpart to the senses: where a sense turns the world into
text, `mind` turns text into a response. Its contract is deliberately identical
in spirit — `think(text) -> str` — so `app.py` can pipe `sense_ear`'s output
straight into it.

Under the hood it is a **minimal LangGraph graph** (`START → respond`) over a
`ChatOpenAI` model. A single OpenAI call would be shorter, but LangGraph was
chosen on purpose: it gives the "thinking" layer a clear place to grow —
conversation memory, tool use, multi-step reasoning — each added as graph nodes
**behind the same `think(text) -> str` surface**, so callers never change. Today
the graph is intentionally one node: the simplest thing that works.

The default model is `gpt-4o-mini` (cheap and fast); construct `Mind(model=...)`
for a different one.

### The voice effector (speaking)

`effector_voice` is the spoken counterpart of `mind`: it turns the reply text into sound,
so the chat always *speaks* as well as writes. Its contract mirrors the others —
`speak(text) -> Path` (a WAV file).

The engine is **Qwen3-TTS VoiceDesign**, selected because the voice can be
described directly in natural language while keeping the same module boundary:
the rest of the app still sends text and receives a WAV path.

- **Custom voice by instruction.** The default voice prompt is intentionally
  short and acoustic: cute soft anime femboy timbre, native Latin American
  Spanish pronunciation, medium pace, controlled volume, calm conversational
  delivery, and dry tsundere wit without shouting.
- **Stable Spanish pronunciation.** The module sends `language="Spanish"` by
  default to avoid accidental English-like pronunciation in mixed Spanish text.
  Set `CHRIS_VOICE_LANGUAGE=Auto` to restore automatic language detection.
- **Local inference.** The model runs through the `qwen-tts` package and caches
  weights locally through Hugging Face. It prefers CUDA when available, with CPU
  as a functional fallback.

#### Qwen3-TTS operational notes

The current app streams **text** from `mind`, but it synthesizes **one full WAV**
per assistant answer. Earlier phrase-by-phrase synthesis reduced perceived
latency, but Qwen3-TTS VoiceDesign reinterpreted the voice instruction on each
chunk, causing different voices across paragraphs and overlapping autoplay in
Streamlit. A single synthesis call keeps the voice coherent for the full reply.

Qwen3-TTS loads lazily by default: opening Streamlit does not immediately put the
1.7B TTS model in VRAM. This avoids CUDA out-of-memory errors when Whisper and
Qwen are accidentally loaded by multiple Streamlit/Python processes. Set
`CHRIS_VOICE_WARMUP=1` to load Qwen3-TTS at app startup instead, trading higher
startup VRAM for a faster first spoken reply.

The local PyTorch cu130/Blackwell stack hit a
`CUDNN_STATUS_SUBLIBRARY_VERSION_MISMATCH` during Qwen3-TTS audio decoding, so
the voice module disables cuDNN for Qwen by default
(`CHRIS_VOICE_DISABLE_CUDNN=1`). CUDA is still used; only cuDNN-backed kernels
are avoided for this module. The generated audio length is capped by
`CHRIS_VOICE_MAX_NEW_TOKENS` (`2048` by default): raise it for very long spoken
answers, or lower it if VRAM becomes tight.

### Tuned for short, real-time audio

The original notebook (`txt_interviews.ipynb`) processed long interview files.
This module instead targets **short, live utterances**: lighter VAD silence
thresholds and `condition_on_previous_text=False` so each clip is transcribed
independently, avoiding cross-clip hallucinations and repetition loops. The
model itself is unchanged: Spanish `large-v3`.

### GPU first, with a transparent CPU fallback

Default is `cuda` + `float16`. If CUDA initialization fails, the `Transcriber`
silently falls back to CPU (`int8`) so the app still works. The actual device in
use is exposed via `Transcriber.device`.

### The Blackwell / CUDA 12 quirk

The GPU is an **RTX 5070 Ti (Blackwell, sm_120)**. CTranslate2 4.8 is compiled
against **CUDA 12** and `dlopen`s `libcublas.so.12` / `libcudnn.so.9` at GPU
time. The system, however, ships **CUDA 13**, so those exact sonames are not on
the loader path and GPU calls fail.

The fix lives entirely inside the module: the `nvidia-cublas-cu12` /
`nvidia-cudnn-cu12` wheels (versions 12.9 / 9.23, which include Blackwell
kernels) provide the libraries, and [`_cuda.py`](reference/senses/sense_ear/cuda.md)
preloads them into the process with `RTLD_GLOBAL` before CTranslate2 needs them.
No `LD_LIBRARY_PATH` editing required — the module is self-contained.

### Why Python 3.12 via uv

The system Python is 3.14, which is too new for parts of the ML ecosystem
(notably PyTorch/pyannote, needed if speaker diarization is added later). The ML
community consensus is **Python 3.11–3.12**. We standardized on **3.12**,
installed with **`uv`** because it needs no `sudo` and produces a self-contained
interpreter and venv.

### Secrets via .env

Both modules read secrets from a git-ignored `.env` file through
`python-dotenv`, loaded automatically on import. Real environment variables
always win over `.env` values.

- `OPENAI_API_KEY` (used by `mind`) is **required** — the LLM client cannot
  authenticate without it.
- `HF_TOKEN` (used by `sense_ear`) is **optional** — the `large-v3` weights are
  public; a token only lifts anonymous download rate limits or unlocks gated
  models.

## Dependency overview

| Dependency | Role |
| --- | --- |
| `faster-whisper` + `ctranslate2` | Whisper inference engine (no PyTorch needed) |
| `nvidia-cublas-cu12`, `nvidia-cudnn-cu12` | CUDA 12 libs with Blackwell support |
| `langgraph` + `langchain-openai` | The `mind` thinking engine: a graph over an OpenAI chat model |
| `qwen-tts` + `soundfile` | The `effector_voice` engine: Qwen3-TTS VoiceDesign inference and WAV writing |
| `python-dotenv` | Loads the `OPENAI_API_KEY` / `HF_TOKEN` secrets from `.env` |
| `streamlit`, `streamlit-mic-recorder` | Demo UI and in-browser microphone capture |
