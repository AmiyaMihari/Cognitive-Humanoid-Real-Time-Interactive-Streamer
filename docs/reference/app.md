# `app.py` — Streamlit demo

Source: [`app.py`](../../app.py)

A minimal, ChatGPT-style demo wiring together the `sense_ear`, `mind` and
`effector_voice` modules. Two inputs only: **type** a message, or tap the
**microphone** and speak. Spoken audio is transcribed by `senses.sense_ear`, the
resulting text is sent to `mind`, its reply appears in the chat **and is spoken
aloud** by `effectors.effector_voice`. The full path is
**audio → text → reply → speech**.

The app is intentionally thin: it contains **no speech, LLM or TTS logic**. All
transcription happens inside `sense_ear`, all thinking inside `mind`, and all
speech synthesis inside `effector_voice`, so the UI never imports Whisper,
OpenAI or Qwen3-TTS directly.

## Run it

```bash
streamlit run app.py
```

## What it does

| Element | Behaviour |
| --- | --- |
| **Model load** | The transcriber loads only when the microphone path is used. Qwen3-TTS loads on first speech by default so the app opens with low VRAM use; set `CHRIS_VOICE_WARMUP=1` to load it at startup instead. The first run downloads `large-v3` (~3 GB) and the Qwen3-TTS VoiceDesign weights and caches them. |
| **Layout** | A single minimal screen: the conversation thread, then one input row — `st.chat_input` and the mic icon placed side by side via `st.columns([12, 1])`, ChatGPT-style. No title, sidebar, or saved chats. |
| **Chat history** | Stored in `st.session_state.messages` and re-rendered with `st.chat_message`. This is the current session only — nothing is persisted. |
| **🎙️ Microphone** | `streamlit_mic_recorder.mic_recorder` records in the browser and returns a **WAV** clip when you stop. The bytes are passed to `transcriber.transcribe(...)` to get text. |
| **Text box** | `st.chat_input` captures typed messages directly. |
| **Reply** | Whether the text came from the mic or the keyboard, it is sent to [`mind.think(...)`](mind/README.md), and the returned reply is appended to the chat as the assistant. |
| **🔊 Voice** | Replies stream as text from `mind`; once the full answer is available, the app sends the whole answer to Qwen3-TTS once and autoplays the resulting WAV. This is deliberate: phrase-by-phrase VoiceDesign synthesis can produce different timbres per paragraph and overlapping browser autoplay. TTS is best-effort: if it fails, the text reply still stands. |

> The demo is a working end-to-end loop: hear/read → think → reply → speak. The
> speech, thinking and TTS logic all live in their modules; this file only
> orchestrates.

## Dependencies used here

- [`senses.sense_ear`](senses/sense_ear/README.md) — the transcription module.
- [`mind`](mind/README.md) — the thinking module (text → reply).
- [`effectors.effector_voice`](effectors/effector_voice/README.md) — the text-to-speech module (text → audio file).
- `streamlit` — the web UI framework.
- `streamlit-mic-recorder` — in-browser microphone capture (returns WAV bytes).

## Customizing

Because all speech, thinking and TTS logic is in the modules, you can change the
UI freely. To change transcription behaviour (model, language, device), build a
custom `Transcriber` — see [transcriber.md](senses/sense_ear/transcriber.md). To
change the reply behaviour (a different model), build a custom `Mind` — see
[mind/agent.md](mind/agent.md). To change the spoken voice (a different voice,
language or speed), build a custom `Voice` — see
[effectors/effector_voice/synthesizer.md](effectors/effector_voice/synthesizer.md)
— and use it instead of the shared singletons.
