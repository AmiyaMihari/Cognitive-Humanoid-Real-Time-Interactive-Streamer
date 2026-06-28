"""Text-to-speech engine: text in, voice audio file out.

The heart of the ``effector_voice`` module. It wraps Qwen3-TTS VoiceDesign
behind the same tiny contract the app already uses: callers pass text and get a
WAV file path back. Model loading, device choice and voice-design instructions
stay hidden inside this module.
"""

from __future__ import annotations

import gc
import os
import tempfile
import uuid
from pathlib import Path

import numpy as np
import soundfile as sf

from ._models import (
    DEFAULT_LANGUAGE,
    DEFAULT_VOICE_DESCRIPTION,
    get_cache_dir,
    get_model_id,
)


class Voice:
    """Turns text into spoken-audio files using Qwen3-TTS VoiceDesign.

    The default instruction describes the custom voice for this project.
    ``language`` defaults to ``"Auto"`` so Qwen3-TTS can adapt to the input text.
    """

    def __init__(
        self,
        voice: str = DEFAULT_VOICE_DESCRIPTION,
        lang: str = DEFAULT_LANGUAGE,
        speed: float = 1.0,
        output_dir: str | Path | None = None,
        model: str | None = None,
        device: str | None = None,
        dtype: str | None = None,
        attn_implementation: str | None = None,
    ) -> None:
        self.voice = voice
        self.lang = lang
        self.speed = speed
        self.model = model or get_model_id()
        self.device = device or os.environ.get("CHRIS_VOICE_DEVICE")
        self.dtype = dtype or os.environ.get("CHRIS_VOICE_DTYPE", "auto")
        self.attn_implementation = attn_implementation or os.environ.get(
            "CHRIS_VOICE_ATTN"
        )
        self.max_new_tokens = int(os.environ.get("CHRIS_VOICE_MAX_NEW_TOKENS", "768"))
        self._engine = None  # lazily built; see `engine`
        self._output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir()) / "chris_voice"
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # -- model lifecycle ---------------------------------------------------

    @property
    def engine(self):
        """The underlying Qwen3-TTS engine, built on first access."""
        if self._engine is None:
            cache_dir = get_cache_dir()
            if cache_dir:
                os.environ.setdefault("HF_HOME", str(cache_dir))

            # Imported lazily so importing effectors.effector_voice stays cheap.
            import torch
            from transformers.utils import logging as transformers_logging
            from qwen_tts import Qwen3TTSModel

            transformers_logging.set_verbosity_error()

            if _env_flag("CHRIS_VOICE_DISABLE_CUDNN", default=True):
                # Work around cuDNN sublibrary mismatches seen in Qwen3-TTS
                # decoding on the local PyTorch cu130/Blackwell stack.
                torch.backends.cudnn.enabled = False

            load_kwargs = self._load_kwargs(torch)
            self._engine = Qwen3TTSModel.from_pretrained(self.model, **load_kwargs)
        return self._engine

    def _load_kwargs(self, torch) -> dict:
        kwargs: dict = {}
        cache_dir = get_cache_dir()
        if cache_dir:
            kwargs["cache_dir"] = str(cache_dir)

        if self.device:
            kwargs["device_map"] = self.device
        elif torch.cuda.is_available():
            kwargs["device_map"] = "cuda:0"
        else:
            kwargs["device_map"] = "cpu"

        dtype = self.dtype.lower()
        if dtype == "auto":
            kwargs["dtype"] = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        elif dtype in {"bfloat16", "bf16"}:
            kwargs["dtype"] = torch.bfloat16
        elif dtype in {"float16", "fp16"}:
            kwargs["dtype"] = torch.float16
        elif dtype in {"float32", "fp32"}:
            kwargs["dtype"] = torch.float32
        else:
            raise ValueError(
                "CHRIS_VOICE_DTYPE must be auto, bfloat16, float16, or float32."
            )

        if self.attn_implementation:
            kwargs["attn_implementation"] = self.attn_implementation
        return kwargs

    # -- the public operation ----------------------------------------------

    def synthesize(self, text: str) -> tuple[np.ndarray, int]:
        """Synthesize ``text`` and return (samples, sample_rate) in memory.

        Use this when you want the raw audio (e.g. to stream); most callers want
        :meth:`speak`, which writes a file.
        """
        try:
            wavs, sample_rate = self.engine.generate_voice_design(
                text=text,
                language=self.lang,
                instruct=self.voice,
                max_new_tokens=self.max_new_tokens,
            )
        finally:
            self.clear_cuda_cache()
        samples = np.asarray(wavs[0], dtype=np.float32)
        if self.speed == 1.0:
            return samples, sample_rate
        return self._resample_speed(samples, sample_rate, self.speed), sample_rate

    def _resample_speed(
        self, samples: np.ndarray, sample_rate: int, speed: float
    ) -> np.ndarray:
        if speed <= 0:
            raise ValueError("speed must be greater than 0.")
        try:
            import librosa
        except ImportError as exc:
            raise RuntimeError("Changing speed requires librosa.") from exc
        return librosa.effects.time_stretch(samples, rate=speed).astype(np.float32)

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

    def clear_cuda_cache(self) -> None:
        """Release temporary PyTorch CUDA allocations after a synthesis call."""
        try:
            import torch
        except ImportError:
            return
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()

    def unload(self) -> None:
        """Unload Qwen3-TTS from memory so another GPU model can run."""
        self._engine = None
        gc.collect()
        self.clear_cuda_cache()


def _env_flag(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}
