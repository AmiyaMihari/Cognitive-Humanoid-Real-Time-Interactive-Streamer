"""Speech-to-text engine: audio in, text out.

This is the heart of the ``sense_ear`` module. It wraps faster-whisper with a
configuration tuned for **short, real-time** utterances (the original notebook
targeted long interview recordings instead).

Design goals:
    * Audio in  -> text out. Nothing else leaks out of this module.
    * Load the model once; reuse it across calls (the model is the expensive part).
    * Run on the GPU (CUDA / float16) by default, with a transparent CPU fallback.
    * Accept whatever the caller has: a file path, raw encoded bytes
      (e.g. a WAV blob from a browser mic), a file-like object or a numpy array.
"""

from __future__ import annotations

import io
import os
from typing import BinaryIO, Union

from faster_whisper import WhisperModel

from ._cuda import preload_cuda_libraries

# A piece of audio can arrive in any of these shapes.
AudioInput = Union[str, bytes, bytearray, BinaryIO, "object"]


class Transcriber:
    """Loads a Whisper model once and turns audio into text.

    Parameters mirror the notebook (same Spanish ``large-v3`` model on CUDA),
    but the decoding defaults are tuned for short clips rather than long files.
    """

    def __init__(
        self,
        model_size: str = "large-v3",
        device: str = "cuda",
        compute_type: str = "float16",
        language: str = "es",
        beam_size: int = 5,
        cpu_fallback: bool = True,
    ) -> None:
        self.model_size = model_size
        self.language = language
        self.beam_size = beam_size
        self._model: WhisperModel | None = None
        self._device = device
        self._compute_type = compute_type
        self._cpu_fallback = cpu_fallback

    # -- model lifecycle ---------------------------------------------------

    def _load_model(self) -> WhisperModel:
        """Lazily build the WhisperModel, falling back to CPU if CUDA fails."""
        if self._device == "cuda":
            # Make CUDA 12 libs resolvable before CTranslate2 touches the GPU.
            preload_cuda_libraries()

        # An HF token is optional for the public Systran large-v3 weights, but
        # honoured if present so private/rate-limited downloads keep working.
        token = os.environ.get("HF_TOKEN")
        try:
            return WhisperModel(
                self.model_size,
                device=self._device,
                compute_type=self._compute_type,
                # faster-whisper's auth kwarg is `use_auth_token`; unknown kwargs
                # are forwarded to ctranslate2.Whisper, which rejects them.
                **({"use_auth_token": token} if token else {}),
            )
        except Exception:
            if self._device == "cuda" and self._cpu_fallback:
                # Degrade gracefully so a missing/broken CUDA setup still works.
                self._device = "cpu"
                self._compute_type = "int8"
                return WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8",
                    **({"use_auth_token": token} if token else {}),
                )
            raise

    @property
    def model(self) -> WhisperModel:
        if self._model is None:
            self._model = self._load_model()
        return self._model

    @property
    def device(self) -> str:
        """Device actually in use ('cuda' or 'cpu') after any fallback."""
        return self._device

    # -- the public operation ----------------------------------------------

    def transcribe(self, audio: AudioInput) -> str:
        """Transcribe a single short utterance and return the text.

        ``audio`` may be a path, encoded bytes (WAV/MP3/...), a binary
        file-like object or a 16 kHz float32 numpy array.
        """
        source = self._coerce_audio(audio)

        segments, _info = self.model.transcribe(
            source,
            language=self.language,
            task="transcribe",  # transcribe, never translate
            beam_size=self.beam_size,
            vad_filter=True,  # drop leading/trailing silence from the clip
            vad_parameters=dict(min_silence_duration_ms=300),
            # Each utterance is independent, so don't condition on prior text.
            # This avoids cross-clip hallucinations and repetition loops.
            condition_on_previous_text=False,
        )

        return " ".join(segment.text.strip() for segment in segments).strip()

    @staticmethod
    def _coerce_audio(audio: AudioInput):
        """Normalise the supported input shapes into something faster-whisper reads."""
        if isinstance(audio, (bytes, bytearray)):
            # Encoded audio bytes (e.g. a WAV blob) -> in-memory file object.
            return io.BytesIO(bytes(audio))
        # str path, file-like object and numpy array are accepted as-is.
        return audio
