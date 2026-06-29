"""Application-level streaming for the voice effector.

Qwen3-TTS does not expose real intra-sentence audio-token streaming
(``generate_voice_clone`` returns the full waveform). To kill the silence
between sentences we stream at the *application* level: split text into
sentences and pipeline them, so sentence N can play while sentence N+1 is
already being synthesized in a worker thread.
"""

from __future__ import annotations

import queue
import re
import threading
from typing import Callable, Iterable, Iterator, TypeVar

T = TypeVar("T")
R = TypeVar("R")

# Sentence terminators, keeping Spanish ellipsis and inverted openers in mind.
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")
# Common abbreviations whose trailing dot must not end a sentence.
_ABBREVIATIONS = {
    "sr", "sra", "srta", "dr", "dra", "ud", "uds", "etc", "vs", "p.ej",
    "ej", "no", "núm", "av", "art", "ing", "lic",
}
# Merge fragments shorter than this (chars) into the next one, so we never
# synthesize a stray "Sí." on its own.
_MIN_SENTENCE_CHARS = 12


def iter_sentences(text: str, min_chars: int = _MIN_SENTENCE_CHARS) -> Iterator[str]:
    """Yield sentence-sized chunks of ``text`` suitable for one synthesis call.

    Splits on ``. ? ! …`` and line breaks, tolerates Spanish ``¿ ¡`` openers,
    skips obvious abbreviations, and merges very short fragments forward so a
    lone short word is never synthesized on its own.
    """
    raw_lines = text.replace("\r\n", "\n").split("\n")
    pieces: list[str] = []
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        for part in _SENTENCE_SPLIT.split(line):
            part = part.strip()
            if part:
                pieces.append(part)

    # Stitch back fragments that were split on an abbreviation's dot, and merge
    # fragments that are too short to stand alone.
    merged: list[str] = []
    for piece in pieces:
        if merged and _ends_with_abbreviation(merged[-1]):
            merged[-1] = f"{merged[-1]} {piece}"
        elif merged and len(merged[-1]) < min_chars:
            merged[-1] = f"{merged[-1]} {piece}"
        else:
            merged.append(piece)

    yield from merged


def _ends_with_abbreviation(text: str) -> bool:
    last = text.split()[-1].rstrip(".").lower() if text.split() else ""
    return last in _ABBREVIATIONS


def pipelined_map(
    items: Iterable[T],
    work: Callable[[T], R],
    prefetch: int = 1,
) -> Iterator[R]:
    """Apply ``work`` to ``items`` in order, one item ahead in a worker thread.

    The worker computes results into a bounded queue so the consumer can use
    result N while result N+1 is already being produced. Exceptions raised in
    the worker are re-raised in the consumer, and the worker is always joined
    cleanly -- including when the consumer stops early or is interrupted.
    """
    results: queue.Queue = queue.Queue(maxsize=max(1, prefetch) + 1)
    _DONE = object()
    stop = threading.Event()

    def _worker() -> None:
        try:
            for item in items:
                if stop.is_set():
                    break
                results.put(work(item))
        except BaseException as exc:  # propagate to the consumer
            results.put(exc)
        finally:
            results.put(_DONE)

    thread = threading.Thread(target=_worker, name="voice-stream", daemon=True)
    thread.start()
    try:
        while True:
            out = results.get()
            if out is _DONE:
                break
            if isinstance(out, BaseException):
                raise out
            yield out
    finally:
        stop.set()
        # Drain so a blocked worker can finish putting and exit.
        while thread.is_alive():
            try:
                if results.get(timeout=0.1) is _DONE:
                    break
            except queue.Empty:
                pass
        thread.join(timeout=1.0)
