# `app.py` — Streamlit demo

Source: [`app.py`](../../app.py)

A minimal, ChatGPT-style demo wiring together the `sense_ear` and `mind` modules.
Two inputs only: **type** a message, or tap the **microphone** and speak. Spoken
audio is transcribed by `senses.sense_ear`, the resulting text is sent to `mind`,
and `mind`'s reply appears in the chat. The full path is **audio → text → reply**.

The app is intentionally thin: it contains **no speech or LLM logic**. All
transcription happens inside `sense_ear` and all thinking inside `mind`, so the
UI never imports Whisper or OpenAI directly.

## Run it

```fish
streamlit run app.py
```

## What it does

| Element | Behaviour |
| --- | --- |
| **Model load** | `load_transcriber()` builds the transcriber once and keeps it warm across reruns/sessions via `@st.cache_resource`. The first run downloads `large-v3` (~3 GB) and caches it. |
| **Chat history** | Stored in `st.session_state.messages` and re-rendered with `st.chat_message`. |
| **🔴 Microphone** | `streamlit_mic_recorder.mic_recorder` records in the browser and returns a **WAV** clip when you stop. The bytes are passed to `transcriber.transcribe(...)` to get text. |
| **Text box** | `st.chat_input` captures typed messages directly. |
| **Reply** | Whether the text came from the mic or the keyboard, it is sent to [`mind.think(...)`](mind/README.md), and the returned reply is appended to the chat as the assistant. |

> The demo is a working end-to-end loop: hear/read → think → reply. The speech
> and thinking logic both live in their modules; this file only orchestrates.

## Dependencies used here

- [`senses.sense_ear`](senses/sense_ear/README.md) — the transcription module.
- [`mind`](mind/README.md) — the thinking module (text → reply).
- `streamlit` — the web UI framework.
- `streamlit-mic-recorder` — in-browser microphone capture (returns WAV bytes).

## Customizing

Because all speech and thinking logic is in the modules, you can change the UI
freely. To change transcription behaviour (model, language, device), build a
custom `Transcriber` — see [transcriber.md](senses/sense_ear/transcriber.md). To
change the reply behaviour (a different model), build a custom `Mind` — see
[mind/agent.md](mind/agent.md) — and use it instead of the shared singletons.
