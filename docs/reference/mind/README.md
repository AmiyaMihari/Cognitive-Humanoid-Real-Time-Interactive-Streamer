# `mind` — text-to-reply (the thinking faculty)

Source: [`mind/__init__.py`](../../../mind/__init__.py)

The **thinking** faculty. Its entire contract is:

> **text in → reply out.**

It wraps an OpenAI chat model behind a minimal [LangGraph](https://langchain-ai.github.io/langgraph/)
graph and hides all model, client and lifecycle handling. Where `sense_ear`
turns *audio into text*, `mind` turns *that text into a response*.

---

## Quick start

```python
from mind import think

reply = think("Hola, ¿cómo estás?")   # -> str
```

That single call:

1. Lazily builds a shared `Mind` the first time it runs (constructs the OpenAI
   client and compiles the LangGraph graph; happens **once** per process).
2. Sends the text to the model.
3. Returns the model's reply as a plain `str`.

---

## Public API

The module exports exactly three names (`__all__`):

| Name | Kind | Summary |
| --- | --- | --- |
| [`think(text)`](#thinktext---str) | function | One-shot convenience: text → reply using a shared `Mind`. |
| [`get_mind()`](#get_mind---mind) | function | Returns the process-wide shared `Mind`. |
| [`Mind`](#class-mind) | class | The engine; construct one directly to pick a different model. |

### `think(text) -> str`

Send a piece of text to the shared default `Mind` and return its reply.

- **Parameter** — `text` (`str`): the message to respond to (for example, a
  transcript coming from `sense_ear`).
- **Returns** — `str`: the model's reply.

```python
from mind import think

print(think("Summarize what I just said in one sentence."))
```

### `get_mind() -> Mind`

Return the **shared, process-wide** `Mind` (created on first call, reused after).
Use this when you want the singleton but also need the object itself:

```python
from mind import get_mind

brain = get_mind()
reply = brain.think("Hello!")
```

### class `Mind`

The engine. Construct your own instance when you want a non-default model.
Full details in [agent.md](agent.md). Constructor summary:

```python
Mind(
    model="gpt-4o-mini",   # any OpenAI chat model name
)
```

Main method — `Mind.think(text) -> str` — same input/return contract as the
module-level `think()`.

---

## What it returns

- Type: **`str`** — always.
- Content: the model's reply text.

---

## Behaviour notes

- **Stateless per call.** Each `think()` sends a single user message and returns
  the reply; the graph keeps no memory between calls. (Conversation history, if
  ever needed, would be added inside the module — callers would not change.)
- **Built once.** The first call (or `get_mind()`) constructs the OpenAI client
  and compiles the graph; both are reused for the process lifetime.
- **Default model is `gpt-4o-mini`.** Construct a `Mind(model=...)` for another.

---

## Secrets handling

On import, the module loads a git-ignored `.env` (via `python-dotenv`) so
`OPENAI_API_KEY` is picked up automatically. Existing environment variables take
precedence over `.env` values.

`OPENAI_API_KEY` is **required** — without it the OpenAI client cannot
authenticate. See
[getting-started.md](../../getting-started.md#3-configure-your-api-keys).

---

## Related pages

- [agent.md](agent.md) — the `Mind` class and its LangGraph graph in full.
- [architecture.md](../../architecture.md) — where this module fits and why.
- [senses/sense_ear/](../senses/sense_ear/README.md) — the module that produces
  the text `mind` consumes.
