"""Text-to-speech engine: text in, voice audio file out.

The heart of the ``effector_voice`` module. It wraps Kokoro (an 82M-parameter
ONNX TTS model) behind a tiny contract and is tuned for **low latency**:

    * Runs on CPU through onnxruntime — no PyTorch, and it leaves the GPU free
      for speech-to-text (sense_ear) and the LLM (mind). Kokoro is small enough
      to synthesize several times faster than real time on CPU.
    * Loads the model once and reuses it across calls.
    * Default voice is a youthful Spanish female (``ef_dora``).

Design goal: take ``mind``'s reply (text) and produce an audio file to play.
"""

from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

import numpy as np
import soundfile as sf

from ._models import ensure_model_files


class Voice:
    """Turns text into spoken-audio files using Kokoro.

    Parameters let you pick a different voice, language or speaking rate, but the
    defaults are chosen for this project: a youthful Spanish female voice.
    """

    def __init__(
        self,
        voice: str = "ef_dora",   # youthful Spanish female
        lang: str = "es",         # Spanish phonemization
        speed: float = 1.0,       # 1.0 = natural pace; >1 faster, <1 slower
        output_dir: str | Path | None = None,
    ) -> None:
        self.voice = voice
        self.lang = lang
        self.speed = speed
        self._kokoro = None  # lazily built; see `engine`
        self._output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir()) / "chris_voice"
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # -- model lifecycle ---------------------------------------------------

    @property
    def engine(self):
        """The underlying Kokoro engine, built on first access (the slow part)."""
        if self._kokoro is None:
            # Imported here so the heavy onnxruntime import is paid lazily.
            from kokoro_onnx import Kokoro

            model_path, voices_path = ensure_model_files()
            self._kokoro = Kokoro(str(model_path), str(voices_path))
        return self._kokoro

    # -- the public operation ----------------------------------------------

    def synthesize(self, text: str) -> tuple[np.ndarray, int]:
        """Synthesize ``text`` and return (samples, sample_rate) in memory.

        Use this when you want the raw audio (e.g. to stream); most callers want
        :meth:`speak`, which writes a file.
        """
        samples, sample_rate = self.engine.create(
            text, voice=self.voice, speed=self.speed, lang=self.lang
        )
        return samples, sample_rate

    def speak(self, text: str, path: str | Path | None = None) -> Path:
        """Synthesize ``text`` to a WAV file and return its path.

        ``path`` may be given to control the destination; otherwise a uniquely
        named file is written under the output directory. This is the method the
        chat uses: it receives ``mind``'s reply and produces the audio to play.
        """
        samples, sample_rate = self.synthesize(text)
        out = Path(path) if path else self._output_dir / f"reply_{uuid.uuid4().hex}.wav"
        out.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(out), samples, sample_rate)
        return out
