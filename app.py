"""Minimal ChatGPT-style demo for the sense_ear module.

Two inputs only: type a message, or hold the microphone and speak. Spoken
audio is sent to ``sense_ear`` and the recognised text appears in the chat
right away. The app is intentionally thin -- all the speech logic lives in the
isolated ``sense_ear`` module, so this file never touches Whisper directly.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st
from streamlit_mic_recorder import mic_recorder

from senses.sense_ear import get_transcriber

st.set_page_config(page_title="sense_ear", page_icon="🎙️")


@st.cache_resource(show_spinner="Loading the speech model (first run only)...")
def load_transcriber():
    """Build the transcriber once and keep it warm across reruns/sessions."""
    transcriber = get_transcriber()
    transcriber.model  # force the (slow) model load to happen here
    return transcriber


def main() -> None:
    st.title("🎙️ sense_ear")
    st.caption("Type a message, or tap the mic and speak — your words appear as text.")

    transcriber = load_transcriber()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render the conversation so far.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Microphone input -------------------------------------------------
    # Records in the browser and returns the clip when the user stops.
    audio = mic_recorder(
        start_prompt="🔴 Start recording",
        stop_prompt="⏹️ Stop recording",
        just_once=True,
        format="wav",
        key="mic",
    )

    if audio and audio.get("bytes"):
        with st.spinner("Transcribing..."):
            text = transcriber.transcribe(audio["bytes"])
        text = text or "_(no speech detected)_"
        st.session_state.messages.append({"role": "user", "content": text})
        st.rerun()

    # --- Text input -------------------------------------------------------
    typed = st.chat_input("Write a message...")
    if typed:
        st.session_state.messages.append({"role": "user", "content": typed})
        st.rerun()


if __name__ == "__main__":
    main()
