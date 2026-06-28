"""Minimal ChatGPT-style chat UI.

One thin screen: the conversation, plus a single input row at the bottom — a
text box with a microphone icon on its right. Type or speak; `sense_ear`
transcribes speech and `mind` replies. Nothing is persisted between sessions.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st
from streamlit_mic_recorder import mic_recorder

from mind import think_stream
from senses.sense_ear import get_transcriber
from effectors.effector_voice import get_voice

st.set_page_config(page_title="C.H.R.I.S.", page_icon="🎙️")


@st.cache_resource(show_spinner="Loading the speech model (first run only)...")
def load_transcriber():
    """Build the transcriber once and keep it warm across reruns/sessions."""
    transcriber = get_transcriber()
    # Force the (slow) model load to happen here. Assigned to a throwaway so
    # Streamlit's "magic" doesn't render the WhisperModel object to the page.
    _ = transcriber.model
    return transcriber


def load_voice():
    """Return the shared TTS voice without loading Qwen until speech is needed."""
    return get_voice()


# CSS that pins the input row to the bottom of the screen (ChatGPT-style) and
# keeps the last messages from hiding behind it. `.st-key-input_bar` is the class
# Streamlit gives the `st.container(key="input_bar")` below.
_PINNED_INPUT_CSS = """
<style>
.st-key-input_bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    margin: 0 auto;
    max-width: 46rem;
    padding: 0.5rem 1rem 0.75rem;
    background-color: var(--background-color, #ffffff);
    z-index: 100;
}
[data-testid="stMainBlockContainer"] { padding-bottom: 6rem; }
</style>
"""


def main() -> None:
    voice = load_voice()
    st.markdown(_PINNED_INPUT_CSS, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render the conversation so far (this session only; nothing is saved).
    # Assistant messages also carry a voice clip: the newest one autoplays once;
    # older ones keep a player so they can be replayed on demand.
    last_index = len(st.session_state.messages) - 1
    for index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            audio_path = message.get("audio")
            if audio_path:
                autoplay = index == last_index and st.session_state.get("play_latest", False)
                st.audio(audio_path, format="audio/wav", autoplay=autoplay)
    # The newest reply has now been (auto)played; don't replay it on the next rerun.
    st.session_state.play_latest = False

    def reply_to(user_text: str) -> None:
        """Store the user's words, stream a text reply, then speak it once."""
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

        answer_parts: list[str] = []
        audio_path = None

        with st.chat_message("assistant"):
            text_slot = st.empty()
            with st.spinner("Thinking..."):
                for delta in think_stream(user_text):
                    answer_parts.append(delta)
                    text_slot.markdown("".join(answer_parts))

            answer = "".join(answer_parts)
            try:
                with st.spinner("Speaking..."):
                    audio_path = str(voice.speak(answer))
            except Exception as exc:
                st.session_state.last_tts_error = str(exc)
                audio_path = None
            if audio_path:
                st.audio(audio_path, format="audio/wav", autoplay=True)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "audio": audio_path}
        )
        st.session_state.play_latest = False

    # Input row: a text box with the mic icon to its right (ChatGPT-style),
    # pinned to the bottom of the screen via the CSS above.
    with st.container(key="input_bar"):
        text_col, mic_col = st.columns([12, 1], vertical_alignment="bottom")

        with text_col:
            typed = st.chat_input("Message")

        with mic_col:
            audio = mic_recorder(
                start_prompt="🎙️",
                stop_prompt="⏹️",
                just_once=True,
                format="wav",
                key="mic",
            )

    # Speech path: transcribe, then reply. Silence is simply ignored.
    if audio and audio.get("bytes"):
        with st.spinner("Transcribing..."):
            voice.unload()
            transcriber = load_transcriber()
            text = transcriber.transcribe(audio["bytes"])
            transcriber.unload()
        if text:
            reply_to(text)

    # Text path.
    if typed:
        reply_to(typed)


if __name__ == "__main__":
    main()
