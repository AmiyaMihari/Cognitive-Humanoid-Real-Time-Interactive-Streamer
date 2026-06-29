"""Text-to-speech engine: text in, voice audio file out.

The heart of the ``effector_voice`` module. It wraps Qwen3-TTS behind the same
tiny contract the app already uses: callers pass text and get a WAV file path
back. Model loading, device choice and the voice identity stay hidden here.

Runtime synthesis follows a "design-once -> clone" pattern: the voice identity
(and, later, emotion) is frozen offline into reference clips with VoiceDesign
(see ``scripts/bake_voice.py``); at runtime we only *clone* from those clips
with the Base model, which keeps the identity stable across generations.
"""

from __future__ import annotations

import gc
import json
import os
import tempfile
import uuid
import warnings
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import soundfile as sf

from ._models import (
    DEFAULT_EMOTION,
    DEFAULT_LANGUAGE,
    get_cache_dir,
    get_identity_dir,
    get_manifest_path,
    get_model_id,
)
from .streaming import iter_sentences, pipelined_map


class Voice:
    """Turns text into spoken-audio files by cloning a baked voice identity.

    Identity lives on disk under ``identity/`` (one folder per emotion, see
    ``scripts/bake_voice.py``). At least ``neutral`` must be baked; requested
    emotions that are not baked yet fall back to ``neutral``. ``language``
    defaults to ``"Spanish"`` to keep Spanish pronunciation stable.
    """

    def __init__(
        self,
        lang: str = DEFAULT_LANGUAGE,
        emotion: str = DEFAULT_EMOTION,
        speed: float = 1.0,
        output_dir: str | Path | None = None,
        model: str | None = None,
        device: str | None = None,
        dtype: str | None = None,
        attn_implementation: str | None = None,
    ) -> None:
        self.lang = os.environ.get("CHRIS_VOICE_LANGUAGE") or lang
        self.emotion = emotion
        self.speed = speed
        self.model = model or get_model_id()
        self.device = device or os.environ.get("CHRIS_VOICE_DEVICE")
        self.dtype = dtype or os.environ.get("CHRIS_VOICE_DTYPE", "auto")
        # flash-attention 2 by default; a safe fallback applies if it is missing.
        self.attn_implementation = (
            attn_implementation
            or os.environ.get("CHRIS_VOICE_ATTN")
            or "flash_attention_2"
        )
        self.max_new_tokens = int(os.environ.get("CHRIS_VOICE_MAX_NEW_TOKENS", "2048"))
        self._engine = None  # lazily built; see `engine`
        self._prompts: dict[str, Any] | None = None  # baked clone prompts
        self._warmed = False
        self._warned: set[str] = set()  # emotions we've warned about once
        self._output_dir = (
            Path(output_dir)
            if output_dir
            else Path(tempfile.gettempdir()) / "chris_voice"
        )
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

            if _env_flag("CHRIS_VOICE_DISABLE_CUDNN", default=False):
                # cuDNN is ON by default now; this override only exists to work
                # around occasional cuDNN sublibrary mismatches in decoding on
                # the local Blackwell stack.
                torch.backends.cudnn.enabled = False

            load_kwargs = self._load_kwargs(torch)
            self._engine = self._build_engine(Qwen3TTSModel, load_kwargs)
        return self._engine

    def _build_engine(self, model_cls, load_kwargs: dict):
        """Build the model, falling back gracefully if flash-attn is unusable."""
        try:
            return model_cls.from_pretrained(self.model, **load_kwargs)
        except (ImportError, RuntimeError, ValueError) as exc:
            if load_kwargs.get("attn_implementation") != "flash_attention_2":
                raise
            warnings.warn(
                f"flash_attention_2 unavailable ({exc}); falling back to the "
                "default attention implementation.",
                RuntimeWarning,
                stacklevel=2,
            )
            load_kwargs.pop("attn_implementation", None)
            return model_cls.from_pretrained(self.model, **load_kwargs)

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
            kwargs["dtype"] = (
                torch.bfloat16 if torch.cuda.is_available() else torch.float32
            )
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

    # -- voice identity (baked clone prompts) ------------------------------

    def _load_identity(self) -> dict[str, Any]:
        """Build and cache a clone prompt per baked emotion from the manifest.

        ``neutral`` is mandatory; if its reference clip is missing we fail loud
        and early with an actionable message instead of breaking mid-stream.
        """
        if self._prompts is not None:
            return self._prompts

        identity_dir = get_identity_dir()
        manifest_path = get_manifest_path()
        manifest: dict[str, Any] = {}
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        emotions = manifest.get("emotions", {})

        neutral = emotions.get(DEFAULT_EMOTION)
        neutral_ref = (
            identity_dir / neutral["reference"] if neutral else identity_dir / DEFAULT_EMOTION / "reference.wav"
        )
        if not neutral or not neutral_ref.is_file():
            raise RuntimeError(
                "No baked 'neutral' voice reference found at "
                f"{neutral_ref}. Bake it first:\n"
                "    python scripts/bake_voice.py --emotion neutral --n 6\n"
                "then promote a candidate with --choose."
            )

        prompts: dict[str, Any] = {}
        for emotion, meta in emotions.items():
            ref = identity_dir / meta["reference"]
            if not ref.is_file():
                continue
            prompts[emotion] = self.engine.create_voice_clone_prompt(
                ref_audio=str(ref),
                ref_text=meta.get("ref_text"),
                x_vector_only_mode=False,
            )
        self._prompts = prompts
        return prompts

    def warmup(self) -> None:
        """Build the engine, all baked prompts, and run one dummy synthesis.

        Doing this at boot compiles CUDA kernels and primes the model so the
        first *real* sentence is fast. Idempotent: safe to call repeatedly.
        """
        if self._warmed:
            return
        prompts = self._load_identity()
        try:
            self.engine.generate_voice_clone(
                text="Hola.",
                language=self.lang,
                voice_clone_prompt=prompts[DEFAULT_EMOTION],
                max_new_tokens=16,
            )
        finally:
            self.clear_cuda_cache()
        self._warmed = True

    # -- the public operation ----------------------------------------------

    def _resolve_prompt(self, emotion: str | None):
        """Return the clone prompt for ``emotion``, falling back to neutral."""
        prompts = self._load_identity()
        want = emotion or self.emotion
        if want in prompts:
            return prompts[want]
        if want not in self._warned:
            warnings.warn(
                f"Emotion '{want}' is not baked yet; using 'neutral'. "
                f"Bake it with: python scripts/bake_voice.py --emotion {want}",
                RuntimeWarning,
                stacklevel=2,
            )
            self._warned.add(want)
        return prompts[DEFAULT_EMOTION]

    def synthesize(
        self, text: str, emotion: str | None = None
    ) -> tuple[np.ndarray, int]:
        """Synthesize ``text`` and return (samples, sample_rate) in memory.

        Use this for the raw audio (e.g. to stream); most callers want
        :meth:`speak`, which writes a file. ``emotion`` falls back to neutral
        when not baked yet.
        """
        prompt = self._resolve_prompt(emotion)
        try:
            wavs, sample_rate = self.engine.generate_voice_clone(
                text=text,
                language=self.lang,
                voice_clone_prompt=prompt,
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

    def speak(
        self,
        text: str,
        emotion: str | None = None,
        path: str | Path | None = None,
    ) -> Path:
        """Synthesize ``text`` to a WAV file and return its path.

        ``path`` may be given to control the destination; otherwise a uniquely
        named file is written under the output directory. This is the method the
        chat uses: it receives ``mind``'s reply and produces audio to play.
        """
        samples, sample_rate = self.synthesize(text, emotion=emotion)
        out = (
            Path(path)
            if path
            else self._output_dir / f"reply_{uuid.uuid4().hex}.wav"
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(out), samples, sample_rate)
        return out

    # -- sentence-level streaming (anti-silence pipeline) ------------------

    def synthesize_stream(
        self, text: str, emotion: str | None = None, prefetch: int = 1
    ) -> Iterator[tuple[np.ndarray, int]]:
        """Yield (samples, sample_rate) per sentence, in order, with prefetch.

        Sentence N+1 is synthesized in a worker thread while the consumer plays
        sentence N, which removes the silent gaps between sentences. Worker
        exceptions propagate to the consumer and the thread is closed cleanly.
        """
        sentences = iter_sentences(text)
        yield from pipelined_map(
            sentences,
            lambda sentence: self.synthesize(sentence, emotion=emotion),
            prefetch=prefetch,
        )

    def speak_stream(
        self, text: str, emotion: str | None = None, prefetch: int = 1
    ) -> Iterator[Path]:
        """Like :meth:`synthesize_stream`, but write each sentence to a WAV.

        Yields the path of each sentence's audio file in order, for playback
        layers that prefer files over in-memory buffers.
        """
        for samples, sample_rate in self.synthesize_stream(
            text, emotion=emotion, prefetch=prefetch
        ):
            out = self._output_dir / f"reply_{uuid.uuid4().hex}.wav"
            sf.write(str(out), samples, sample_rate)
            yield out

    # -- cleanup -----------------------------------------------------------

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
        self._prompts = None
        self._warmed = False
        gc.collect()
        self.clear_cuda_cache()


def _env_flag(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}
