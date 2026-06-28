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

## 3. Configure your API keys

Secrets live in a git-ignored `.env` file. Create it from the template:

```fish
cp .env.example .env
```

Then edit `.env`:

| Key | Required? | Used by | Notes |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | **Yes** | `mind` | The thinking module sends text to an OpenAI model; without it, replies fail. Get one at <https://platform.openai.com/api-keys>. |
| `HF_TOKEN` | No | `sense_ear` | The Spanish `large-v3` weights are public. Set a token only to avoid anonymous download rate limits, or for a gated model. |

```ini
OPENAI_API_KEY=sk-...
HF_TOKEN=          # leave empty unless you need it
```

Both modules load `.env` automatically on import. `.env` is git-ignored, so the
keys never reach the repository. See
[reference/mind/](reference/mind/README.md#secrets-handling) and
[reference/senses/sense_ear/](reference/senses/sense_ear/README.md#secrets-handling).

## 4. Run the demo app

```fish
streamlit run app.py
```

Open the URL it prints. The screen is a minimal chat: a text box with a
**🎙️ microphone** icon on its right. **Type** a message, or tap the mic, speak a
short phrase, and tap **⏹️** to stop. Your words appear in the chat (transcribed
by `sense_ear` when spoken), then `mind` replies. The full path is
**audio → text → reply**. The first run downloads the `large-v3` model (~3 GB)
and caches it; later runs start in seconds.

## 5. Use the modules from your own code

The two engines are independent and each has a one-line contract:

```python
from senses.sense_ear import transcribe   # audio in -> text out
from mind import think                     # text in  -> reply out

text  = transcribe(audio_bytes)
reply = think(text)
print(reply)
```

Full APIs (inputs, return values, options) are in
[reference/senses/sense_ear/](reference/senses/sense_ear/README.md) and
[reference/mind/](reference/mind/README.md).

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `Library libcublas.so.12 is not found` | Ensure `nvidia-cublas-cu12` / `nvidia-cudnn-cu12` are installed (they are in `requirements.txt`). The module preloads them; no `LD_LIBRARY_PATH` needed. |
| First transcription is very slow | The `large-v3` model is downloading/loading. Subsequent calls reuse the cached, in-memory model. |
| Runs on CPU instead of GPU | Check `nvidia-smi`. The module falls back to CPU if CUDA initialization fails; see `Transcriber.device`. |
| Empty string returned | No speech was detected in the clip (silence/noise). That is the expected result. |
| Reply errors / auth failure from `mind` | `OPENAI_API_KEY` is missing or invalid. Check your `.env` (step 3) and that the key is active. |
