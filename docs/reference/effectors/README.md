# `effectors` package

Source: [`effectors/`](../../../effectors/)

The `effectors` package groups C.H.R.I.S.'s action modules — one sub-package per
effector. It is the efferent counterpart to [`senses`](../senses/README.md):
where a sense turns the world into text, an effector turns text into an action
on the world. Each effector is self-contained and exposes a small, stable API.

## Modules

| Module | Effector | Contract | Reference |
| --- | --- | --- | --- |
| `effectors.effector_voice` | Speaking | `text -> audio file` | [effector_voice/](effector_voice/README.md) |

> Future effectors (e.g. movement, expressions) would live here as additional
> sub-packages, following the same "small public contract, hidden
> implementation" pattern.

## Importing

```python
from effectors.effector_voice import speak
```
