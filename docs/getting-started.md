# Getting started

This guide takes you from a fresh checkout to a running speech-to-text demo.

## Prerequisites

- **Linux** with an **NVIDIA GPU** (developed on an RTX 5070 Ti / Blackwell).
  CPU-only also works — the module falls back automatically — just slower.
- **NVIDIA driver** installed (`nvidia-smi` should work). You do **not** need a
  matching CUDA toolkit: the required CUDA 12 libraries are installed as Python
  wheels and loaded by the module itself.
- **`ffmpeg`** on the `PATH` (used to decode audio).
- **Python 3.12**, managed with [`uv`](https://docs.astral.sh/uv/). See
  [architecture.md](architecture.md#why-python-312-via-uv) for why.

## 1. Install Python 3.12 and the virtual environment

```fish
# Install uv (no sudo; lands in ~/.local/bin)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the interpreter and create the venv
uv python install 3.12
uv venv --python 3.12 venv
```

The fish shell auto-activates this `venv` whenever you `cd` into the project
(via `~/.config/fish/conf.d/auto_venv.fish`), and deactivates it when you leave.

## 2. Install dependencies

```fish
source venv/bin/activate        # automatic in fish; explicit here for clarity
uv pip install -r requirements.txt
```

## 3. (Optional) Configure a Hugging Face token

The default Spanish `large-v3` weights are **public**, so this is **not
required**. Set a token only to avoid anonymous download rate limits, or if you
later switch to a gated model (e.g. pyannote diarization):

```fish
cp .env.example .env
# then edit .env and set HF_TOKEN=hf_xxx
```

The module loads `.env` automatically. `.env` is git-ignored, so the token never
reaches the repository. See
[reference/senses/sense_ear/](reference/senses/sense_ear/README.md#secrets-handling).

## 4. Run the demo app

```fish
streamlit run app.py
```

Open the URL it prints. You can **type** a message, or tap **🔴 Start
recording**, speak a short phrase, and **⏹️ Stop** — the recognised text appears
in the chat. The first run downloads the `large-v3` model (~3 GB) and caches it;
later runs start in seconds.

## 5. Use the module from your own code

```python
from senses.sense_ear import transcribe

text = transcribe(audio_bytes)   # audio in -> text out
print(text)
```

Full API (inputs, return value, options) is in
[reference/senses/sense_ear/](reference/senses/sense_ear/README.md).

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `Library libcublas.so.12 is not found` | Ensure `nvidia-cublas-cu12` / `nvidia-cudnn-cu12` are installed (they are in `requirements.txt`). The module preloads them; no `LD_LIBRARY_PATH` needed. |
| First transcription is very slow | The `large-v3` model is downloading/loading. Subsequent calls reuse the cached, in-memory model. |
| Runs on CPU instead of GPU | Check `nvidia-smi`. The module falls back to CPU if CUDA initialization fails; see `Transcriber.device`. |
| Empty string returned | No speech was detected in the clip (silence/noise). That is the expected result. |
