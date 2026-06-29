# `effectors.effector_voice.streaming`

Source: [`effectors/effector_voice/streaming.py`](../../../../effectors/effector_voice/streaming.py)

Application-level streaming for the voice effector: split text into sentences and
pipeline them so sentence N can play while sentence N+1 is still being
synthesized.

> ⚠️ This is **not** intra-sentence audio-token streaming. The local `qwen_tts`
> package returns the full waveform per call (`generate_voice_clone` is not a
> generator), so streaming here happens at the *sentence* level only.

## Public API

| Name | Kind | Summary |
| --- | --- | --- |
| [`iter_sentences(text, min_chars=12)`](#iter_sentencestext-min_chars12---iteratorstr) | function | Split text into sentence-sized chunks. |
| [`pipelined_map(items, work, prefetch=1)`](#pipelined_mapitems-work-prefetch1---iteratorr) | function | Apply `work` to `items` in order, one step ahead in a worker thread. |

These power [`Voice.synthesize_stream` / `Voice.speak_stream`](synthesizer.md);
most callers use those rather than calling these directly.

### `iter_sentences(text, min_chars=12) -> Iterator[str]`

Yield sentence-sized chunks suitable for one synthesis call.

- Splits on `.` `?` `!` `…` and line breaks.
- Tolerates Spanish `¿` `¡` openers.
- Skips obvious abbreviations (e.g. `Sr.`, `Dra.`, `etc.`) so their dot does not
  end a sentence.
- Merges fragments shorter than `min_chars` into the next one, so a lone `"Sí."`
  is never synthesized on its own.

```python
from effectors.effector_voice.streaming import iter_sentences

list(iter_sentences("Sí. Ah, ya volviste. ¿En qué andas?"))
# ['Sí. Ah, ya volviste.', '¿En qué andas?']
```

### `pipelined_map(items, work, prefetch=1) -> Iterator[R]`

Apply `work` to `items` **in order**, computing one item ahead in a worker
thread so the consumer can use result N while result N+1 is already being
produced.

- `items` - any iterable.
- `work` - callable applied to each item (here, "synthesize one sentence").
- `prefetch` - how many results to compute ahead (queue size is `prefetch + 1`).

Guarantees:

- **Order preserved** — results come out in input order.
- **Exceptions propagate** — an error in the worker is re-raised in the consumer.
- **Clean shutdown** — the worker thread is always joined, including when the
  consumer stops early or is interrupted (no dangling threads).

```python
from effectors.effector_voice.streaming import pipelined_map

for n in pipelined_map([1, 2, 3], lambda x: x * 10, prefetch=1):
    print(n)        # 10, 20, 30 (in order)
```

## Related pages

- [synthesizer.md](synthesizer.md) - `synthesize_stream` / `speak_stream` use these.
- [README.md](README.md) - the module's public API.
