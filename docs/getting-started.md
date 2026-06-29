# Getting started

This guide takes you from a fresh checkout to a running speech-to-text demo.

## Prerequisites

- **Linux, macOS or Windows**, with **Git** installed.
- An **NVIDIA GPU** is optional but recommended (developed on an RTX 5070 Ti /
  Blackwell). CPU-only also works — `sense_ear` falls back automatically — just
  slower. You do **not** need a matching CUDA toolkit: the required CUDA 12
  libraries are installed as Python wheels and loaded by the module itself.
- **SoX** is optional but recommended for the Qwen3-TTS audio stack. `setup.sh`
  and `setup.ps1` try to install it automatically when possible.

> You do **not** need to install Python yourself. The setup below installs the
> exact version (3.12) in isolation via [`uv`](https://docs.astral.sh/uv/), and
> PyAV bundles the audio decoders, so no system `ffmpeg` is required. See
> [architecture.md](architecture.md#why-python-312-via-uv) for the rationale.

## Quick setup (recommended)

One script installs everything — `uv`, SoX when possible, Python 3.12, the
virtualenv and all dependencies — and creates your `.env`:

```bash
# Linux / macOS
chmod +x setup.sh
./setup.sh
```

```powershell
# Windows (PowerShell)
./setup.ps1
```

Then jump to [step 3](#3-configure-your-api-keys) to add your API key. The rest
of this page (steps 1–2) is the **manual alternative** if you'd rather run the
commands yourself.

## 1. Install Python 3.12 and the virtual environment

```bash
# Install uv (no sudo; lands in ~/.local/bin)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the interpreter and create the venv
uv python install 3.12
uv venv --python 3.12 venv
```

On Linux, `setup.sh` also installs a hook (for **bash** via `~/.bashrc`, and for
**fish** via `conf.d`) that auto-activates this `venv` whenever you `cd` into the
project, and deactivates it when you leave.

## 2. Install dependencies

```bash
source venv/bin/activate        # automatic via the auto-venv hook; explicit here for clarity
uv pip install -r requirements.txt
```

## 3. Configure your API keys

Secrets live in a git-ignored `.env` file. Create it from the template:

```bash
cp .env.example .env
```

Then edit `.env`:

| Key | Required? | Used by | Notes |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | **Yes** | `mind` | The thinking module sends text to an OpenAI model; without it, replies fail. Get one at <https://platform.openai.com/api-keys>. |
| `HF_TOKEN` | No | `sense_ear` | The Spanish `large-v3` weights are public. Set a token only to avoid anonymous download rate limits, or for a gated model. |
| `CHRIS_VOICE_LANGUAGE` | No | `effector_voice` | Defaults to `Spanish` to keep Qwen3-TTS pronunciation stable. |
| `CHRIS_VOICE_DISABLE_CUDNN` | **On Blackwell** | `effector_voice` | Defaults to `0` (cuDNN ON). **Set `1`** on this Blackwell box, or TTS decoding crashes with `CUDNN_STATUS_SUBLIBRARY_VERSION_MISMATCH`. |
| `CHRIS_VOICE_MODEL` | No | `effector_voice` | Runtime clone model. Set `Qwen/Qwen3-TTS-12Hz-0.6B-Base` for a noticeably faster voice. |
| `CHRIS_VOICE_WARMUP` | No | `app.py` | `0` keeps startup VRAM low; `1` warms up Qwen3-TTS at app startup so the first audio is faster. |
| `CHRIS_VOICE_MAX_NEW_TOKENS` | No | `effector_voice` | Defaults to `2048`; raise it if very long replies are cut. |

```ini
OPENAI_API_KEY=sk-...
HF_TOKEN=          # leave empty unless you need it
```

Both modules load `.env` automatically on import. `.env` is git-ignored, so the
keys never reach the repository. See
[reference/mind/](reference/mind/README.md#secrets-handling) and
[reference/senses/sense_ear/](reference/senses/sense_ear/README.md#secrets-handling).

## 4. Bake Chris's voice (first run only)

The voice is **cloned** from a fixed reference clip, so you must bake that clip
once before the app can speak. Until you do, `speak()` fails with a clear error
pointing here.

```bash
# 1. Generate voice candidates to audition.
python scripts/bake_voice.py --emotion neutral --n 6

# 2. Listen to identity/neutral/candidates/cand_*.wav, then promote your favourite.
python scripts/bake_voice.py --emotion neutral --choose cand_03
```

The first command downloads the VoiceDesign weights (~4.3 GB) and writes six
candidates; the second promotes one to the official reference clip and records it
in `manifest.json`. Full details, plus how to add the `happy`/`sad`/`angry`/
`fear`/`shame` emotions later, are in
[baking-the-voice.md](reference/effectors/effector_voice/baking-the-voice.md).

## 5. Run the demo app

```bash
streamlit run app.py
```

Open the URL it prints. The screen is a minimal chat: a text box with a
**🎙️ microphone** icon on its right. **Type** a message, or tap the mic, speak a
short phrase, and tap **⏹️** to stop. Your words appear in the chat (transcribed
by `sense_ear` when spoken), then `mind` replies and `effector_voice` **speaks the
reply out loud in the background** (no visible player; replies never overlap).
The full path is **audio → text → reply → speech**. The first run downloads the
`large-v3` model (~3 GB) and the Qwen3-TTS Base weights and caches them; later
runs reuse the cache. The first spoken reply can still take a moment while
Qwen3-TTS loads; set `CHRIS_VOICE_WARMUP=1` to warm it up when Streamlit starts.

## 6. Use the modules from your own code

The engines are independent and each has a one-line contract:

```python
from senses.sense_ear import transcribe   # audio in -> text out
from mind import think                     # text in  -> reply out
from effectors.effector_voice import speak  # text in  -> audio file out

text       = transcribe(audio_bytes)
reply      = think(text)
audio_path = speak(reply)
print(reply, "->", audio_path)
```

Full APIs (inputs, return values, options) are in
[reference/senses/sense_ear/](reference/senses/sense_ear/README.md),
[reference/mind/](reference/mind/README.md) and
[reference/effectors/effector_voice/](reference/effectors/effector_voice/README.md).

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `Library libcublas.so.12 is not found` | Ensure `nvidia-cublas-cu12` / `nvidia-cudnn-cu12` are installed (they are in `requirements.txt`). The module preloads them; no `LD_LIBRARY_PATH` needed. |
| First transcription is very slow | The `large-v3` model is downloading/loading. Subsequent calls reuse the cached, in-memory model. |
| Runs on CPU instead of GPU | Check `nvidia-smi`. The module falls back to CPU if CUDA initialization fails; see `Transcriber.device`. |
| Empty string returned | No speech was detected in the clip (silence/noise). That is the expected result. |
| Reply errors / auth failure from `mind` | `OPENAI_API_KEY` is missing or invalid. Check your `.env` (step 3) and that the key is active. |
| `SoX could not be found` during Qwen3-TTS import | Install the system SoX binary (`sudo pacman -S sox` on Arch/Manjaro, `sudo apt install sox` on Debian/Ubuntu). The Python package is installed by `requirements.txt`, but the optional command-line binary is system-level. |
| `No baked 'neutral' voice reference found ...` | You have not baked the voice yet. Run step 4: `python scripts/bake_voice.py --emotion neutral --n 6`, then `--choose`. |
| `CUDNN_STATUS_SUBLIBRARY_VERSION_MISMATCH` during TTS | Set `CHRIS_VOICE_DISABLE_CUDNN=1` in `.env` (required on this Blackwell box) and restart. |
| `flash-attn ... not installed` warning | Harmless — the module falls back to the default attention. To remove it, either install `flash-attn` (delicate on Blackwell) or set `CHRIS_VOICE_ATTN=eager`. |
| First spoken reply is very slow | The Base model is loading. Set `CHRIS_VOICE_WARMUP=1`, and/or use the faster `CHRIS_VOICE_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B-Base`. |
| Voice has a Spanglish accent | Keep `CHRIS_VOICE_LANGUAGE=Spanish`; `Auto` is more flexible but less stable for Spanish. |
| Voice audio is cut short | Increase `CHRIS_VOICE_MAX_NEW_TOKENS` in `.env` and restart Streamlit. |
| CUDA out of memory | Stop old Streamlit/Python processes and check `nvidia-smi`; two app servers can load multiple GPU models at once. |
