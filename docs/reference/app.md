# `app.py` — Streamlit demo

Source: [`app.py`](../../app.py)

A minimal, ChatGPT-style demo for the `sense_ear` module. Two inputs only:
**type** a message, or tap the **microphone** and speak. Spoken audio is sent to
`senses.sense_ear` and the recognised text appears in the chat immediately.

The app is intentionally thin: it contains **no speech logic**. All transcription
happens inside the isolated module, so the UI never imports Whisper directly.

## Run it

```fish
streamlit run app.py
```

## What it does

| Element | Behaviour |
| --- | --- |
| **Model load** | `load_transcriber()` builds the transcriber once and keeps it warm across reruns/sessions via `@st.cache_resource`. The first run downloads `large-v3` (~3 GB) and caches it. |
| **Chat history** | Stored in `st.session_state.messages` and re-rendered with `st.chat_message`. |
| **🔴 Microphone** | `streamlit_mic_recorder.mic_recorder` records in the browser and returns a **WAV** clip when you stop. The bytes are passed to `transcriber.transcribe(...)`; the text is appended to the chat. Empty result shows `(no speech detected)`. |
| **Text box** | `st.chat_input` appends typed messages directly. |

> The demo simply echoes back what you said or typed (it is not a chatbot) — its
> purpose is to show the speech-to-text module working end to end.

## Dependencies used here

- [`senses.sense_ear`](senses/sense_ear/README.md) — the transcription module.
- `streamlit` — the web UI framework.
- `streamlit-mic-recorder` — in-browser microphone capture (returns WAV bytes).

## Customizing

Because all speech handling is in the module, you can change the UI freely. To
change transcription behaviour (model, language, device), build a custom
`Transcriber` — see [transcriber.md](senses/sense_ear/transcriber.md) — and use
it instead of `get_transcriber()`.
