# `mind.agent`

Source: [`mind/agent.py`](../../../mind/agent.py)

The engine behind the module: a minimal [LangGraph](https://langchain-ai.github.io/langgraph/)
graph wrapped around an OpenAI chat model. Where the public
[README](README.md) describes the *contract*, this page describes the *class*.

## class `Mind`

A tiny language-model brain: give it text, get back a reply.

### Constructor

```python
Mind(
    model: str = "gpt-4o-mini",
)
```

| Parameter | Default | Description |
| --- | --- | --- |
| `model` | `"gpt-4o-mini"` | Any OpenAI chat model name passed to `ChatOpenAI`. |

On construction the `Mind`:

1. Builds a `ChatOpenAI` client for `model` (reads `OPENAI_API_KEY` from the
   environment).
2. Compiles a one-node LangGraph graph: `START → respond`. The single `respond`
   node invokes the model on the current messages and appends the reply.

> The constructor builds the client and graph eagerly, but makes **no network
> call** — the model is only contacted when `think()` runs.

### Methods

#### `think(text: str) -> str`

Process one piece of text and return the model's reply.

- **`text`** — the user message to respond to.
- **Returns** — `str`, the content of the model's reply (the last message in the
  graph's result).

Internally it invokes the graph with a single user message and returns
`result["messages"][-1].content`.

#### `stream(text: str) -> Iterator[str]`

Stream one reply as text chunks. This uses the same `ChatOpenAI` client directly
so callers that need progressive UI updates can start work before the complete
reply string is available.

## The graph

```
        ┌─────────┐
START ─►│ respond │─► END
        └─────────┘
   (ChatOpenAI.invoke on the message list)
```

The graph uses LangGraph's built-in `MessagesState`, so the message list is
accumulated automatically. Today it is a single node; this shape leaves room to
grow (memory, tools, routing) **without changing the public contract** — callers
keep using `think(text) -> str`.

## Examples

```python
from mind import Mind

# Default model
brain = Mind()
print(brain.think("Give me a one-line greeting."))

# A different OpenAI model
brain = Mind(model="gpt-4o")
print(brain.think("Explain Diátaxis in one sentence."))
```

## Why LangGraph for something this small?

A single API call would be shorter, but the project standardizes on LangGraph so
the "thinking" layer has a clear place to grow into — conversation memory, tool
use, multi-step reasoning — each added as graph nodes behind the same
`think(text) -> str` surface. See
[architecture.md](../../architecture.md#the-mind-module-thinking).
